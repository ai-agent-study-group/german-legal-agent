"""
json 파일을 파이썬이 쓸수있는 문서목록으로 바꾸어주는것.
json file --> loader.py(읽기 + 검사) --> 파이썬 목록 (law document, case document)
"""

import json
from pathlib import Path
from law_project.schemas.document import CaseDocument, Document, LawDocument

# 파일들을 열어서 json을 가져옴.
DATA_FILES: dict[str, type[Document]] = {
    "bgb_mietrecht_laws.json": LawDocument,
    "bgh_mietrecht_cases.json": CaseDocument,
}


def load_documents(data_dir: Path) -> list[Document]:
    documents: list[Document] = []
    for name, model in DATA_FILES.items():
        path = data_dir / name
        with path.open(encoding="utf-8") as f:
            records = json.load(f)
        # 한 건씩 양식대로 검사. 필수 칸이 빠지면 여기서 에러가 난다.
        documents.extend(model.model_validate(record) for record in records)
        # model.model_validate(record) 가 검사하는 부분.
    return documents