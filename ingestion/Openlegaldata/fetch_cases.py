import json
from pathlib import Path

import requests


API_URL = "https://de.openlegaldata.io/api/cases/"

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
    params = {
        "offset": 0,
    }

    headers = {
        "Accept": "application/json",
    }

    response = requests.get(
        API_URL,
        params=params,
        headers=headers,
        timeout=30,
    )

    print("Request URL:", response.url)
    print("Status code:", response.status_code)

    response.raise_for_status()

    return response.json()


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
        "source": "Open Legal Data",
        "source_url": case.get("source_url"),
    }


def save_json(data, output_file):
    output_file.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with output_file.open(
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            data,
            file,
            ensure_ascii=False,
            indent=2,
        )


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


if __name__ == "__main__":
    main()