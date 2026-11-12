"""② 검색: 키워드 점수로 자료를 찾고, id로 본문을 읽는다.

나중에 벡터 검색으로 바꿀 때 고치는 곳은 이 파일의 search()뿐이다.
(함수 이름·인자·돌려주는 모양을 그대로 두면 tools.py와 그래프는 그대로 쓴다.)

직접 실험해 볼 수 있다 (agent/ 폴더에서):
    .venv/bin/python -m legal_agent.search Kaution
"""

import math
import re
import sys
from dataclasses import dataclass

from legal_agent.data import Source, load_sources

TOP_K = 3  # 검색 결과 최대 개수 (팀 데모의 search_sources도 3개)
EXCERPT_CHARS = 200  # 검색 결과에 보여 주는 발췌 길이
READ_MAX_CHARS = 4000  # 본문을 읽을 때 돌려주는 최대 길이 (판례는 길어서 토큰 비용이 커진다)


@dataclass(frozen=True)
class Hit:
    source: Source
    score: float
    excerpt: str


def _words(text: str) -> set[str]:
    # \w+ : 글자·숫자가 이어진 덩어리 (정규식, PHP의 preg_match_all과 같다). ä ö ü ß도 글자로 본다.
    # {... for ... in ...} : 집합(set) 컴프리헨션. 중복이 사라지는 목록을 한 줄로 만든다.
    return {w for w in re.findall(r"\w+", text.lower()) if len(w) >= 2}


def search(domain: str, query: str, kind: str = "law", top_k: int = TOP_K) -> list[Hit]:
    """질문의 단어가 많이 들어 있는 자료일수록 높은 점수를 준다."""
    pool = [s for s in load_sources(domain) if s.kind == kind]
    words = _words(query)

    # 단어마다 "그 단어가 들어 있는 자료 수"를 센다.
    # 거의 모든 자료에 있는 흔한 단어(예: bgb)는 점수를 덜 주고, 드문 단어는 더 준다.
    haystacks = {s.id: s.text.lower() for s in pool}
    titles = {s.id: s.title.lower() for s in pool}
    weights = {}
    for w in words:
        count = sum(1 for s in pool if w in titles[s.id] or w in haystacks[s.id])
        if count:  # 어디에도 없는 단어는 버린다
            weights[w] = math.log(1 + len(pool) / count)

    hits = []
    for s in pool:
        score = 0.0
        for w, weight in weights.items():
            if w in titles[s.id]:
                score += 3 * weight  # 제목에 있으면 본문에 있을 때보다 3배
            elif w in haystacks[s.id]:
                score += weight
        if score > 0:
            hits.append(Hit(source=s, score=score, excerpt=s.text[:EXCERPT_CHARS].replace("\n", " ")))

    # 점수 높은 순, 같으면 id 순 (같은 입력이면 항상 같은 결과가 나오게)
    hits.sort(key=lambda h: (-h.score, h.source.id))
    return hits[:top_k]


def read(domain: str, source_id: str, max_chars: int = READ_MAX_CHARS) -> tuple[Source, str, bool] | None:
    """id로 자료를 찾아 (자료, 잘린 본문, 잘렸는지)를 돌려준다. 없으면 None."""
    for s in load_sources(domain):
        if s.id == source_id:
            return s, s.text[:max_chars], len(s.text) > max_chars
    return None


# 이 파일을 직접 실행했을 때만 도는 부분 (다른 파일이 import할 때는 실행되지 않는다).
# PHP에서 "if (php_sapi_name() === 'cli')"로 CLI 실행만 따로 두는 것과 비슷하다.
if __name__ == "__main__":
    query = " ".join(sys.argv[1:]) or "Kaution"
    for kind in ("law", "case"):
        print(f"--- {kind} 검색: {query!r}")
        for h in search("housing", query, kind=kind):
            print(f"{h.score:6.2f}  {h.source.id}  {h.source.title}")
