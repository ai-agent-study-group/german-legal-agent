# Wohnraummietrecht 데이터 수집

Open Legal Data에서 BGB 임대차 조항과 Bundesgerichtshof(BGH) 판결의 원문을 가져와 Backend와 RAG에서 사용할 JSON으로 저장합니다. `text`에는 API의 HTML 본문에서 태그를 제거한 독일어 텍스트가 들어갑니다.

## 실행

저장소 루트에서 Python 3.9 이상으로 실행합니다. 표준 라이브러리만 사용합니다.

```powershell
python -B ingestion/Openlegaldata/fetch_cases.py --mietrecht
```

기존 범용 판례 샘플을 다시 생성하려면 같은 명령에서 `--mietrecht`를 생략합니다.

부분 수집에 이어서 실행할 때는 `--mietrecht --resume`을 사용합니다. 현재 BGB 판과 ID가 같은 저장 조항의 원문을 재사용합니다. 판례 후보는 다시 조회합니다. 오류가 있는 재실행에서 저장된 레코드 수가 줄어들면 기존 출력 파일을 보존합니다.

## 범위와 선정 기준

- **Primary**는 BGB §§ 535–548의 일반 임대차 규정과 §§ 549–577a의 주거 임대차 규정입니다. 최신 BGB 판의 실제 API 목록을 순회하므로 § 536a, § 555a, § 556d, § 573a 같은 조항도 포함합니다.
- **Optional**은 BGB §§ 578–580a입니다. 별도 파일로 저장합니다.
- **판례**는 BGH 검색 결과 중 주거 임대차 검색어와 BGB 인용 근거를 함께 가진 판결을 최대 50건 수집합니다. 본문의 명시적인 BGB 인용을 우선하고 Open Legal Data의 구조화된 인용 인덱스로 보완합니다. 인용 조항 수, 날짜 순으로 후보를 정렬하고, 상세 응답에서 법원과 필수 메타데이터를 확인합니다. 날짜와 사건번호가 같은 판결은 한 번만 저장합니다.

## 출력

`web/data/samples/`에 저장합니다.

| 파일 | 내용 |
| --- | --- |
| `bgb_mietrecht_laws.json` | Primary BGB 조항 |
| `bgb_mietrecht_optional_laws.json` | Optional BGB 조항 |
| `bgh_mietrecht_cases.json` | BGH 판례 원문과 날짜, 사건번호, ECLI, 인용 조항 |
| `parsing_failures.json` | ID, 레코드 유형, 실패 원인. 목록·검색 오류의 경우 조회 단계도 기록합니다. |
| `ingestion_summary.json` | 데이터 유형별 수집 건수, 실패 건수와 출처 |

모든 문서는 `id`, `type`, `title`, `text`, `source`, `source_url`을 포함합니다. ID에는 법률과 판례를 구별하는 접두사를 붙입니다. 법률 문서에는 Gesetze im Internet의 공식 링크를 추가합니다. 판례는 API가 제공하는 원출처 URL을 우선 사용하고 없으면 상세 API URL을 사용합니다. `cited_laws`는 수집 범위의 관련 인용을 담습니다.

## API 제약

- 운영 API는 BGB 판 목록에 `/api/law_books/`를 사용합니다. 판례 검색의 법원 코드는 `BGH`입니다.
- 상세 요청은 목록에서 제공하지 않는 본문과 판례 메타데이터를 가져옵니다. [API 문서](https://openlegaldata.github.io/oldp/v0.13.2/api/api-overview.html)는 익명 요청을 일 100회, 인증 요청을 시간당 5,000회로 안내합니다. 실행에 100회 이상 필요할 수 있으므로 토큰이 있으면 로컬 환경 변수 `OLDP_API_TOKEN`으로 전달하세요.
- 검색은 주거 임대차 검색어와 제한된 결과 페이지를 사용합니다. 수집 결과는 인용을 기준으로 선정한 PoC 표본이며, 중요 판례의 법률 전문가 검토는 별도입니다.
- 누락이나 API 오류가 있는 레코드는 별도로 기록하고 수집을 계속합니다. 실패가 있거나 필수 데이터셋이 비어 있으면 부분 결과를 저장하고 종료 코드 1을 반환합니다.
