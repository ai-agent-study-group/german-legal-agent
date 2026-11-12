---
제목: "LLM 설계"
유형: "위키"
설명: "GitHub Wiki 에서 자동 동기화된 문서입니다."
---

# LLM 설계

[현재 구조와 기술](#doc=wiki/Home.md) · 영역별 설계: [PO/QA](#doc=wiki/구조-PO-QA.md) · [FE](#doc=wiki/구조-FE.md) · [BE](#doc=wiki/구조-BE.md) · **LLM** · [데이터 수집](#doc=wiki/구조-데이터-수집.md) · [DevOps](#doc=wiki/구조-DevOps.md)

인공지능 모델에 전달할 질문·지시문과 답변 생성·자료 검색의 실행 흐름을 다루는 역할입니다. 모델·프롬프트·도구 실행과 실험 결과를 기록합니다.

## 1. 역할

- 질문을 받아 관련 법률·판례를 검색(RAG / Vector Search)하고, 근거·출처(Citation)와 함께 답변 생성
- 모델·프롬프트·도구 호출 흐름을 구성하고 실험 결과를 비교

## 2. 현재 상태

- `agent/`에 pydantic-ai·Groq를 쓴 예시(`legal_agent_groq_example.py`, `tool-test.mjs`)가 있음. 방향 탐색용 PoC이며 채택을 뜻하지 않음
- 모델·프레임워크·호출 위치(FE/BE)는 미정

## 3. 데이터 담당과 맞출 것

[데이터 수집](#doc=wiki/구조-데이터-수집.md)의 Mietrecht 법률·판례 Schema가 Retrieval의 입력입니다.

- 검색 단위(조항·판례), 반환 형식, 근거로 보여줄 필드(조항 번호·Aktenzeichen·Quelle)
- 출처 없는 답변을 막는 방식(근거 필수, Citation 포함)
- 평가 셋으로 프롬프트·모델 변경 전후를 비교 ([구조 PO/QA](#doc=wiki/구조-PO-QA.md))

## 4. 정할 것 (미정)

- 사용할 모델과 호출 방식·비용·키 관리
- RAG 저장소·임베딩 방식 ([구조 BE](#doc=wiki/구조-BE.md)와 함께)
- 답변 품질 평가 기준
