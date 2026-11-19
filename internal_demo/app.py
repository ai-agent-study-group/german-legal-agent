import json
import os
from pathlib import Path
import subprocess
import sys
from threading import Lock

import streamlit as st


ROOT = Path(__file__).resolve().parents[1]
SAMPLES = ROOT / "web" / "data" / "samples"
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
METRICS = {
    "Primary BGB Laws": "primary_laws_collected",
    "Optional BGB Laws": "optional_laws_collected",
    "BGH Cases": "bgh_cases_collected",
    "Parsing Failures": "parsing_failed",
}
LAW_FIELDS = ("section", "title", "text", "scope", "source", "official_source_url")
CASE_FIELDS = ("id", "title", "court", "date", "topics", "cited_laws", "text", "text_type", "language", "source_url")


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
    try:
        data = json.loads((SAMPLES / filename).read_text(encoding="utf-8"))
    except FileNotFoundError:
        st.info(f"No saved output for {filename}.")
        return None
    except (OSError, ValueError):
        st.warning(f"Could not read {filename}.")
        return None
    if not isinstance(data, expected_type) or (
        isinstance(data, list) and any(not isinstance(row, dict) for row in data)
    ):
        st.warning(f"Unexpected JSON structure in {filename}.")
        return None
    return redact(data, token)


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
        "Read full text", range(len(rows)), index=None, key=key,
        format_func=lambda index: rows[index].get("title") or f"Record {index + 1}",
    )
    if selected is not None:
        st.text(rows[selected].get("text") or "")


def show_laws(token):
    primary = read_sample("bgb_mietrecht_laws.json", list, token)
    optional = read_sample("bgb_mietrecht_optional_laws.json", list, token)
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


def show_cases(token, topics):
    rows = read_sample("bgh_mietrecht_cases.json", list, token)
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
                topic in row["topics"] if "topics" in row
                else matches(row, topic.casefold(), ("title", "text"))
            ))
            and (not section or f"bgb § {section}" in {
                str(citation).casefold() for citation in (row.get("cited_laws") or [])
            })
            and (not date or row.get("date") == date)
            and matches(row, record_id, ("id",))
        ]
        show_table(filtered, CASE_FIELDS, "case_detail")


def collection_settings(domain):
    with st.form("ingestion_settings"):
        law_column, case_column = st.columns(2)
        with law_column:
            st.subheader("Law Collection")
            laws = st.checkbox("Enable Law Collection", value=True)
            scopes = [key for key, label in domain["scopes"].items() if st.checkbox(label, value=True)]
            start = st.text_input("Section From", domain["sections"][0]).strip()
            end = st.text_input("Section To", domain["sections"][1]).strip()
            law_limit = st.number_input("Law Limit", min_value=1, value=None, step=1, placeholder="All")
        with case_column:
            st.subheader("Case Collection")
            cases = st.checkbox("Enable Case Collection", value=True)
            court = st.selectbox("Court", domain["courts"])
            topic_options = domain["topics"]
            topics = st.multiselect(
                "Topics", topic_options, default=list(topic_options),
                format_func=lambda term: (
                    f"{term} — BGB §{topic_options[term]}" if topic_options[term] else term
                ),
            )
            case_limit = st.number_input("New BGH Cases per Run", 1, MAX_CASE_LIMIT, CASE_LIMIT)
            st.caption("Existing IDs are skipped. Legacy full texts are summarized once during migration.")
        st.subheader("Run Options")
        resume = st.checkbox("Resume existing dataset", value=True)
        debug = st.checkbox("Debug mode")
        run = st.form_submit_button("Run Data Ingestion", type="primary")
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
    st.set_page_config(page_title="Data Collection Demo", layout="wide")
    st.title("German Legal Agent — Data Collection Demo")
    token = os.getenv("OLDP_API_TOKEN")
    st.subheader("Data Source")
    st.write("Open Legal Data")
    st.caption("API Authentication: Available" if token else "API Authentication: Not configured")
    configured = bool(os.getenv("OPENAI_API_KEY") and os.getenv("OLDP_SUMMARY_MODEL"))
    st.caption("AI Summarization: Available" if configured else
               "AI Summarization: Configure OPENAI_API_KEY and OLDP_SUMMARY_MODEL")

    key = st.selectbox("Domain", list(DOMAINS), format_func=lambda key: DOMAINS[key]["label"])
    domain = DOMAINS[key]
    st.caption("Coming soon · Visa, Labor, Human Rights")
    selection = collection_settings(domain)
    if selection is not None:
        arguments, settings = selection
        with st.spinner("Running ingestion..."):
            code, output = run_ingestion(domain, arguments, token)
        st.session_state.ingestion_result = code, output, settings

    st.subheader("Ingestion Summary")
    result = st.session_state.get("ingestion_result")
    if result is not None:
        code, output, settings = result
        if code == 0:
            st.success("Completed")
        elif code is None:
            st.error("Failed to start ingestion.")
        else:
            st.error(f"Failed (exit code {code})")
            if RATE_LIMIT_MESSAGE in output:
                st.warning("Open Legal Data request quota exhausted (HTTP 429). Retry after the quota resets.")
                if not token:
                    st.info("Set OLDP_API_TOKEN in the shell that starts Streamlit, then restart the app.")
        st.caption(" · ".join(f"{label}: {value}" for label, value in settings.items()))

    st.caption("Counts reflect the datasets currently saved on disk.")
    summary = read_sample("ingestion_summary.json", dict, token)
    if summary is not None:
        for column, (label, key) in zip(st.columns(len(METRICS)), METRICS.items()):
            column.metric(label, summary.get(key, "—"), border=True)
        st.caption(f"Source: {summary.get('source', 'Open Legal Data')}")
        incremental = {
            label: summary.get(field, 0) for label, field in (
                ("Existing cases", "existing_cases"),
                ("Duplicate cases skipped", "duplicate_cases_skipped"),
                ("New cases added", "new_cases_added"),
                ("AI summaries generated", "ai_summaries_generated"),
                ("AI summarization failures", "summarization_failed"),
                ("Total cases", "total_cases"),
            )
        }
        if "existing_cases" in summary:
            st.write(incremental)

    st.subheader("Data Preview")
    laws, cases, failures, raw = st.tabs(["Laws", "Cases", "Failures", "Summary"])
    with laws:
        show_laws(token)
    with cases:
        show_cases(token, domain["topics"])
    with failures:
        records = read_sample("parsing_failures.json", list, token)
        if records:
            st.json(records)
        elif records == []:
            st.info("No parsing failures")
    with raw:
        if summary is not None:
            st.json(summary)

    with st.expander("Execution Log", expanded=result is not None and result[0] != 0):
        if result is not None:
            st.code(redact(output, token) or "(No output)", language="text")
        else:
            st.caption("Run data ingestion to see stdout and stderr here.")


main()
