import json
import os
import re
from html.parser import HTMLParser
from http.client import HTTPException
from urllib.error import HTTPError
from urllib.parse import urlencode, urljoin, urlsplit
from urllib.request import Request, urlopen


API_ROOT = "https://de.openlegaldata.io/api/"
SOURCE = "Open Legal Data"


class IngestionError(ValueError):
    pass


class RateLimitError(IngestionError):
    pass


def get_json(path, params=None):
    url = urljoin(API_ROOT, path)
    if urlsplit(url)[:2] != urlsplit(API_ROOT)[:2]:
        raise IngestionError("unexpected API host")
    if params:
        url += "?" + urlencode(params)
    headers = {"Accept": "application/json", "User-Agent": "german-legal-agent-ingestion/1.0"}
    token = os.getenv("OLDP_API_TOKEN")
    if token:
        headers["Authorization"] = f"Token {token}"
    try:
        with urlopen(Request(url, headers=headers), timeout=30) as response:
            payload = json.load(response)
    except HTTPError as error:
        if error.code == 429:
            raise RateLimitError("HTTP 429 (API request quota exhausted)") from error
        raise IngestionError(f"HTTP {error.code}") from error
    except (OSError, HTTPException) as error:
        raise IngestionError(f"API connection failed ({error})") from error
    except ValueError as error:
        raise IngestionError("API returned invalid JSON") from error
    if not isinstance(payload, dict):
        raise IngestionError("unexpected API response object")
    return payload


def records(path, params, max_pages=None):
    visited = set()
    while path and (max_pages is None or len(visited) < max_pages):
        if path in visited:
            raise IngestionError("repeated pagination URL")
        visited.add(path)
        page = get_json(path, params)
        if not isinstance(page.get("results"), list):
            raise IngestionError("missing API results list")
        yield from page["results"]
        path = page.get("next")
        if path is not None and not isinstance(path, str):
            raise IngestionError("invalid API pagination URL")
        params = None


def require_id(record):
    if not isinstance(record, dict):
        raise IngestionError("unexpected record structure")
    record_id = record.get("id")
    if type(record_id) is not int or record_id <= 0:
        raise IngestionError("missing or invalid ID")
    return record_id


def require_string(record, field):
    value = record.get(field)
    if not isinstance(value, str) or not value.strip():
        raise IngestionError(f"missing {field}")
    return value.strip()


def detail(kind, record):
    record_id = require_id(record)
    if record.get("content"):
        return record
    try:
        payload = get_json(f"{kind}/{record_id}/")
        if require_id(payload) != record_id:
            raise IngestionError("detail ID mismatch")
    except IngestionError as error:
        raise type(error)(f"detail endpoint failed: {error}") from error
    return {**record, **payload}


def record_failure(failures, kind, record, error):
    record_id = record.get("id") if isinstance(record, dict) else record
    failures.append({"record_id": record_id, "record_type": kind, "reason": str(error)})


def section_key(value):
    match = re.fullmatch(r"\s*§?\s*(\d+)\s*([a-z]?)\s*", value, re.I)
    return (int(match[1]), match[2].lower()) if match else None


def law_scope(key):
    if key and (535, "") <= key <= (577, "a"):
        return "primary"
    if key and (578, "") <= key <= (580, "a"):
        return "optional"
    return None


class LegalTextParser(HTMLParser):
    blocks = {"br", "div", "p", "li", "tr", "section", "h1", "h2", "h3", "h4", "blockquote"}

    def __init__(self):
        super().__init__()
        self.parts = []

    def handle_starttag(self, tag, attrs):
        if tag in self.blocks:
            self.parts.append("\n")

    def handle_endtag(self, tag):
        if tag in self.blocks:
            self.parts.append("\n")
        elif tag in {"td", "th"}:
            self.parts.append(" ")

    def handle_data(self, data):
        self.parts.append(data)


def normalized_document(kind, record_id, title, content, source_url):
    parser = LegalTextParser()
    if isinstance(content, str):
        parser.feed(content)
        parser.close()
    lines = [" ".join(line.split()) for line in "".join(parser.parts).splitlines()]
    text = "\n".join(line for line in lines if line)
    if not text:
        raise IngestionError("missing full_text")
    return {
        "id": f"oldp:{kind}:{record_id}",
        "type": kind,
        "title": title,
        "text": text,
        "source": SOURCE,
        "source_url": source_url,
    }
