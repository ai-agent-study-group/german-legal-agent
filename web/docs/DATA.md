# 자료 수집과 검토

## 기본 예제

2026-10-11 공식 원문을 읽고 작성한 짧은 한국어 학습용 요약 4개입니다.
`kind: editorial_summary`로 원문 전체와 구분합니다. 전문 법률 검수를 의미하지 않습니다.

| 자료                            | 공식 원문                                                                               |
| ------------------------------- | --------------------------------------------------------------------------------------- |
| 보증금 상한·분할 납부·분리 보관 | https://www.gesetze-im-internet.de/bgb/__551.html                                       |
| 계약 종료 통지의 서면 형식      | https://www.gesetze-im-internet.de/bgb/__568.html                                       |
| 유학 체류 기본 요건             | https://www.make-it-in-germany.com/en/visa-residence/types/studying                     |
| 전문인력 취업 체류 기본 요건    | https://www.make-it-in-germany.com/en/visa-residence/types/work-qualified-professionals |

개별 반환 기한, 특정 비자 승인, 관할별 제출 서류를 판단할 자료는 없습니다.
변동이 큰 금액과 법정 기간을 데모 요약에 포괄적으로 나열하지 않습니다.

## 추가하는 순서

1. 공식 출처와 질문 범위를 정합니다. sources.json에 ID·분야·URL·본문 selector·한국어 키워드를 추가합니다.
2. 수집합니다. collect.py는 https 공식 호스트만 허용하고 자동으로 다른 링크를 따라 수집하지 않습니다.
3. pending 파일에서 본문 누락, 중복, 메뉴, 게시일과 수집일 차이를 확인합니다.
4. 원문과 비교하고 필요하면 짧은 한국어 요약을 작성합니다. 편집 언어도 갱신합니다.
5. review.py --approve <id>를 실행합니다. reviewedAt은 승인일이며 법 시행일이 아닙니다.
6. 앱에서 질문하고 출처가 내용을 뒷받침하는지 확인합니다.

일부 사이트는 HTML 구조가 바뀌거나 수집을 차단할 수 있습니다. 실패는 보고되고 앱 자료는 유지됩니다.
robots.txt와 이용 조건을 확인해 작은 범위로 수동 실행하세요. 사이트가 수집을 허용하지 않으면 적법하게 확보한 자료를 사람이 정리해 사용합니다.
수집은 20초 요청 제한, 2MB 응답 제한, 페이지 사이 0.3초 간격을 둡니다.
자동 승인과 정기 갱신은 없습니다. pending에는 저작권이 있는 본문이 포함될 수 있어 기본 Git 제외합니다.

JSON 공통 필드: id, domain, title, body, url, keywords, collectedAt, reviewedAt, reviewed, language, kind.
자료를 앱에 배포할 때 출처·이용 조건과 필요한 범위를 확인하세요.

## 실제 수집 확인

기본 수집 목록은 BGB §551·§568 및 AufenthG §16b·§18b입니다.
Make it in Germany는 자동 수집 요청에 브라우저 확인 화면을 반환합니다. 이를 우회하지 않습니다.
해당 사이트의 수집 예시는 portal-sources.json에 분리했고, 기본 실행은 공식 법령 사이트를 사용합니다.
기본 앱의 체류 예제는 사람이 확인한 포털 안내 요약을 유지합니다.
포털 수집 실패를 관찰하려면 `python3 scripts/scrape/collect.py --manifest scripts/scrape/portal-sources.json`을 실행하세요.

## 공식 페이지 수집 예시

스크롤링(화면을 아래로 이동)과 스크래핑(페이지 내용을 가져오기)은 다릅니다.
현재 예제는 조문이 HTML에 포함되어 있어 스크롤 없이 본문을 추출합니다.
아래 링크를 열어 제목 아래 번호가 붙은 문단을 확인하세요. `.jurAbsatz`는 Python이 해당 문단을 고르는 이름(selector)입니다.

| 분야 | 실제 수집 페이지                                                                                  | 가져올 부분                           | 검토 대기 파일                        |
| ---- | ------------------------------------------------------------------------------------------------- | ------------------------------------- | ------------------------------------- |
| 주거 | [BGB §551 — 보증금](https://www.gesetze-im-internet.de/bgb/__551.html)                            | (1)~(4)항 조문 본문                   | data/pending/housing-deposit.json     |
| 주거 | [BGB §568 — 종료 통지](https://www.gesetze-im-internet.de/bgb/__568.html)                         | (1)~(2)항 조문 본문                   | data/pending/housing-termination.json |
| 체류 | [AufenthG §16b — 유학](https://www.gesetze-im-internet.de/aufenthg_2004/__16b.html)               | 각 항의 본문; 첫 검토는 (1)·(2)항부터 | data/pending/visa-study-law.json      |
| 체류 | [AufenthG §18b — 학위 소지 전문인력](https://www.gesetze-im-internet.de/aufenthg_2004/__18b.html) | 제목 아래 조문 본문                   | data/pending/visa-work-law.json       |

§18b 한 조문은 취업 요건 전체를 설명하지 않습니다. 관련 규정과 공식 안내를 함께 검토해야 합니다.

### 한 페이지로 실습하기

프로젝트 폴더에서 Python 환경을 준비한 뒤 실행합니다.

```bash
# 보증금 페이지 한 건만 검토 대기 파일로 수집
python3 scripts/scrape/collect.py --manifest scripts/scrape/deposit-example.json

# 원문과 data/pending/housing-deposit.json을 직접 비교한 뒤에만 실행
python3 scripts/scrape/review.py --approve housing-deposit
```

수집만 하면 앱 자료는 바뀌지 않습니다. 승인하면 같은 ID의 기존 앱 자료가 교체됩니다.
전체 네 건은 `python3 scripts/scrape/collect.py`로 수집합니다.
현재 `.jurAbsatz` 본문을 선택하고 메뉴·스타일·스크립트는 제외합니다. 페이지 제목과 키워드는 수집 목록에서 지정합니다.

### 저장되는 JSON 구조

아래 body와 시각은 설명용 자리표시자입니다. 실제 파일은 원문 본문과 실제 수집 시각을 포함합니다.

```json
{
  "id": "housing-deposit",
  "domain": "housing",
  "title": "임대 보증금 — BGB §551",
  "url": "https://www.gesetze-im-internet.de/bgb/__551.html",
  "keywords": ["보증금", "분할", "납부"],
  "language": "de",
  "body": "여기에 추출한 독일어 본문이 저장됩니다.",
  "collectedAt": "<실제 수집 시각: UTC>",
  "reviewed": false,
  "reviewedAt": "",
  "kind": "scraped"
}
```

원문과 본문을 비교하고 검색 키워드를 보완한 뒤 승인합니다. 검토 대기 파일은 채팅에서 읽지 않습니다.
기본 체류 예제(포털 요약)와 수집할 체류 법령 원문은 서로 다른 자료입니다.

비개발자는 링크에서 본문을 확인하고 파일과 비교합니다. 개발 경험자는 수집 명령을 실행하고 본문 위치를 확인합니다.
