# Wohnraummietrecht 데이터 수집

Open Legal Data에서 BGB 임대차 조항과 BGH 판결을 수집합니다. 법률 text는 원문이며 판례의 최종 text는 독일어 AI 요약입니다.

## 실행

저장소 루트에서 Python 3.9 이상으로 실행합니다. 표준 라이브러리만 사용합니다.

```powershell
python -B ingestion/Openlegaldata/fetch_cases.py --mietrecht
```

기존 범용 판례 샘플을 다시 생성하려면 같은 명령에서 `--mietrecht`를 생략합니다.

부분 수집에 이어서 실행할 때는 `--mietrecht --resume`을 사용합니다. 현재 BGB 판과 ID가 같은 저장 조항의 원문을 재사용합니다. 판례 후보는 다시 조회합니다. 법률 오류 시 기존 법률 파일을 보존합니다. 판례는 Resume 선택과 무관하게 ID 기반으로 증분 저장합니다.

인증 환경에서 판례 5건을 먼저 수집하고 검색·상세 응답을 확인하려면 다음 명령을 실행합니다. 기본값은 50건이며 `--case-limit`으로 1–500건을 요청할 수 있습니다.

```powershell
python -B ingestion/Openlegaldata/fetch_cases.py --mietrecht --resume --case-limit 5 --debug
```

## 범위와 선정 기준

- **Primary**는 BGB §§ 535–548의 일반 임대차 규정과 §§ 549–577a의 주거 임대차 규정입니다. 최신 BGB 판의 실제 API 목록을 순회하므로 § 536a, § 555a, § 556d, § 573a 같은 조항도 포함합니다.
- **Optional**은 BGB §§ 578–580a입니다. 별도 파일로 저장합니다.
- **판례**는 BGH 검색 결과 중 주거 임대차 검색어와 BGB 인용 근거를 함께 가진 판결을 요청한 한도까지 수집합니다. 본문의 명시적인 BGB 인용을 우선하고 Open Legal Data의 구조화된 인용 인덱스로 보완합니다. 인용 인덱스 검색을 먼저 처리하고 상세 응답에서 법원과 필수 메타데이터를 확인합니다. 중복은 Open Legal Data ID로 판단합니다.

## 출력

`web/data/samples/`에 저장합니다.

| 파일 | 내용 |
| --- | --- |
| `bgb_mietrecht_laws.json` | Primary BGB 조항 |
| `bgb_mietrecht_optional_laws.json` | Optional BGB 조항 |
| `bgh_mietrecht_cases.json` | BGH 판례 독일어 AI 요약과 날짜, 인용 조항 |
| `parsing_failures.json` | ID, 레코드 유형, 실패 원인. 목록·검색 오류의 경우 조회 단계도 기록합니다. |
| `ingestion_summary.json` | 데이터 유형별 수집 건수, 실패 건수와 출처 |

모든 문서는 `id`, `type`, `title`, `text`, `source`, `source_url`을 포함합니다. ID에는 법률과 판례를 구별하는 접두사를 붙입니다. 법률 문서에는 Gesetze im Internet의 공식 링크를 추가합니다. 판례는 API가 제공하는 원출처 URL을 우선 사용하고 없으면 상세 API URL을 사용합니다. `cited_laws`는 수집 범위의 관련 인용을 담습니다.

## API 제약

- 운영 API는 BGB 판 목록에 `/api/law_books/`를 사용합니다. 판례 검색의 법원 코드는 `BGH`입니다.
- 판례 검색은 주제별 단일 검색을 실행하고 ID로 후보를 합칩니다. 검색 응답의 `court`는 법원 코드 문자열이며, `return_text=1`이면 `text`를 요청합니다. 상세 응답의 `court`는 객체이며 원문은 HTML `content`에 있습니다. 구조화 인용은 응답 행의 필드로 제공되는 대신 `cited_law_book`과 `cited_law_section` 검색 조건으로 확인합니다.
- 상세 요청은 목록에서 제공하지 않는 본문과 판례 메타데이터를 가져옵니다. [API 문서](https://openlegaldata.github.io/oldp/v0.13.2/api/api-overview.html)는 익명 요청을 일 100회, 인증 요청을 시간당 5,000회로 안내합니다. 실행에 100회 이상 필요할 수 있으므로 토큰이 있으면 로컬 환경 변수 `OLDP_API_TOKEN`으로 전달하세요.
- 검색은 주거 임대차 검색어와 API의 next 페이지를 사용합니다. 수집 결과는 인용을 기준으로 선정한 PoC 표본이며, 중요 판례의 법률 전문가 검토는 별도입니다.
- 누락·요약 실패는 parsing_failures.json에 기록합니다. API 오류 시 탐색을 중단하며, 성공한 요약과 원문은 보존합니다. 실패가 있으면 종료 코드 1을 반환합니다.


## 증분 판례와 AI 요약

환경변수는 앱을 시작하는 셸에 설정합니다.

- `OLDP_API_TOKEN`은 Open Legal Data 인증 키입니다.
- `OPENAI_API_KEY`는 OpenAI 요약 API 키입니다.
- `OLDP_SUMMARY_MODEL`은 계정에서 사용할 수 있는 Responses API 모델 ID입니다. 모델은 명시적으로 선택하며 기본값은 없습니다.

요약은 별도 AI API 사용량이 발생합니다. 표준 라이브러리 HTTP 클라이언트를 사용하므로 추가 SDK는 필요하지 않습니다. 키가 누락되면 판례 API 호출과 판례 파일 변경을 수행하지 않고 실패 로그와 실행 요약을 저장합니다. Law-only 실행에는 AI 설정이 필요하지 않습니다.

`--case-limit 50`은 이번 실행에 **최대 50개의 신규 unique ID**를 추가한다는 의미입니다. 기존 ID는 detail 조회와 AI 호출 전에 건너뜁니다. next 링크를 끝까지 탐색하며, 신규 목표 달성·결과 소진·API 오류 중 하나가 발생하면 멈춥니다. 기존 전역 후보 정렬 대신 인용 인덱스 검색부터 순차 처리하여 목표 달성 시 불필요한 후속 조회를 줄입니다.

`summarize.py`는 원문 전체를 OpenAI Responses API에 전달합니다. 프롬프트는 법적 쟁점, 사실관계, 판단, 핵심 논거 및 BGB 조항을 독일어 300–500단어로 보존하도록 지시합니다. 응답 완료 상태와 단어 수를 검증하며, 길이를 맞추기 위한 자동 재호출은 하지 않습니다. 이 검증은 법률적 정확성에 대한 전문가 검토를 대체하지 않습니다.

- 최종 RAG 데이터는 `web/data/samples/bgh_mietrecht_cases.json`에 저장합니다. `ecli`, `file_number`를 제거하고 `text_type: ai_summary`, `language: de`를 추가합니다.
- 원문은 요약 호출 **이전**에 `web/data/raw/bgh_mietrecht_cases_raw.json`에 ID별로 보관합니다. HTML을 정규화한 전체 텍스트이며 재시도에 필요한 메타데이터를 포함합니다.
- 기존 full-text 레코드는 archive에 보관한 후 요약합니다. 이미 `ai_summary` 및 `de`로 표시된 레코드는 재요약하지 않습니다. 기존 레코드의 변환은 신규 추가 한도에 포함되지 않습니다.
- 요약 검증에 실패한 원문은 archive에 남고 최종 파일에는 넣지 않습니다. 다음 실행에서 archive를 재사용하여 재시도합니다. 기존 원문 변환 실패 시 해당 레코드는 최종 파일에서 제외되므로 최초 마이그레이션 중 최종 건수가 줄 수 있습니다.
- AI 인증·연결·HTTP 오류가 발생하면 후속 AI 호출을 중단합니다. 이미 생성한 요약을 저장하며 다음 실행에서는 이를 재사용합니다.

파일별 atomic replace와 프로세스 간 파일 잠금으로 동시 실행과 중단 후 재시도를 보호합니다. 원문을 먼저 저장하고 성공한 요약을 checkpoint합니다. 실행이 강제 중단되어 AI 응답 수신과 checkpoint 사이에서 멈추면 해당 한 건은 다시 요약될 수 있습니다.

실행 요약에는 기존 law 필드와 함께 existing_cases, new_cases_added, duplicate_cases_skipped(고유 중복 ID 수), total_cases, ai_summaries_generated, summarization_failed가 저장됩니다. parsing_failures.json과 ingestion_summary.json은 가장 최근 실행 결과입니다.

오프라인 회귀 테스트

```powershell
python -B -m unittest discover -s ingestion/Openlegaldata -p test_ingestion.py
```
