import json
import os
from pathlib import Path
import subprocess
import sys
from threading import Lock

import streamlit as st


ROOT = Path(__file__).resolve().parents[1]
SAMPLES = ROOT / "web" / "data" / "samples"
RAW = ROOT / "web" / "data" / "raw"
INGESTION = ROOT / "ingestion" / "Openlegaldata"
if str(INGESTION) not in sys.path:
    sys.path.insert(0, str(INGESTION))

from fetch_cases import CASE_COURTS, CASE_LIMIT, HOUSING_SEARCHES, MAX_CASE_LIMIT
from normalize import RATE_LIMIT_MESSAGE, section_key

DOMAINS = {
    "housing": {
        "label": "Housing / Mietrecht",
        "script": INGESTION / "fetch_cases.py",
        "flag": "--mietrecht",
        "topics": dict(HOUSING_SEARCHES),
        "courts": tuple(CASE_COURTS),
        "scopes": {"primary": "Primary · BGB §§535–577a", "optional": "Optional · BGB §§578–580a"},
        "sections": ("535", "580a"),
    },
}
DATASETS = {
    "Primary Laws": SAMPLES / "bgb_mietrecht_laws.json",
    "Optional Laws": SAMPLES / "bgb_mietrecht_optional_laws.json",
    "Final Cases": SAMPLES / "bgh_mietrecht_cases.json",
    "Raw Cases": RAW / "bgh_mietrecht_cases_raw.json",
    "Parsing Failures": SAMPLES / "parsing_failures.json",
}
LAST_RUN_METRICS = {
    "Existing Cases": "existing_cases",
    "New Cases Added": "new_cases_added",
    "Duplicate Cases Skipped": "duplicate_cases_skipped",
    "AI Summaries Generated": "ai_summaries_generated",
    "AI Summarization Failures": "summarization_failed",
    "Total Cases": "total_cases",
    "Parsing Failures": "parsing_failed",
}
LAW_FIELDS = ("id", "section", "title", "scope", "text", "source", "official_source_url")
CASE_FIELDS = ("id", "title", "court", "date", "topics", "cited_laws", "text", "text_type", "language", "source_url")
RAW_FIELDS = ("id", "title", "date", "court", "text")


@st.cache_resource
def ingestion_lock():
    return Lock()


def redact(value, token):
    if isinstance(value, str):
        for secret in (token, os.getenv("OPENAI_API_KEY")):
            if secret:
                for variant in {secret, ascii(secret)[1:-1], json.dumps(secret)[1:-1]}:
                    value = value.replace(variant, "[REDACTED]")
        return value
    if isinstance(value, list):
        return [redact(item, token) for item in value]
    if isinstance(value, dict):
        return {redact(key, token): redact(item, token) for key, item in value.items()}
    return value


def run_ingestion(domain, arguments, token):
    command = [sys.executable, "-B", str(domain["script"]), domain["flag"], *arguments]
    with ingestion_lock():
        try:
            result = subprocess.run(
                command,
                cwd=ROOT,
                env={**os.environ, "PYTHONIOENCODING": "utf-8"},
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                encoding="utf-8",
                errors="replace",
                check=False,
            )
        except OSError as error:
            return None, redact(str(error), token)
    return result.returncode, redact(result.stdout, token)


def read_sample(filename, expected_type, token):
    path = Path(filename)
    if not path.is_absolute():
        path = SAMPLES / path
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return None
    except (OSError, ValueError):
        st.warning(f"Could not read {path.name}.")
        return None
    if not isinstance(data, expected_type) or (
        isinstance(data, list) and any(not isinstance(row, dict) for row in data)
    ):
        st.warning(f"Unexpected JSON structure in {path.name}.")
        return None
    return redact(data, token)


def load_datasets(token):
    return {label: read_sample(path, list, token) for label, path in DATASETS.items()}


def dataset_counts(datasets):
    return {label: len(rows) if rows is not None else None for label, rows in datasets.items()}


def show_metrics(values, columns):
    for start in range(0, len(values), columns):
        for column, (label, value) in zip(st.columns(columns), list(values.items())[start:start + columns]):
            column.metric(label, value if value is not None else "Not available", border=True)


def matches(row, query, fields):
    return not query or any(query in str(row.get(field, "")).casefold() for field in fields)


def show_table(rows, fields, key):
    if not rows:
        st.info("No matching records.")
        return
    preview = []
    for row in rows:
        item = {field: row.get(field) for field in fields}
        body = str(item["text"] or "")
        item["text"] = body[:350] + ("…" if len(body) > 350 else "")
        preview.append(item)
    st.dataframe(preview, hide_index=True)
    selected = st.selectbox(
        "Select a record", range(len(rows)), index=None, key=key,
        format_func=lambda index: f"{rows[index].get('id', index + 1)} · {rows[index].get('title', '')}",
    )
    if selected is not None:
        with st.expander("Full text", expanded=False):
            st.text(rows[selected].get("text") or "")


def show_laws(primary, optional):
    section = st.text_input("Section search").strip().casefold()
    query = st.text_input("Law keyword").strip().casefold()
    scope = st.selectbox("Scope filter", ("All", "primary", "optional"))
    if primary is not None or optional is not None:
        rows = (primary or []) + (optional or [])
        filtered = [
            row for row in rows
            if matches(row, section, ("section",)) and matches(row, query, ("title", "text"))
            and (scope == "All" or row.get("scope") == scope)
        ]
        show_table(filtered, LAW_FIELDS, "law_detail")
    else:
        st.info("No law datasets available.")


def show_cases(rows, topics):
    query = st.text_input("Case keyword").strip().casefold()
    topic = st.selectbox("Topic filter", (None, *topics), format_func=lambda value: value or "All")
    section = st.text_input("Cited BGB section", placeholder="e.g. 536a").strip().casefold()
    section = section.removeprefix("bgb").strip().removeprefix("§").strip()
    date = st.text_input("Decision date", placeholder="YYYY-MM-DD").strip()
    record_id = st.text_input("Open Legal Data ID").strip().casefold()
    if rows is not None:
        filtered = [
            row for row in rows
            if matches(row, query, ("title", "text", "court"))
            and (topic is None or (
                topic in (row["topics"] or []) if "topics" in row
                else matches(row, topic.casefold(), ("title", "text"))
            ))
            and (not section or f"bgb § {section}" in {
                str(citation).casefold() for citation in (row.get("cited_laws") or [])
            })
            and (not date or row.get("date") == date)
            and matches(row, record_id, ("id",))
        ]
        show_table(filtered, CASE_FIELDS, "case_detail")
    else:
        st.info("No final case dataset available.")


def collection_settings(domain):
    st.subheader("Collection Type")
    laws = st.checkbox("Enable Law Collection", value=True)
    cases = st.checkbox("Enable Case Collection", value=True)
    scopes, start, end, law_limit = [], "", "", None
    topics, court, case_limit = [], None, CASE_LIMIT
    if laws:
        with st.container(border=True):
            st.subheader("Law Collection")
            scopes = [key for key, label in domain["scopes"].items() if st.checkbox(label, value=True)]
            start = st.text_input("Section From", domain["sections"][0]).strip()
            end = st.text_input("Section To", domain["sections"][1]).strip()
            law_limit = st.number_input("Law Limit", min_value=1, value=None, step=1, placeholder="All")
    if cases:
        with st.container(border=True):
            st.subheader("Case Collection")
            court = st.selectbox("Court", domain["courts"])
            topic_options = domain["topics"]
            topics = st.multiselect(
                "Topics", topic_options, default=list(topic_options),
                format_func=lambda term: (
                    f"{term} — BGB §{topic_options[term]}" if topic_options[term] else term
                ),
            )
            case_limit = st.number_input("New Cases to Add", 1, MAX_CASE_LIMIT, CASE_LIMIT)
            st.caption("Existing IDs are skipped. Legacy full texts are summarized once during migration.")
    st.subheader("Run Options")
    resume = st.checkbox("Resume existing dataset", value=True)
    debug = st.checkbox("Debug mode")
    run = st.button("Run Data Collection", type="primary")
    if not run:
        return None
    if not (laws or cases):
        st.error("Please enable at least one collection type.")
        return None
    if laws:
        if not scopes:
            st.error("Please select at least one law scope.")
            return None
        start_key, end_key = section_key(start), section_key(end)
        if start_key is None or end_key is None or start_key > end_key:
            st.error("Enter a valid section range, such as 535 to 580a.")
            return None
    if cases and not topics:
        st.error("Please select at least one case topic.")
        return None

    arguments = []
    if not laws:
        arguments.append("--cases-only")
    if not cases:
        arguments.append("--laws-only")
    if laws:
        if (start, end) != domain["sections"]:
            arguments.extend((f"--section-from={start}", f"--section-to={end}"))
        arguments.extend(f"--law-scope={scope}" for scope in scopes)
        if law_limit is not None:
            arguments.append(f"--law-limit={law_limit}")
    if cases:
        arguments.extend((f"--court={court}", f"--case-limit={case_limit}"))
        arguments.extend(f"--topic={topic}" for topic in topics)
    if resume:
        arguments.append("--resume")
    if debug:
        arguments.append("--debug")
    settings = {
        "Selected Domain": domain["label"],
        "Selected Topics": ", ".join(topics) if cases else "Case collection disabled",
        "Requested Case Limit": case_limit if cases else "—",
        "Requested Law Limit": (law_limit or "All") if laws else "—",
    }
    return arguments, settings


def main():
    st.set_page_config(page_title="Data Collection Dashboard", layout="wide")
    st.title("German Legal Agent — Data Collection Dashboard")
    token = os.getenv("OLDP_API_TOKEN")
    st.write("Data Source · Open Legal Data")
    oldp, ai, model = st.columns(3)
    oldp.metric("Open Legal Data API", "Available" if token else "Not configured")
    configured = bool(os.getenv("OPENAI_API_KEY") and os.getenv("OLDP_SUMMARY_MODEL"))
    ai.metric("AI Summarization", "Available" if configured else "Not configured")
    model.metric("AI Model", redact(os.getenv("OLDP_SUMMARY_MODEL") or "Not configured", token))

    controls, current = st.columns([3, 2], gap="large")
    with controls:
        key = st.selectbox("Domain", list(DOMAINS), format_func=lambda key: DOMAINS[key]["label"])
        domain = DOMAINS[key]
        st.caption("Coming soon · Visa, Labor, Human Rights")
        selection = collection_settings(domain)
        if selection is not None:
            arguments, settings = selection
            before = dataset_counts(load_datasets(token))
            with st.spinner("Running ingestion..."):
                code, output = run_ingestion(domain, arguments, token)
            st.session_state.collection_result = {
                "code": code, "output": output, "settings": settings, "before": before,
            }

    # Read after execution on every rerun. Preview and counts share the same snapshot.
    datasets = load_datasets(token)
    counts = dataset_counts(datasets)
    summary = read_sample("ingestion_summary.json", dict, token)
    with current:
        st.subheader("Current Dataset Status")
        st.caption("Record counts calculated from the JSON files currently saved on disk.")
        show_metrics(counts, 2)

    result = st.session_state.get("collection_result")
    if result is not None:
        code, output = result["code"], result["output"]
        if code == 0:
            st.success("Completed")
        elif code is None:
            st.error("Failed to start data collection.")
        else:
            st.error(f"Failed (exit code {code})")
            if RATE_LIMIT_MESSAGE in output:
                st.warning("Open Legal Data request quota exhausted (HTTP 429). Retry after the quota resets.")
                if not token:
                    st.info("Set OLDP_API_TOKEN in the shell that starts Streamlit, then restart the app.")
        st.caption(redact(" · ".join(f"{label}: {value}" for label, value in result["settings"].items()), token))
        before_cases = result["before"]["Final Cases"]
        after_cases = counts["Final Cases"]
        st.write(
            f"Final Cases · Before run {before_cases if before_cases is not None else 'Not available'}"
            f" → Now {after_cases if after_cases is not None else 'Not available'}"
        )

    st.subheader("Last Run Statistics")
    st.caption("Most recent saved execution report. These values come from ingestion_summary.json.")
    if summary is None:
        st.info("No execution summary available.")
    else:
        show_metrics({label: summary.get(field) for label, field in LAST_RUN_METRICS.items()}, 4)

    st.subheader("Data Preview")
    laws, cases, raw, failures, summary_tab = st.tabs(["Laws", "Cases", "Raw Cases", "Failures", "Summary"])
    with laws:
        show_laws(datasets["Primary Laws"], datasets["Optional Laws"])
    with cases:
        show_cases(datasets["Final Cases"], domain["topics"])
    with raw:
        st.caption("Archived full texts used for verification and future summarization.")
        rows = datasets["Raw Cases"]
        if rows is None:
            st.info("No raw case archive available.")
        else:
            show_table(rows, RAW_FIELDS, "raw_detail")
    with failures:
        records = datasets["Parsing Failures"]
        if records:
            st.json(records)
        elif records == []:
            st.info("No parsing failures")
        else:
            st.info("No parsing failure file available.")
    with summary_tab:
        if summary is not None:
            st.json(summary)

    with st.expander("Execution Log", expanded=result is not None and result["code"] != 0):
        if result is not None:
            st.code(redact(result["output"], token) or "(No output)", language="text")
        else:
            st.caption("Run data collection to see stdout and stderr here.")


main()
