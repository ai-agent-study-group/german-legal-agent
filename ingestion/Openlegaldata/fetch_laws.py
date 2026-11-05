from normalize import (
    API_ROOT,
    IngestionError,
    RateLimitError,
    detail,
    law_scope,
    normalized_document,
    record_failure,
    records,
    require_id,
    require_string,
    section_key,
)


def collect_laws(failures, previous=()):
    laws = {"primary": {}, "optional": {}}
    stage = "law_books"
    try:
        books = records("law_books/", {"code": "BGB"})
        book = next(
            (item for item in books if isinstance(item, dict)
             and item.get("code") == "BGB" and item.get("latest") is True),
            None,
        )
        if book is None:
            raise IngestionError("latest BGB revision not found")
        book_id = require_id(book)
        cached = {
            item["id"]: item for item in previous
            if item.get("revision_date") == book.get("revision_date")
        }
        stage = "laws"
        for row in records("laws/", {"book_id": book_id, "limit": 500}):
            try:
                record_id = require_id(row)
                key = section_key(require_string(row, "section"))
                scope = law_scope(key)
                if not scope:
                    continue
                if row.get("book") != book_id:
                    raise IngestionError("unexpected BGB revision")
                section = f"{key[0]}{key[1]}"
                if section in laws[scope]:
                    continue
                saved = cached.get(f"oldp:law:{record_id}")
                if saved and saved.get("section") == section and saved.get("scope") == scope:
                    laws[scope][section] = saved
                    continue
                law = detail("laws", row)
                title = f"BGB § {section}"
                if law.get("title"):
                    title += f" {require_string(law, 'title')}"
                document = normalized_document(
                    "law", record_id, title, law.get("content"), f"{API_ROOT}laws/{record_id}/"
                )
                document.update(
                    law_book="BGB", section=section, scope=scope,
                    official_source_url=f"https://www.gesetze-im-internet.de/bgb/__{section}.html",
                    revision_date=book.get("revision_date"),
                )
                laws[scope][section] = document
            except IngestionError as error:
                record_failure(failures, "law", row, error)
                if isinstance(error, RateLimitError):
                    break
        if not any(laws.values()):
            raise IngestionError("no in-scope BGB sections collected")
    except IngestionError as error:
        record_failure(failures, "law", stage, error)
    return tuple(
        sorted(group.values(), key=lambda law: section_key(law["section"]))
        for group in laws.values()
    )
