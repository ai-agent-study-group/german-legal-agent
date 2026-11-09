---
제목: "DevOps 설계"
유형: "위키"
설명: "GitHub Wiki 에서 자동 동기화된 문서입니다."
관련문서: []
---

# DevOps 설계

[현재 구조와 기술](#doc=STRUCTURE.md) · 영역별 설계: [PO/QA](#doc=po/README.md) · [FE](#doc=fe/README.md) · [BE](#doc=be/README.md) · [LLM](#doc=ai-llm/README.md) · [데이터 수집](#doc=data/README.md) · **DevOps**

프로그램 실행에 필요한 기반 환경과 배포·자동 검사·운영을 관리하는 역할입니다.

## 1. 자동 검사(CI)

변경 검토 요청을 올리면 GitHub가 자동으로 검사합니다. 설정: [`.github/workflows/ci.yml`](https://github.com/ai-agent-study-group/german-legal-agent/blob/main/.github/workflows/ci.yml)

| 검사 | 무엇을 보나 |
| --- | --- |
| Lint | 코드 스타일·흔한 실수 (안 쓰는 변수, 들여쓰기·따옴표 규칙) |
| Typecheck | 타입 오류 (숫자 자리에 문자열 등) |
| Test | 코드가 의도대로 동작하는지 (`web/`의 agent·수집 로직) |

문서만 바꾸면 변경 검토 요청 없이 직접 저장할 수 있습니다. 코드 변경에서는 검사 통과가 병합 조건입니다.

## 2. 문서 사이트

- `docs/`를 GitHub Pages로 배포. 설정: `Deploy from a branch → main → /docs`
- 화면·메뉴·스타일은 `docs/index.html` 하나로 구성
- 로컬 미리보기: 루트에서 `npm install && npm run docs:dev` → http://localhost:4173

## 3. 정할 것 (미정)

- 서비스 배포 대상·방식 (FE 서버 유무, BE 언어에 따라 달라짐)
- 개발 환경 공유 여부, API 예산·키 관리
- 커밋하지 않을 것: 키(`.env`)·실행 결과·개인정보. `.gitignore`로 막고, 실수로 올렸으면 키를 즉시 폐기
