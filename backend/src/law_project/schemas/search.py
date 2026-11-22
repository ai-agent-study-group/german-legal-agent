"""검색 결과 한 개의 모양. LLM 파이프라인(agent)에 넘기는 객체.

search()는 짧은 목록(SearchHit)을 돌려주고, 전문이 필요하면 read(id)로 Document를 가져간다.
"""

from typing import Literal

from pydantic import BaseModel, Field


class SearchHit(BaseModel):
    id: str = Field(description="문서 ID", examples=["oldp:law:129437"])
    type: Literal["law", "case"] = Field(description="조문(law) / 판례(case)")
    title: str
    excerpt: str = Field(description="본문 중 검색어 주변 부분 (최대 약 500자). 전문은 read(id)로")
    score: float = Field(description="관련도. 클수록 관련 있음")
    source_url: str