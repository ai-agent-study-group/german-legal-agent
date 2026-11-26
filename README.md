---
제목: "German Legal Information Agent"
유형: "프로젝트 안내"
설명: "스터디의 목표와 모임 일정, 문서 위치 및 현재 개발 상태를 처음 확인할 때 읽습니다."
관련문서: []
---

# German Legal Information Agent

독일 법률 정보를 제공하는 agent를 함께 만드는 스터디입니다. 현재는 킥오프·기획 단계입니다.
**담당은 [프로젝트 역할](docs/TEAM.md), 기술 선택과 작업 기록은 각 직군 폴더에서 관리합니다.**

**정기 모임: 매주 목요일 18:00 (Europe/Berlin).**

## 문서와 회의

- [프로젝트 역할](docs/TEAM.md)
- [구조 분리 후보·기술 선택 질문](docs/STRUCTURE.md)
- [날짜별 회의 기록](docs/meetings/README.md)
- [GitHub에서 문서 작성·수정하기](docs/GITHUB_GUIDE.md)
- [기여 규칙](CONTRIBUTING.md)

문서는 저장소의 Markdown 파일로 관리할 수 있습니다. GitHub에서 파일을 새로 만들거나 수정하고
**Markdown 문서와 문서용 이미지 변경은 변경 검토 요청(Pull Request, PR)이 필수가 아닙니다.**
변경 검토 요청은 다른 사람에게 내용을 확인받고 기준이 되는 기본 브랜치에 합쳐달라고 요청하는 절차입니다. GitHub에서 main에 직접 저장할 수 있습니다.
코드·사이트 화면·설정 변경에는 변경 검토 요청을 사용합니다.

## 문서 로컬 미리보기

프로젝트 루트에서 실행합니다. Node.js 20 이상이 필요합니다.

```bash
npm install
npm run docs:dev
```

[http://localhost:4173](http://localhost:4173)에서 확인합니다. 파일을 저장하면 자동으로 갱신되며 배포는 필요하지 않습니다.
이 npm 설정은 문서 미리보기용입니다. 서비스 개발에 사용하는 기술은 각 직군 문서에서 확인합니다.

## 자동 검사(Continuous Integration, CI)

변경 검토 요청을 올리면 GitHub가 자동으로 아래 검사를 실행합니다. 설정은 [`.github/workflows/ci.yml`](.github/workflows/ci.yml)에 있습니다.

| 검사 | 무엇을 보나 |
| --- | --- |
| 백엔드 | `backend/`의 Python 3.12 의존성을 `uv sync --locked`로 설치하고 API 테스트 실행 |
| 웹 | `web/`의 lint·타입 검사·테스트와 프로덕션 빌드 |
| 자료 수집 | `web/scripts/scrape/`의 Python 테스트 |
| 종합 검사 | `all-checks`는 위 세 작업이 모두 성공해야 통과 |

**비개발자 안내:** 문서만 바꾸면 변경 검토 요청 없이 직접 저장할 수 있습니다. 현재 자동 검사는 main 반영 시에도 실행될 수 있으며,
결과는 GitHub Actions에서 확인할 수 있습니다. 코드 변경 검토에서는 검사 통과가 병합 조건입니다. 자세한 규칙은 [기여 규칙](CONTRIBUTING.md)을 참고하세요.

로컬 검사 명령은 [백엔드 안내](backend/README.md)와 [웹 안내](web/README.md)의 검증 항목을 참고하세요. 현재 CI는 별도 `agent/`와 `ingestion/`의 테스트를 실행하지 않습니다.

## 기능 흐름 후보

공식 자료 수집 → 분류·검토·저장 → 질문에 맞는 검색 → agent 응답 → 웹에서 설명·출처 확인.
어떤 단계가 최소 기능 제품(Minimum Viable Product, MVP)에 필요하고 어떤 단위로 나눌지는 미팅에서 논의합니다.

## 역할별 폴더

역할별로 논의·작업을 시작할 공간을 만들었습니다. 현재 `web/` 데모와 별도의 Python 백엔드·agent 및 자료 수집 코드가 있습니다.
폴더 이름은 초기 구분이고, 최종 패키지 구조나 별도 서버 채택을 뜻하지 않습니다.

| 경로 | 역할·현재 상태 |
| --- | --- |
| `web/` | 프론트엔드 화면과 현재 데모 |
| [backend/](backend/README.md) | FastAPI 백엔드와 API 테스트 |
| [ingestion/](ingestion/README.md) | 자료 출처·수집·분류·검토 |
| [eval/](eval/README.md) | 제품 기획의 사용자·평가 관점 참고 |
| [infra/](infra/README.md) | 개발 환경·자동 검사·배포·운영 |
| `docs/` | 기획·기술 선택·회의 기록 |

`api/`, `agent/`, `search/`, `schemas/`, `tests/` 등 내부 모듈의 경로와 실행 단위는 기술 선택 후 논의합니다.


## 직군별 문서 작성

[제품 기획](docs/po/README.md) · [화면 개발](docs/fe/README.md) · [서버 개발](docs/be/README.md) · [인공지능](docs/ai-llm/README.md) · [자료 수집](docs/data/README.md) · [개발 운영](docs/infra/README.md)

각 폴더에 메모·작업 내용·공유 자료를 Markdown으로 추가합니다. 작성법은 [쉬운 안내](docs/GITHUB_GUIDE.md)를 참고하세요.
