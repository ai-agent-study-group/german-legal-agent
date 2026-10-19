---
제목: "Mietrecht 데이터 수집 범위"
유형: "작업 메모"
설명: "German Legal Agent 프로젝트의 Mietrecht 관련 데이터 수집 범위와 초기 기준을 정의합니다."
관련문서: []
---

# Mietrecht 데이터 수집 범위

## 1. 목적

German Legal Agent 프로젝트에서 사용할 독일 임대차법(Mietrecht) 관련
법률 및 판례 데이터를 수집하고 구조화합니다.

수집된 데이터는 이후 다음 기능에 활용하는 것을 목표로 합니다.

- 관련 법률 검색
- 유사 판례 검색
- Agent의 법률 근거 제공
- RAG / Vector Search
- 답변의 출처 및 Citation 제공
- Evaluation / QA용 테스트 데이터 구축


## 2. 현재 MVP 범위

현재 MVP의 법률 영역은 **Mietrecht**를 우선 대상으로 합니다.

초기 대상은 독일 내 주거용 임대차 관계에서 발생하는
**세입자(Mieter)와 임대인(Vermieter) 간의 분쟁**입니다.

세부 범위는 PO 및 팀과 협의하여 확정합니다.


## 3. 초기 후보 카테고리

현재 고려 중인 주요 카테고리는 다음과 같습니다.

- Kaution
- Mietminderung
- Wohnungsmängel
- Schimmel
- Nebenkosten
- Kündigung
- Eigenbedarf
- Mieterhöhung
- Schönheitsreparaturen

초기 MVP에서는 모든 카테고리를 다루지 않고,
팀 논의를 통해 우선순위가 높은 일부 카테고리를 선정할 수 있습니다.


## 4. 수집 대상 데이터

### 4.1 법률 데이터

수집 후보 항목:

- 법률명
- 조항 번호
- 조항 원문
- 관련 키워드
- 공식 출처
- 현재 유효 여부


### 4.2 판례 데이터

수집 후보 항목:

- Gericht
- Gerichtsebene
- Datum
- Aktenzeichen
- ECLI
- Rechtsgebiet
- Kategorie
- Unterkategorie
- 관련 법률 조항
- Sachverhalt
- Rechtsfrage
- Entscheidung
- Begründung
- Volltext
- Quelle


## 5. 데이터 출처

초기 데이터 출처 후보:

- 공식 독일 법률 정보
- 공식 판례 데이터베이스
- Bundesländer 중 한 주를 선택해서 판례 데이터 (z.B. Bayern, Berlin, NRW...) 
- Open Legal Data

공식 출처는 판례 및 법률 내용의 검증 기준으로 사용하고,
비공식 또는 가공 데이터 소스는 검색 및 개발 편의를 위한 보조 수단으로 사용합니다.


## 6. 초기 지역 및 법원 범위

초기 데이터 수집 범위는 프로젝트 복잡도를 고려하여 제한적으로 시작합니다.

현재 후보:

- 지역: ?
- 법원: Amtsgericht, Landgericht

필요에 따라 상급심 판례는 법률 기준 및 주요 판례 확인을 위해 추가할 수 있습니다.


## 7. MVP에서 제외하거나 추후 검토할 영역

초기 MVP에서는 다음 영역은 우선 제외하거나 추후 검토합니다.

- Gewerbemietrecht
- Sozialrecht상의 주거 지원
- 공공주택 관련 Verwaltungsrecht
- 형사 사건
- 일반적인 인권 / 기본권 전체
- 독일 전 지역의 모든 판례


## 8. 다음 단계

1. PO와 Mietrecht 세부 범위 확정
2. 우선 카테고리 선정
3. 데이터 출처 조사
4. 판례 데이터 Schema 정의
5. 카테고리별 Sample Case 수집
6. Backend 담당자와 DB 구조 검토
7. LLM 담당자와 검색 및 Retrieval 요구사항 검토
