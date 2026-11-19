# German Legal Agent — Data Collection Dashboard

저장소 루트에서 Python 3.10 이상과 Streamlit 1.57 이상으로 실행합니다.

```powershell
python -m pip install "streamlit>=1.57"
streamlit run internal_demo/app.py
```

브라우저에서 [localhost:8501](http://localhost:8501)을 엽니다. 인증하려면 앱을 시작하는 셸에 `OLDP_API_TOKEN`을 설정합니다. 화면에는 설정 여부만 표시됩니다.

## 수집과 결과 확인

- **Law Collection**에서 Primary, Optional 또는 두 범위를 선택합니다. 기본 범위는 535–580a입니다. 536a 같은 접미사도 입력할 수 있습니다. Law Limit을 비워 두면 범위 안의 조항을 모두 수집합니다. 숫자를 입력하면 범위와 scope를 적용한 뒤 두 scope를 합산해 해당 개수까지 수집합니다.
- **Case Collection**에서 BGH, 검색할 토픽, 이번 실행에서 추가할 신규 판례 수를 선택합니다. 기본값은 50건이며 최대 500건을 요청할 수 있습니다. 실제 수집 건수는 검색 결과, 중복 제거, 인용 필터 및 API 요청 한도에 따라 달라집니다.
- **Resume**은 기존 BGB 조항을 재사용합니다. **Debug mode**는 API 응답 샘플을 로그에 추가합니다. 두 수집 유형은 독립적으로 켜거나 끌 수 있습니다.
- **Run Data Collection**을 누르면 저장된 결과를 **Laws**, **Cases**, **Raw Cases**, **Failures**, **Summary** 탭에서 확인할 수 있습니다. 이전 판례에 토픽 메타데이터가 없으면 토픽 미리보기 필터는 제목과 본문을 검색합니다.

## Dashboard 구조와 통계

상단에 데이터 소스, Open Legal Data 인증 상태, AI 요약 설정 상태와 모델 이름을 표시합니다. 키 값은 표시하지 않습니다. 왼쪽에서 도메인과 수집 유형을 고르고, 활성화한 수집 유형의 설정을 조절합니다. **New Cases to Add**는 이번 실행에서 추가할 신규 unique 판례 수이며 기본값은 50, 최대값은 500입니다.

오른쪽 **Current Dataset Status**는 화면을 열거나 위젯을 조작할 때마다 Primary Laws, Optional Laws, Final Cases, Raw Cases, Parsing Failures의 실제 JSON 목록 길이를 계산합니다. 파일이 없거나 읽을 수 없으면 **Not available**을 표시합니다.

아래 **Last Run Statistics**는 ingestion_summary.json의 최근 실행 통계를 표시합니다. 현재 파일 건수와 별도로 기존 판례, 신규 추가, 중복 생략, AI 요약 생성 및 실패, 총 판례, 파싱 실패를 보여줍니다. 이전 형식의 요약에 필드가 없으면 **Not available**을 표시합니다.

실행 버튼을 누르면 실행 직전 건수를 기록합니다. 수집 프로세스가 종료된 뒤 파일을 다시 읽어 현재 건수, 미리보기, 마지막 실행 통계를 자동으로 갱신합니다. 별도의 API 호출 없이 저장된 파일을 읽습니다. Before run과 Now는 이 브라우저 세션의 마지막 실행 전 건수와 현재 파일 건수를 비교합니다.

표의 text는 앞 350자만 표시합니다. 레코드를 선택하고 **Full text**를 펼치면 전체 요약 또는 원문을 확인할 수 있습니다. Raw Cases는 별도 archive를 읽습니다. **Execution Log**에서 현재 세션의 실행 로그를 확인할 수 있으며 실패하면 자동으로 펼쳐집니다.

## 파이프라인 연결과 데이터 보호

앱은 같은 Python 인터프리터에서 `fetch_cases.py --mietrecht`를 별도 프로세스로 실행합니다. Law/Case 토글은 `--laws-only` 또는 `--cases-only`에, 범위와 제한은 `--law-scope`, `--section-from`, `--section-to`, `--law-limit`에 매핑됩니다. 판례에는 `--court`, 반복 가능한 `--topic`, `--case-limit`을 전달합니다. 수집기는 `fetch_laws.py`와 `normalize.py`를 재사용합니다.

판례 검색은 API의 다음 페이지를 따라가며 후보를 판례 ID로 합칩니다. 기존 Open Legal Data ID를 먼저 확인하고 신규 목표를 채우거나 검색 결과가 소진될 때까지 페이지를 탐색합니다. 종료 코드와 토큰을 가린 stdout/stderr는 실행 후 확인할 수 있습니다.

비활성 수집 유형과 선택하지 않은 law scope의 파일은 그대로 유지합니다. 법률 필터 실행은 선택한 법률 파일을 갱신합니다. 판례는 ID 기반으로 신규 요약을 추가합니다. 실패 사유는 **Execution Log**와 **Failures**에서 확인할 수 있습니다.

## 도메인 확장

새 도메인 수집기가 준비되면 `app.py`의 `DOMAINS`에 CLI 진입점, 토픽과 관련 조항, 법원, scope를 등록합니다. 출력 파일이나 CLI 규약이 다르면 해당 도메인의 인자 매핑과 미리보기 경로도 연결합니다. Housing 토픽과 지원 법원은 `fetch_cases.py`의 `HOUSING_SEARCHES`와 `CASE_COURTS`에서 관리합니다.

판례 요약에는 `OPENAI_API_KEY`와 `OLDP_SUMMARY_MODEL` 환경변수가 필요합니다. 원문과 실패한 요약의 재시도 자료는 `web/data/raw/bgh_mietrecht_cases_raw.json`에 보관됩니다. 기존 원문 판례의 최초 마이그레이션도 AI 호출을 사용하며, 요약 실패 레코드는 최종 RAG 파일에서 제외됩니다. 상세 동작은 ingestion/Openlegaldata/README.md를 참고하세요.
