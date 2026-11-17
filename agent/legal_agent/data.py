"""① 자료 읽기: JSON 파일들을 읽어서 조문과 판례를 같은 모양(Source)으로 만든다.

자료 형식이 바뀌면(다른 팀이 형식을 바꾸거나 DB로 옮기면) 이 파일만 고친다.
"""

import json
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

# JSON 파일이 있는 폴더 = 이 파일(data.py)의 부모(legal_agent/)의 부모(agent/)
DATA_DIR = Path(__file__).resolve().parent.parent

# 분야(domain) -> 그 분야의 자료 파일 목록. 분야가 늘면 여기에 추가한다.
DOMAIN_FILES = {
    "housing": [
        "bgb_mietrecht_laws.json",
        "bgb_mietrecht_optional_laws.json",
        "bgb_mietrecht_cases.json",
    ],
}


# dataclass: "필드만 있는 클래스"를 짧게 만드는 문법 (PHP 8의 생성자 프로퍼티 승격과 비슷).
# frozen=True: 만든 뒤에는 값을 바꿀 수 없다 (자료를 실수로 고치지 않게).
@dataclass(frozen=True)
class Source:
    id: str  # 예: "oldp:law:129433"
    kind: str  # "law"(조문) 또는 "case"(판례)
    title: str  # 예: "BGB § 535 Inhalt und Hauptpflichten des Mietvertrags"
    text: str  # 본문 (독일어)
    url: str  # 출처 주소 (답변에 인용할 때 쓴다)


def _to_source(raw: dict) -> Source:
    # 조문은 공식 사이트 주소(official_source_url)가 있고, 판례는 source_url만 있다.
    # dict.get(키, 기본값): 키가 없으면 기본값. PHP의 $raw['x'] ?? 기본값 과 같다.
    url = raw.get("official_source_url") or raw["source_url"]
    return Source(id=raw["id"], kind=raw["type"], title=raw["title"], text=raw["text"], url=url)


# lru_cache: 같은 인자로 다시 부르면 처음 계산한 결과를 재사용하는 데코레이터 (캐시).
# 1MB가 넘는 JSON을 호출할 때마다 다시 읽지 않게 한다.
# 캐시 값이 바뀌면 안 되므로 list가 아니라 tuple(수정 불가 목록)로 돌려준다.
@lru_cache(maxsize=None)
def load_sources(domain: str) -> tuple[Source, ...]:
    if domain not in DOMAIN_FILES:
        raise ValueError(f"알 수 없는 분야: {domain!r}. 가능한 값: {list(DOMAIN_FILES)}")
    sources = []
    for filename in DOMAIN_FILES[domain]:
        with open(DATA_DIR / filename, encoding="utf-8") as f:  # with: 블록이 끝나면 파일을 자동으로 닫는다
            sources.extend(_to_source(raw) for raw in json.load(f))
    return tuple(sources)
