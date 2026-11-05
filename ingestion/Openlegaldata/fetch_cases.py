import argparse
import json
import re
from pathlib import Path
from tempfile import NamedTemporaryFile

from fetch_laws import collect_laws
from normalize import (
    API_ROOT, SOURCE, IngestionError, RateLimitError, detail, get_json, law_scope, normalized_document,
    record_failure, records, require_id, require_string, section_key,
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
HOUSING_QUERY = (
    "Wohnraummietrecht OR Wohnraummiete OR Wohnraummietvertrag OR Mietwohnung OR "
    "Mietminderung OR Eigenbedarf OR Mietkaution OR Betriebskostenabrechnung OR Schönheitsreparaturen"
)
BGB_CITATION = re.compile(
    r"§{1,2}\s*(\d+\s*[a-z]?)\b"
    r"(?:\s*(?:Abs(?:atz)?|Nr|Satz|S|Alt|Halbsatz|Hs|lit)\.?\s+[\da-z]+)*"
    r"\s*BGB\b",
    re.I,
)


def cited_sections(text):
    return {
        key for value in BGB_CITATION.findall(text)
        if law_scope(key := section_key(value)) == "primary"
    }


def search_candidates(failures):
    candidates = {}
    # The citation index can resolve references without an explicit BGB suffix.
    for section in (None, "556", "558", "573", "573a"):
        params = {"text": HOUSING_QUERY, "court": "BGH", "limit": 50, "return_text": 1}
        if section:
            params.update(cited_law_book="bgb", cited_law_section=section)
        try:
            for row in records("cases/search/", params, max_pages=1 if section else 2):
                try:
                    record_id = require_id(row)
                    if require_string(row, "court") != "BGH":
                        raise IngestionError("unexpected court in BGH search")
                    direct = cited_sections(require_string(row, "text"))
                    item = candidates.setdefault(record_id, {"row": row, "direct": set(), "indexed": set()})
                    item["direct"].update(direct)
                    if section:
                        item["indexed"].add(section_key(section))
                except IngestionError as error:
                    record_failure(failures, "case", row, error)
        except IngestionError as error:
            record_failure(failures, "case", f"search:{section or 'housing'}", error)
            if isinstance(error, RateLimitError):
                break
    return sorted(
        candidates.values(),
        key=lambda item: (
            bool(item["direct"]),
            len(item["direct"] | item["indexed"]),
            str(item["row"].get("date") or ""),
            item["row"]["id"],
        ),
        reverse=True,
    )


def collect_bgh_cases(failures):
    collected = {}
    for item in search_candidates(failures):
        if not (item["direct"] or item["indexed"]):
            continue
        row = item["row"]
        try:
            case = detail("cases", row)
            if not isinstance(case.get("court"), dict):
                raise IngestionError("missing or invalid court")
            metadata = normalize_case(case)
            if metadata["court"] != "Bundesgerichtshof":
                raise IngestionError("missing court or unexpected court")
            date = require_string(metadata, "date")
            file_number = require_string(metadata, "file_number")
            if (date, file_number) in collected:
                continue
            record_id = require_id(case)
            source_url = metadata["source_url"]
            if not isinstance(source_url, str) or not source_url.startswith(("http://", "https://")):
                source_url = f"{API_ROOT}cases/{record_id}/"
            document = normalized_document(
                "case", record_id, f"BGH, {date} – {file_number}", case.get("content"), source_url
            )
            citations = cited_sections(document["text"]) | item["indexed"]
            if not citations:
                continue
            for field in ("court", "date", "file_number", "ecli", "decision_type"):
                document[field] = metadata[field]
            document["cited_laws"] = [f"BGB § {num}{suffix}" for num, suffix in sorted(citations)]
            collected[date, file_number] = document
            if len(collected) == CASE_LIMIT:
                break
        except IngestionError as error:
            record_failure(failures, "case", row, error)
            if isinstance(error, RateLimitError):
                break
    if not collected:
        record_failure(failures, "case", "search", "no eligible BGH cases collected")
    return list(collected.values())


def load_previous(filename):
    path = RAW_OUTPUT_FILE.parent / filename
    if not path.exists():
        return []
    with path.open(encoding="utf-8") as file:
        documents = json.load(file)
    if not isinstance(documents, list) or not all(
        isinstance(item, dict) and isinstance(item.get("id"), str) and item.get("text")
        for item in documents
    ):
        raise IngestionError(f"invalid existing dataset: {filename}")
    return documents


def collect_mietrecht(resume=False):
    failures = []
    primary_file = "bgb_mietrecht_laws.json"
    optional_file = "bgb_mietrecht_optional_laws.json"
    cases_file = "bgh_mietrecht_cases.json"
    previous = load_previous(primary_file) + load_previous(optional_file) if resume else []
    previous_cases = load_previous(cases_file) if resume else []
    primary, optional = collect_laws(failures, previous)
    cases = collect_bgh_cases(failures)
    if resume and failures and (
        len(primary) + len(optional) < len(previous) or len(cases) < len(previous_cases)
    ):
        for failure in failures:
            print(failure)
        print("Partial run would discard previous records. Existing outputs were preserved.")
        return 1
    summary = {
        "primary_laws_collected": len(primary),
        "optional_laws_collected": len(optional),
        "bgh_cases_collected": len(cases),
        "parsing_failed": len(failures),
        "source": SOURCE,
    }
    for filename, data in (
        (primary_file, primary),
        (optional_file, optional),
        (cases_file, cases),
        ("parsing_failures.json", failures),
        ("ingestion_summary.json", summary),
    ):
        save_json(data, RAW_OUTPUT_FILE.parent / filename)
    print(f"Primary BGB laws collected: {len(primary)}")
    print(f"Optional BGB laws collected: {len(optional)}")
    print(f"BGH Mietrecht cases collected: {len(cases)}")
    print(f"Parsing failed: {len(failures)}")
    print(f"Source: {SOURCE}")
    return 1 if failures or not (primary and optional and cases) else 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--mietrecht", action="store_true", help="Collect the BGB and BGH datasets")
    parser.add_argument("--resume", action="store_true", help="Reuse previously collected BGB sections")
    args = parser.parse_args()
    if args.resume and not args.mietrecht:
        parser.error("--resume requires --mietrecht")
    if args.mietrecht:
        raise SystemExit(collect_mietrecht(args.resume))
    main()
