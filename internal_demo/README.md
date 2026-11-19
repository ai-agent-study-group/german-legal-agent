# German Legal Agent — Data Collection Demo

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
- **Run Data Ingestion**을 누르면 저장된 결과를 요약과 **Laws**, **Cases**, **Failures**, **Summary** 탭에서 확인할 수 있습니다. 이전 판례에 토픽 메타데이터가 없으면 토픽 미리보기 필터는 제목과 본문을 검색합니다.

## 파이프라인 연결과 데이터 보호

앱은 같은 Python 인터프리터에서 `fetch_cases.py --mietrecht`를 별도 프로세스로 실행합니다. Law/Case 토글은 `--laws-only` 또는 `--cases-only`에, 범위와 제한은 `--law-scope`, `--section-from`, `--section-to`, `--law-limit`에 매핑됩니다. 판례에는 `--court`, 반복 가능한 `--topic`, `--case-limit`을 전달합니다. 수집기는 `fetch_laws.py`와 `normalize.py`를 재사용합니다.

판례 검색은 API의 다음 페이지를 따라가며 후보를 판례 ID로 합칩니다. 기존 Open Legal Data ID를 먼저 확인하고 신규 목표를 채우거나 검색 결과가 소진될 때까지 페이지를 탐색합니다. 종료 코드와 토큰을 가린 stdout/stderr는 실행 후 확인할 수 있습니다.

비활성 수집 유형과 선택하지 않은 law scope의 파일은 그대로 유지합니다. 법률 필터 실행은 선택한 법률 파일을 갱신합니다. 판례는 ID 기반으로 신규 요약을 추가합니다. 실패 사유는 **Execution Log**와 **Failures**에서 확인할 수 있습니다.

## 도메인 확장

새 도메인 수집기가 준비되면 `app.py`의 `DOMAINS`에 CLI 진입점, 토픽과 관련 조항, 법원, scope를 등록합니다. 출력 파일이나 CLI 규약이 다르면 해당 도메인의 인자 매핑과 미리보기 경로도 연결합니다. Housing 토픽과 지원 법원은 `fetch_cases.py`의 `HOUSING_SEARCHES`와 `CASE_COURTS`에서 관리합니다.

판례 요약에는 `OPENAI_API_KEY`와 `OLDP_SUMMARY_MODEL` 환경변수가 필요합니다. 원문과 실패한 요약의 재시도 자료는 `web/data/raw/bgh_mietrecht_cases_raw.json`에 보관됩니다. 기존 원문 판례의 최초 마이그레이션도 AI 호출을 사용하며, 요약 실패 레코드는 최종 RAG 파일에서 제외됩니다. 상세 동작은 ingestion/Openlegaldata/README.md를 참고하세요.
