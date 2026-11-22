"""
Document: 조문과 판례의 공통 칸 (검색은 이것만 써도 된다)
LawDocument: 조문 전용 칸을 더한 것   (bgb_mietrecht_laws.json)
CaseDocument: 판례 전용 칸을 더한 것  (bgh_mietrecht_cases.json)

document가 parents 이고, 나머지 두개는 자식.
"""

from datetime import date
from typing import Literal

from pydantic import BaseModel, ConfigDict


class Document(BaseModel):
    model_config = ConfigDict(extra="ignore")  # 정의 안 한 칸은 무시 (ecli 등이 있어도·없어도 안 깨지게)

    id: str  
    type: Literal["law", "case"]
    title: str
    text: str
    source: str
    source_url: str
    domain: Literal["housing", "visa"] = "housing"  # 없으면 housing (지금 자료는 전부 임대차)


class LawDocument(Document):
    type: Literal["law"] = "law"
    law_book: str  # 예: "BGB"
    section: str  # 예: "551", "536a"
    scope: str | None = None  # "primary" / "optional"
    official_source_url: str | None = None
    revision_date: date | None = None


class CaseDocument(Document):
    type: Literal["case"] = "case"
    court: str  # 예: "Bundesgerichtshof"
    date: date
    decision_type: str | None = None  # 예: "Urteil", "Beschluss"
    cited_laws: list[str] = []  # 예: ["BGB § 536", "BGB § 551"]