import argparse
import json
import os
import re
from html import unescape
from contextlib import contextmanager
from pathlib import Path
from tempfile import NamedTemporaryFile

from fetch_laws import collect_laws
from summarize import SummaryServiceError, summarize_case
from normalize import (
    API_ROOT, SOURCE, IngestionError, RateLimitError, detail, get_json, law_scope, normalized_document,
    quota_exhausted, record_failure, records, require_id, require_string, section_key,
)

BASE_DIR = Path(__file__).resolve().parents[2]

RAW_OUTPUT_FILE = (
    BASE_DIR
    / "web"
    / "data"
    / "samples"
    / "openlegaldata_raw.json"
)

NORMALIZED_OUTPUT_FILE = (
    BASE_DIR
    / "web"
    / "data"
    / "samples"
    / "openlegaldata_cases.json"
)


def fetch_cases():
    return get_json("cases/", {"offset": 0})


def normalize_case(case):
    court = case.get("court") or {}

    return {
        "id": case.get("id"),
        "slug": case.get("slug"),
        "court": court.get("name"),
        "court_city": court.get("city"),
        "court_state": court.get("state"),
        "jurisdiction": court.get("jurisdiction"),
        "court_level": court.get("level_of_appeal"),
        "file_number": case.get("file_number"),
        "date": case.get("date"),
        "decision_type": case.get("type"),
        "ecli": case.get("ecli"),
        "source": SOURCE,
        "source_url": case.get("source_url"),
    }


def save_json(data, output_file):
    output_file.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with NamedTemporaryFile(
        mode="w", encoding="utf-8", dir=output_file.parent, delete=False
    ) as file:
        temporary = Path(file.name)
        try:
            json.dump(data, file, ensure_ascii=False, indent=2)
            file.write("\n")
            file.close()
            temporary.replace(output_file)
        finally:
            file.close()
            temporary.unlink(missing_ok=True)


def main():
    print("Fetching cases from Open Legal Data...")

    raw_data = fetch_cases()

    cases = raw_data.get("results", [])

    print("Total available cases:", raw_data.get("count"))
    print("Cases received:", len(cases))

    save_json(
        raw_data,
        RAW_OUTPUT_FILE,
    )

    normalized_cases = [
        normalize_case(case)
        for case in cases
    ]

    save_json(
        normalized_cases,
        NORMALIZED_OUTPUT_FILE,
    )

    print("Raw data saved to:")
    print(RAW_OUTPUT_FILE)

    print("Normalized data saved to:")
    print(NORMALIZED_OUTPUT_FILE)


CASE_LIMIT = 50
MAX_CASE_LIMIT = 500
CASE_COURTS = {"BGH": "Bundesgerichtshof"}
HOUSING_SEARCHES = (
    ("Eigenbedarf", "573"),
    ("Mietminderung", "536"),
    ("Mietkaution", "551"),
    ("Betriebskostenabrechnung", "556"),
    ("Mieterhöhung", "558"),
    ("Schönheitsreparaturen", None),
    ("Wohnraummietvertrag", None),
)
SECTION_NUMBER = r"\d+(?:\s*[a-z])?\b"
SUBSECTION = r"(?:\s*(?:Abs(?:atz)?|Nr|Satz|S|Alt|Halbsatz|Hs|lit)\.?\s*[\da-z]+\b)*"
CITATION_SEPARATOR = r"\s*(?:,|und|oder|bis)\s*§{0,2}\s*"
BGB_CITATION = re.compile(
    rf"§{{1,2}}\s*({SECTION_NUMBER}{SUBSECTION}"
    rf"(?:{CITATION_SEPARATOR}{SECTION_NUMBER}{SUBSECTION})*)\s*BGB\b",
    re.I,
)


def cited_sections(text):
    return {
        key
        for citation in BGB_CITATION.findall(unescape(text))
        for part in re.split(CITATION_SEPARATOR, citation, flags=re.I)
        if law_scope(key := section_key(re.match(SECTION_NUMBER, part, re.I)[0])) == "primary"
    }


def debug_response(label, row):
    print(f"{label}: id={row.get('id')!r}, court={row.get('court')!r}, fields={sorted(row)}")
    for field in ("text", "content"):
        if isinstance(value := row.get(field), str):
            if token := os.getenv("OLDP_API_TOKEN"):
                value = value.replace(token, "[REDACTED]")
            print(f"  {field} ({len(value)} chars): {value[:100]!a}")


def search_candidates(failures, debug=False, *, limit=CASE_LIMIT, court="BGH", topics=None):
    selected = [(term, section) for term, section in HOUSING_SEARCHES if topics is None or term in topics]
    # Search citation-indexed streams first, then recover explicit citations from text.
    searches = [(term, section) for term, section in selected if section]
    searches.extend((term, None) for term, _ in selected)
    for term, section in searches:
        params = {"text": term, "court": court, "limit": 25, "return_text": 1}
        if section:
            params.update(cited_law_book="bgb", cited_law_section=section)
        try:
            for row in records("cases/search/", params):
                try:
                    require_id(row)
                    if require_string(row, "court") != court:
                        raise IngestionError("unexpected court in case search")
                    direct = cited_sections(row["text"]) if isinstance(row.get("text"), str) else set()
                    yield {"row": row, "direct": direct,
                           "indexed": {section_key(section)} if section else set(), "topics": {term}}
                except IngestionError as error:
                    record_failure(failures, "case", row, error)
        except IngestionError as error:
            record_failure(failures, "case", f"search:{term}", error)
            return


def summary_document(document, stats, failures):
    clean = {key: value for key, value in document.items()
             if key not in {"ecli", "file_number", "_legacy_record"}}
    if clean.get("text_type") == "ai_summary" and clean.get("language") == "de":
        return clean
    try:
        clean["text"] = summarize_case(document)
    except IngestionError as error:
        stats["summarization_failed"] += 1
        record_failure(failures, "case_summary", document, error)
        if isinstance(error, SummaryServiceError):
            stats["_ai_unavailable"] = True
        return None
    clean.update(text_type="ai_summary", language="de")
    stats["ai_summaries_generated"] += 1
    return clean


def is_summary(document):
    return document.get("text_type") == "ai_summary" and document.get("language") == "de"


def collect_bgh_cases(failures, limit=CASE_LIMIT, debug=False, *, court="BGH", topics=None,
                      previous=(), archive=None, stats=None, checkpoint=None):
    archive = archive if archive is not None else {}
    stats = stats if stats is not None else {}
    previous = list({row["id"]: row for row in previous}.values())
    stats.update(existing_cases=len(previous), new_cases_added=0, duplicate_cases_skipped=0,
                 summarization_failed=0, ai_summaries_generated=0)
    collected = {
        row["id"]: {key: value for key, value in row.items() if key not in {"ecli", "file_number"}}
        for row in previous if is_summary(row)
    }
    existing_ids = {document["id"] for document in previous}
    # Archive legacy originals before migration. Failed summaries remain retryable in raw.
    for document in previous:
        if not is_summary(document):
            archive.setdefault(document["id"], {**document, "_legacy_record": True})
    if checkpoint:
        checkpoint(list(collected.values()), archive, raw_only=True)
    for document in previous:
        summary = summary_document(document, stats, failures)
        if summary:
            collected[summary["id"]] = summary
            if checkpoint:
                checkpoint(list(collected.values()), archive)
        if stats.get("_ai_unavailable"):
            break
    collected = {
        row["id"]: collected[row["id"]] for row in previous if row["id"] in collected
    }
    # Recover failed new summaries directly from raw without another detail request.
    pending = [
        row for key, row in archive.items() if key not in existing_ids
        and row.get("court") == CASE_COURTS[court]
        and (row.get("_legacy_record") or topics is None
             or set(row.get("topics", [])) & set(topics)
             or any(term.casefold() in row["text"].casefold() for term in topics))
    ]
    seen = set(existing_ids)
    duplicates = set()
    def candidates():
        if stats.get("_ai_unavailable"):
            return
        for document in pending:
            yield {"raw": document, "row": {"id": int(document["id"].rsplit(":", 1)[1])}}
        yield from search_candidates(failures, debug, limit=limit, court=court, topics=topics)

    for item in candidates():
        row = item["row"]
        case_id = f"oldp:case:{require_id(row)}"
        if case_id in seen:
            if case_id not in duplicates:
                stats["duplicate_cases_skipped"] += 1
                duplicates.add(case_id)
            continue
        try:
            document = item.get("raw")
            if document is None:
                if not (item["direct"] or item["indexed"]) and row.get("text"):
                    continue
                case = detail("cases", row)
                if debug:
                    debug_response("Case detail", case)
                if require_id(case) != require_id(row):
                    raise IngestionError("detail ID mismatch")
                if not isinstance(case.get("court"), dict):
                    raise IngestionError("missing or invalid court")
                metadata = normalize_case(case)
                if metadata["court"] != CASE_COURTS[court]:
                    raise IngestionError("missing court or unexpected court")
                date = require_string(metadata, "date")
                source_url = metadata["source_url"]
                if not isinstance(source_url, str) or not source_url.startswith(("http://", "https://")):
                    source_url = f"{API_ROOT}cases/{require_id(case)}/"
                document = normalized_document(
                    "case", require_id(case), f"{court}, {date}", case.get("content"), source_url
                )
                citations = cited_sections(document["text"]) | item["indexed"]
                if not citations:
                    continue
                for field in ("court", "date", "decision_type"):
                    document[field] = metadata[field]
                document["cited_laws"] = [f"BGB § {num}{suffix}" for num, suffix in sorted(citations)]
                document["topics"] = sorted(item["topics"])
            seen.add(case_id)
            archive[case_id] = document
            if checkpoint:
                checkpoint(list(collected.values()), archive, raw_only=True)
            summary = summary_document(document, stats, failures)
            if summary:
                collected[case_id] = summary
                if not document.get("_legacy_record"):
                    stats["new_cases_added"] += 1
                if checkpoint:
                    checkpoint(list(collected.values()), archive)
                if stats["new_cases_added"] >= limit:
                    break
            if stats.get("_ai_unavailable"):
                break
        except IngestionError as error:
            record_failure(failures, "case", row, error)
            break
    stats["total_cases"] = len(collected)
    stats.pop("_ai_unavailable", None)
    return list(collected.values())


def load_previous(filename):
    path = RAW_OUTPUT_FILE.parent / filename
    if not path.exists():
        return []
    try:
        with path.open(encoding="utf-8") as file:
            documents = json.load(file)
    except (OSError, ValueError):
        raise IngestionError(f"cannot read existing dataset: {path.name}") from None
    if not isinstance(documents, list) or not all(
        isinstance(item, dict) and isinstance(item.get("id"), str)
        and isinstance(item.get("text"), str) and item["text"].strip()
        for item in documents
    ):
        raise IngestionError(f"invalid existing dataset: {filename}")
    return documents


LAW_FILES = {
    "primary": "bgb_mietrecht_laws.json",
    "optional": "bgb_mietrecht_optional_laws.json",
}
CASES_FILE = "bgh_mietrecht_cases.json"
CASE_ARCHIVE = BASE_DIR / "web" / "data" / "raw" / "bgh_mietrecht_cases_raw.json"


@contextmanager
def ingestion_file_lock():
    """Serialize read/merge/write across terminal and Streamlit processes."""
    path = RAW_OUTPUT_FILE.parent / ".ingestion.lock"
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a+b") as file:
        if file.tell() == 0:
            file.write(b"0")
            file.flush()
        file.seek(0)
        try:
            if os.name == "nt":
                import msvcrt
                msvcrt.locking(file.fileno(), msvcrt.LK_NBLCK, 1)
            else:
                import fcntl
                fcntl.flock(file, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError:
            raise IngestionError("Another ingestion is running for this output directory") from None
        try:
            yield
        finally:
            if os.name == "nt":
                file.seek(0)
                msvcrt.locking(file.fileno(), msvcrt.LK_UNLCK, 1)
            else:
                fcntl.flock(file, fcntl.LOCK_UN)


def collect_mietrecht(*args, **kwargs):
    try:
        with ingestion_file_lock():
            return _collect_mietrecht(*args, **kwargs)
    except (IngestionError, OSError) as error:
        print(f"Ingestion failed: {error}")
        return 1


def _collect_mietrecht(resume=False, case_limit=CASE_LIMIT, debug=False, *,
                      laws=True, cases=True, scopes=("primary", "optional"),
                      section_from=None, section_to=None, law_limit=None,
                      court="BGH", topics=None):
    failures = []
    filenames = (*LAW_FILES.values(), CASES_FILE)
    previous = {name: load_previous(name) for name in filenames}
    ai_configured = bool(os.getenv("OPENAI_API_KEY") and os.getenv("OLDP_SUMMARY_MODEL"))
    if cases:
        for row in previous[CASES_FILE]:
            if not re.fullmatch(r"oldp:case:[1-9]\d*", row["id"]):
                raise IngestionError("invalid existing Open Legal Data case ID")
        if not ai_configured:
            record_failure(failures, "case_summary", "configuration",
                           "AI summary requires OPENAI_API_KEY and OLDP_SUMMARY_MODEL")
    updates = {}
    if laws:
        cached = [row for scope in scopes for row in previous[LAW_FILES[scope]]] if resume else []
        primary, optional = collect_laws(
            failures, cached, scopes=scopes, section_from=section_from,
            section_to=section_to, limit=law_limit,
        )
        if not failures and law_limit is None and section_from is None and section_to is None:
            for scope, rows in zip(LAW_FILES, (primary, optional)):
                if scope in scopes and not rows:
                    record_failure(failures, "law", scope, "no laws collected for selected scope")
        for scope, rows in zip(LAW_FILES, (primary, optional)):
            if scope in scopes:
                updates[LAW_FILES[scope]] = rows
    stats = {}
    if cases:
        stats = dict(existing_cases=len(previous[CASES_FILE]), new_cases_added=0,
                     duplicate_cases_skipped=0, ai_summaries_generated=0,
                     summarization_failed=int(not ai_configured), total_cases=len(previous[CASES_FILE]))
    if cases and ai_configured and not quota_exhausted(failures):
        archive = {row["id"]: row for row in load_previous(CASE_ARCHIVE)}
        if any(not re.fullmatch(r"oldp:case:[1-9]\d*", key) for key in archive):
            raise IngestionError("invalid archived Open Legal Data case ID")

        def checkpoint(documents, archive, raw_only=False):
            save_json(list(archive.values()), CASE_ARCHIVE)
            if not raw_only:
                save_json(documents, RAW_OUTPUT_FILE.parent / CASES_FILE)

        updates[CASES_FILE] = collect_bgh_cases(
            failures, case_limit, debug, court=court, topics=topics,
            previous=previous[CASES_FILE], archive=archive, stats=stats, checkpoint=checkpoint,
        )
    if failures:
        for failure in failures:
            print(failure)
        for name in tuple(updates):
            if name != CASES_FILE and previous[name]:
                del updates[name]
    saved = {**previous, **updates}
    summary = {
        "primary_laws_collected": len(saved[LAW_FILES["primary"]]),
        "optional_laws_collected": len(saved[LAW_FILES["optional"]]),
        "bgh_cases_collected": len(saved[CASES_FILE]),
        "parsing_failed": len(failures),
        "source": SOURCE,
        **stats,
    }
    for label, key in (
        ("Existing cases", "existing_cases"),
        ("Duplicate cases skipped", "duplicate_cases_skipped"),
        ("New cases added", "new_cases_added"),
        ("AI summaries generated", "ai_summaries_generated"),
        ("AI summarization failures", "summarization_failed"),
        ("Total cases", "total_cases"),
    ):
        if key in stats:
            print(f"{label}: {stats[key]}")
    for filename, data in (
        *updates.items(),
        ("parsing_failures.json", failures),
        ("ingestion_summary.json", summary),
    ):
        save_json(data, RAW_OUTPUT_FILE.parent / filename)
    for name, rows in updates.items():
        print(f"{name}: {len(rows)} records saved")
    print(f"Parsing failed: {len(failures)}")
    print(f"Source: {SOURCE}")
    return int(bool(failures))


def positive_int(value):
    number = int(value)
    if number < 1:
        raise argparse.ArgumentTypeError("must be a positive integer")
    return number


def section_argument(value):
    key = section_key(value)
    if key is None:
        raise argparse.ArgumentTypeError("expected a BGB section such as 535 or 580a")
    return key


def cli():
    parser = argparse.ArgumentParser()
    parser.add_argument("--mietrecht", action="store_true", help="Collect the BGB and BGH datasets")
    parser.add_argument("--resume", action="store_true", help="Reuse previously collected BGB sections")
    parser.add_argument("--case-limit", type=positive_int, metavar="N",
                        help=f"Add at most N NEW unique decisions (1–{MAX_CASE_LIMIT}, default {CASE_LIMIT})")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--laws-only", action="store_true")
    mode.add_argument("--cases-only", action="store_true")
    parser.add_argument("--law-scope", choices=tuple(LAW_FILES), action="append")
    parser.add_argument("--section-from", type=section_argument)
    parser.add_argument("--section-to", type=section_argument)
    parser.add_argument("--law-limit", type=positive_int)
    parser.add_argument("--court", choices=tuple(CASE_COURTS))
    parser.add_argument("--topic", choices=[term for term, _ in HOUSING_SEARCHES], action="append")
    parser.add_argument("--debug", action="store_true", help="Show BGH search and detail response samples")
    args = parser.parse_args()
    if not args.mietrecht and any(vars(args).values()):
        parser.error("collection options require --mietrecht")
    if args.case_limit is not None and args.case_limit > MAX_CASE_LIMIT:
        parser.error(f"--case-limit must be between 1 and {MAX_CASE_LIMIT}")
    if args.section_from and args.section_to and args.section_from > args.section_to:
        parser.error("--section-from must not be after --section-to")
    if args.mietrecht:
        raise SystemExit(collect_mietrecht(
            args.resume, args.case_limit or CASE_LIMIT, args.debug,
            laws=not args.cases_only, cases=not args.laws_only,
            scopes=args.law_scope or tuple(LAW_FILES),
            section_from=args.section_from, section_to=args.section_to, law_limit=args.law_limit,
            court=args.court or "BGH", topics=args.topic,
        ))
    main()


if __name__ == "__main__":
    cli()
