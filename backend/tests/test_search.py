"""진짜 수집 데이터(web/data/samples/*.json)로 하는 검색 테스트.

샘플 질문으로 관련 조항·판례 검색
데이터 파일은 커밋하지 않아서, 파일이 없는 컴퓨터(CI 등)에서는 건너뛴다.

"""

import pytest

from law_project.core.config import get_settings
from law_project.search.loader import DATA_FILES
from law_project.search.service import get_documents, read, search

DATA_DIR = get_settings().data_dir
pytestmark = pytest.mark.skipif(
    not all((DATA_DIR / name).exists() for name in DATA_FILES),
    reason="수집 데이터 JSON이 없음",
)


def law_sections(hits):
    return [h.title.split()[2] for h in hits if h.type == "law"]  # "BGB § 536 ..." → "536"

# 조문, 판례가 다 읽힘
def test_all_documents_load():
    docs = get_documents()
    assert len([d for d in docs if d.type == "law"]) > 0
    assert len([d for d in docs if d.type == "case"]) > 0


def test_mietminderung_finds_section_536():
    hits = search("Mietminderung Mangel", "housing")
    assert law_sections(hits)[0] == "536"
    assert any(h.type == "case" for h in hits)


def test_mietsicherheit_finds_section_551():
    hits = search("Mietsicherheit", "housing")
    assert "551" in law_sections(hits)


def test_read_returns_full_text_longer_than_excerpt():
    hits = search("Mietminderung Mangel", "housing")
    case_hit = next(h for h in hits if h.type == "case")
    doc = read(case_hit.id)
    assert doc is not None
    assert len(doc.text) > len(case_hit.excerpt)