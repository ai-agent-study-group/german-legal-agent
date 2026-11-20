---
제목: "Data Collection"
유형: "위키"
설명: "GitHub Wiki 에서 자동 동기화된 문서입니다."
---

# Data Collection

German Legal Agent에서 사용하는 법률 및 판례 데이터를 수집하고, Backend / RAG / LLM에서 사용할 수 있는 JSON 형태로 정규화하는 파이프라인입니다.

현재 PoC에서는 **Housing / Mietrecht** 도메인을 대상으로 BGB 법률 조항과 Bundesgerichtshof(BGH) 판례를 수집합니다.

## 전체 흐름

```text
Streamlit Data Collection Dashboard
        ↓
Open Legal Data API
        ↓
┌───────────────────────┐
│ Law Collection        │
│ fetch_laws.py         │
└───────────────────────┘

┌───────────────────────┐
│ Case Collection       │
│ fetch_cases.py        │
└───────────────────────┘
        ↓
Duplicate Check
        ↓
Raw Case Archive
        ↓
OpenAI API
        ↓
German Case Summary
        ↓
Normalized Final JSON
        ↓
Backend / RAG / LLM
```

## 코드 구조

```text
ingestion/Openlegaldata/
├── fetch_cases.py
├── fetch_laws.py
├── normalize.py
├── summarize.py
├── test_ingestion.py
└── README.md

internal_demo/
├── app.py
└── README.md
```

### `fetch_cases.py`

BGH 판례 수집의 메인 ingestion entry point입니다.

주요 기능:

- Open Legal Data 판례 검색
- Housing / Mietrecht topic filtering
- BGH court filtering
- API pagination
- Open Legal Data ID 기반 duplicate check
- 기존 데이터 유지
- 신규 unique case만 incremental append
- raw case archive 저장
- AI summarization 호출
- ingestion statistics 생성

`--case-limit`은 최종 데이터 개수를 의미하지 않고, **이번 실행에서 추가할 신규 unique case의 최대 개수**를 의미합니다.

예:

```text
현재 Case: 50

--case-limit 20

→ 신규 Case 최대 20개 추가
→ 최종 Case 최대 70개
```

## `fetch_laws.py`

BGB Mietrecht 법률 조항을 Open Legal Data에서 수집합니다.

현재 범위:

- Primary: BGB §§535–577a
- Optional: BGB §§578–580a

다음 조건을 설정할 수 있습니다.

- Law scope
- Section From / To
- Law limit

## `normalize.py`

Open Legal Data에서 받은 데이터를 프로젝트에서 공통으로 사용할 수 있는 JSON schema로 변환합니다.

공통 field 예:

```json
{
  "id": "oldp:case:12345",
  "type": "case",
  "title": "...",
  "text": "...",
  "source": "Open Legal Data",
  "source_url": "..."
}
```

## `summarize.py`

판례 원문 전체를 OpenAI Responses API로 전달하고, **300–500단어의 독일어 법률 요약**을 생성합니다.

요약 시 다음 내용을 보존하도록 설정되어 있습니다.

- 핵심 법적 쟁점
- 주요 사실관계
- 법원의 판단
- 판단의 주요 논거
- 관련 BGB 조항

최종 RAG용 case JSON에서는 전체 판례 원문 대신 AI summary를 `text`에 저장합니다.

```json
{
  "text_type": "ai_summary",
  "language": "de"
}
```

원문은 별도의 raw archive에 유지합니다.

## Incremental Collection

판례 수집은 기존 JSON을 매번 새로 만드는 방식이 아니라 **incremental append 방식**을 사용합니다.

```text
기존 JSON
   ↓
Existing ID 확인
   ↓
Open Legal Data 검색
   ↓
Duplicate ID
   → Skip

New ID
   ↓
Raw 저장
   ↓
AI Summary
   ↓
Final JSON에 추가
```

따라서 스크립트를 여러 번 실행해도 기존 데이터는 유지되고 새로운 데이터만 추가됩니다.

## 데이터 저장 구조

### Raw Archive

```text
web/data/raw/
└── bgh_mietrecht_cases_raw.json
```

Open Legal Data에서 가져온 판례 원문을 보관합니다.

용도:

- AI summary 검증
- summary 실패 시 재시도
- 원문 확인

### Final Dataset

```text
web/data/samples/
├── bgb_mietrecht_laws.json
├── bgb_mietrecht_optional_laws.json
├── bgh_mietrecht_cases.json
├── ingestion_summary.json
└── parsing_failures.json
```

### `bgh_mietrecht_cases.json`

RAG / LLM에서 사용할 최종 판례 데이터입니다.

판례 원문 대신 독일어 AI summary가 저장됩니다.

### `ingestion_summary.json`

최근 ingestion 실행 결과를 저장합니다.

예:

```json
{
  "existing_cases": 50,
  "new_cases_added": 20,
  "duplicate_cases_skipped": 15,
  "ai_summaries_generated": 20,
  "summarization_failed": 0,
  "total_cases": 70
}
```

### `parsing_failures.json`

수집, parsing 또는 AI summarization 과정에서 실패한 record와 원인을 기록합니다.

## Data Collection Dashboard

Streamlit 기반 internal dashboard를 제공합니다.

실행:

```powershell
streamlit run internal_demo/app.py
```

Dashboard에서 다음 작업을 수행할 수 있습니다.

- Domain 선택
- Law Collection ON / OFF
- Case Collection ON / OFF
- Law scope 설정
- BGB section 범위 설정
- Law limit 설정
- Case topic 선택
- Court 선택
- New Cases to Add 설정
- Resume / Debug 설정
- Data Collection 실행
- Current Dataset Status 확인
- Last Run Statistics 확인
- Law / Case / Raw data preview
- Failure 및 execution log 확인

현재 지원 domain:

```text
Housing / Mietrecht
```

향후 다음 domain으로 확장할 수 있도록 구조를 분리하고 있습니다.

```text
Visa
Labor
Human Rights
```

## API 및 환경변수

판례 수집 및 AI summary를 사용하려면 다음 환경변수가 필요합니다.

```text
OLDP_API_TOKEN
OPENAI_API_KEY
OLDP_SUMMARY_MODEL
```

API key와 token은 GitHub repository에 저장하지 않고 각 개발자의 local environment에서 관리합니다.

현재 AI summary model은:

```text
gpt-6-luna
```

을 사용합니다.

## 현재 구현 상태

- BGB Mietrecht Law Collection
- BGH Mietrecht Case Collection
- Topic / Court Filtering
- Pagination
- ID 기반 Duplicate 제거
- Incremental Append
- Raw / Final 데이터 분리
- OpenAI 판례 요약
- Parsing / Summarization Failure Logging
- Streamlit Data Collection Dashboard
- Dataset Status / Last Run Statistics
- Automated Ingestion Tests

## 향후 작업

- Visa / Labor / Human Rights domain 확장
- Backend normalized schema 최종 합의
- Vector DB 연결
- RAG retrieval 연결
- LLM / Agent pipeline과 통합