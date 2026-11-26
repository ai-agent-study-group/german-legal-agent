---
제목: "DevOps 설계"
유형: "위키"
설명: "GitHub Wiki 에서 자동 동기화된 문서입니다."
---

# DevOps 설계

[현재 구조와 기술](#doc=wiki/Home.md) · 영역별 설계: [PO/QA](#doc=wiki/구조-PO-QA.md) · [FE](#doc=wiki/구조-FE.md) · [BE](#doc=wiki/구조-BE.md) · [LLM](#doc=wiki/구조-LLM.md) · [데이터 수집](#doc=wiki/구조-데이터-수집.md) · **DevOps**

프로그램 실행에 필요한 기반 환경과 배포·자동 검사·운영을 관리하는 역할입니다.

## 1. 자동 검사(CI)

변경 검토 요청(PR)을 올리거나 `main`에 변경이 반영되면 GitHub Actions가 자동으로 검사합니다.
설정 파일: [`.github/workflows/ci.yml`](https://github.com/ai-agent-study-group/german-legal-agent/blob/main/.github/workflows/ci.yml)

| 검사 | 확인 내용 |
| --- | --- |
| 백엔드 | Python 3.12 환경에서 `uv sync --locked`로 의존성을 설치하고 `uv run --locked pytest`로 API 테스트 실행 |
| 웹 | `web/`의 lint, 타입 검사, 테스트 및 프로덕션 빌드 |
| 자료 수집 | `web/scripts/scrape/`의 Python 테스트 |
| 종합 검사 | `all-checks`: 백엔드·웹·자료 수집 검사가 모두 성공해야 통과 |

현재 CI는 별도 `agent/`와 `ingestion/`의 테스트는 실행하지 않습니다.

코드 변경의 병합 조건은 CI 통과와 리뷰입니다. 문서만 변경한 경우에는
[기여 규칙](https://github.com/ai-agent-study-group/german-legal-agent/blob/main/CONTRIBUTING.md)을 따릅니다.

로컬 검사 방법은 [백엔드 README](https://github.com/ai-agent-study-group/german-legal-agent/blob/main/backend/README.md)와
[웹 README](https://github.com/ai-agent-study-group/german-legal-agent/blob/main/web/README.md)를 참고하세요.

> 저장소 관리자는 `main`의 브랜치 보호 설정에 `all-checks`가 필수 검사로 지정되어 있는지,
> 그리고 문서 직접 저장 규칙과 충돌하지 않는지 별도로 확인해야 합니다.

## 2. 문서 사이트

- `docs/`를 GitHub Pages로 배포. 설정: `Deploy from a branch → main → /docs`
- 화면·메뉴·스타일은 `docs/index.html` 하나로 구성
- 로컬 미리보기: 루트에서 `npm install && npm run docs:dev` → http://localhost:4173

## 3. 정할 것 (미정)

- 서비스 배포 대상·방식 (FE 서버 유무, BE 언어에 따라 달라짐)
- 개발 환경 공유 여부, API 예산·키 관리
- 커밋하지 않을 것: 키(`.env`)·실행 결과·개인정보. `.gitignore`로 막고, 실수로 올렸으면 키를 즉시 폐기
