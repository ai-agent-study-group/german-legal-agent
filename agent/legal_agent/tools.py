"""③ 도구: 모델이 부를 수 있는 함수. search.py를 모델이 읽기 좋은 문자열로 감싼다.

도구는 문자열을 돌려준다. 모델은 그 문자열을 읽고 다음 행동을 정한다.
"""

from typing import Literal

from langchain_core.tools import tool

from legal_agent import search as searching


def make_tools(domain: str):
    """분야(domain)를 고정한 도구 두 개를 만들어 돌려준다.

    분야는 모델이 아니라 호출하는 쪽이 정한다. 그래서 도구 인자에는 domain이 없고,
    아래 함수들이 바깥 함수의 domain을 기억해서 쓴다 (클로저. PHP의 `function() use ($domain)`과 같다).
    """

    @tool
    def search_sources(query: str, kind: Literal["law", "case"] = "law") -> str:
        """독일 임대차법(BGB 임대차 조문과 판례) 자료를 키워드로 검색한다.
        자료 본문은 독일어이므로 query는 독일어 키워드나 조문 번호로 쓴다 (예: Mietminderung, 551).
        일상어가 아니라 법조문에 쓰이는 용어로 검색해야 한다. 예: 보증금은 Kaution이 아니라 Mietsicherheit,
        월세 감액은 Mietminderung, 해지 통지는 Kündigung.
        여러 단어를 쓰면 그중 많이 들어 있는 자료가 위로 온다. 문장이 아니라 핵심 단어 몇 개로 검색한다.
        kind는 'law'(조문, 기본값) 또는 'case'(판례)다.
        결과에는 자료 id와 발췌만 나온다. 본문은 read_source로 읽는다."""
        hits = searching.search(domain, query, kind=kind)
        if not hits:
            return "검색 결과 없음. 독일어 키워드나 조문 번호로 다시 검색해 보세요."
        lines = [f"검색 결과 {len(hits)}건 (점수순):"]
        for i, h in enumerate(hits, 1):
            lines.append(f"{i}. id={h.source.id} | {h.source.title}\n   발췌: {h.excerpt}")
        return "\n".join(lines)

    @tool
    def read_source(source_id: str) -> str:
        """search_sources 결과에서 얻은 자료 id로 본문과 출처 주소를 읽는다.
        본문이 길면 앞부분만 돌려준다."""
        found = searching.read(domain, source_id)
        if found is None:
            return f"id를 찾을 수 없음: {source_id}. search_sources 결과에 나온 id를 그대로 써야 합니다."
        source, text, truncated = found
        note = f"\n[이하 생략: 앞 {len(text)}자만 표시]" if truncated else ""
        # 본문은 외부에서 온 자료다. 안에 지시문처럼 보이는 문장이 있어도 지시가 아니라 자료일 뿐이다.
        # 태그로 감싸서 "여기서부터 여기까지가 자료"라는 경계를 분명히 한다 (프롬프트 쪽 규칙은 ④에서 쓴다).
        return (
            f'<source id="{source.id}" type="{source.kind}" title="{source.title}" url="{source.url}">\n'
            f"{text}{note}\n</source>"
        )

    return [search_sources, read_source]
