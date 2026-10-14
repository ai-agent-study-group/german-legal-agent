# German Legal Information Agent

독일 법률 정보를 제공하는 agent를 함께 만드는 스터디입니다. 현재는 킥오프·기획 단계입니다.
**MVP 범위, 기술 스택, 최종 폴더 구조, 담당, 일정은 아직 미정입니다.**

## 문서와 회의

- [참여자 소개·역할 논의](docs/TEAM.md)
- [프로젝트 논의 항목](docs/PROJECT_PLAN.md)
- [구조 분리 후보·기술 선택 질문](docs/STRUCTURE.md)
- [Python·Next.js 백엔드 비교](docs/BACKEND_OPTIONS.md)
- [날짜별 회의 기록](docs/meetings/README.md) · [2026-10-15 킥오프](docs/meetings/2026-10-15.md)
- [GitHub에서 문서 작성·수정하기](docs/GITHUB_GUIDE.md)
- [기여 규칙](CONTRIBUTING.md)

문서는 저장소의 Markdown 파일로 관리할 수 있습니다. GitHub에서 파일을 새로 만들거나 수정하고
PR로 변경 내용을 검토하는 방법은 위 안내를 참고하세요.

## 문서 로컬 미리보기

프로젝트 루트에서 실행합니다. Node.js 20 이상이 필요합니다.

```bash
npm install
npm run docs:dev
```

[http://localhost:4173](http://localhost:4173)에서 확인합니다. 파일을 저장하면 자동으로 갱신되며 배포는 필요하지 않습니다.
이 npm 설정은 문서 미리보기용입니다. 서비스의 기술 스택·BE 언어는 아직 미정입니다.

## 기능 흐름 후보

공식 자료 수집 → 분류·검토·저장 → 질문에 맞는 검색 → agent 응답 → 웹에서 설명·출처 확인.
어떤 단계가 MVP에 필요하고 어떤 단위로 나눌지는 미팅에서 논의합니다.

## 역할별 폴더

역할별로 논의·작업을 시작할 공간을 만들었습니다. 새 폴더는 README만 있으며 실제 코드는 아직 `web/`에 있습니다.
폴더 이름은 초기 구분이고, 최종 패키지 구조나 별도 서버 채택을 뜻하지 않습니다.

| 경로 | 역할·현재 상태 | 담당 |
| --- | --- | --- |
| `web/` | 현재 화면·API·agent·수집을 포함하는 데모. 최종 역할은 논의 필요 | ? |
| [backend/](backend/README.md) | API·agent·검색·저장소 경계 논의. 언어 미정 | ? |
| [ingestion/](ingestion/README.md) | 자료 출처·수집·분류·검토 논의 | ? |
| [eval/](eval/README.md) | 질문·기대 근거·답변 평가 논의 | ? |
| [infra/](infra/README.md) | 개발 환경·자동 검사·배포·운영 논의 | ? |
| `docs/` | 기획·기술 선택·회의 기록 | ? |

`api/`, `agent/`, `search/`, `schemas/`, `tests/` 등 내부 모듈의 경로와 실행 단위는 기술 선택 후 논의합니다.
[Python 별도 서버와 Next.js 유지 비교](docs/BACKEND_OPTIONS.md)를 참고하세요.

## 현재 코드의 위치

이호수가 준비한 `web/`은 화면 외에 서버 API·agent 데모·자료·Python 수집 스크립트까지 들어 있는 실험용 기반입니다.
**현재 코드는 규칙 기반 데모이며 실제 AI 호출은 없습니다.** 기존 코드의 기술과 위치가 프로젝트 최종 선택을 뜻하지 않습니다.
현재 위치와 분리 후보의 대응은 [구조 문서](docs/STRUCTURE.md)에 정리되어 있습니다.

현재 데모만 실행하려면 [web/README.md](web/README.md)를 참고하세요.
팀 전체의 공통 실행 명령은 기술과 구조를 정한 뒤 작성할 예정입니다.
