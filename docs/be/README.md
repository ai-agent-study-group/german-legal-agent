---
제목: "BE 설계"
유형: "위키"
설명: "GitHub Wiki 에서 자동 동기화된 문서입니다."
관련문서: []
---

# BE 설계

[현재 구조와 기술](#doc=STRUCTURE.md) · 영역별 설계: [PO/QA](#doc=po/README.md) · [FE](#doc=fe/README.md) · **BE** · [LLM](#doc=ai-llm/README.md) · [데이터 수집](#doc=data/README.md) · [DevOps](#doc=infra/README.md)

화면 뒤에서 요청을 처리하고 자료를 저장·조회하는 서버를 개발하는 역할입니다. **언어·프레임워크는 미정**입니다.

## 1. 현재 상태

- `backend/`는 README만 있는 논의용 폴더입니다. 실제 코드는 아직 `web/`에 있습니다.
- Python 별도 BE를 둘지, Next.js 서버를 유지할지 미정 ([docs/STRUCTURE.md](https://github.com/ai-agent-study-group/german-legal-agent/blob/main/docs/STRUCTURE.md))

## 2. 현재 데모 위치와 분리 후보

| 기능 | 현재 데모 위치 | 분리 경로 후보 |
| --- | --- | --- |
| 사용자 화면 | `web/app/`, `web/components/`, `web/hooks/` | `web/` |
| 공통 기획·회의 문서 | `docs/` | `docs/` |

자료 접근 코드는 단순 파일 복사로 옮길 수 있다고 가정하지 않습니다. 서버 코드·파일 경로·데이터 형식은 영역을 나눌 때 함께 확인합니다.

## 3. 연결 지점에서 정할 것

| 연결 | 질문 | 합의 |
| --- | --- | --- |
| 웹 ↔ API | 요청·응답 형식, 오류, 출처·실행 기록을 어떻게 전달할까? | ? |
| API ↔ agent | 같은 프로세스의 함수 호출인가, 별도 서비스인가? | ? |
| 수집 ↔ 저장 | 자료 ID·분류·날짜·검토 상태를 어떤 형식으로 남길까? | ? |
| 검색 ↔ agent | 검색 결과와 본문을 어떤 도구·형식으로 전달할까? | ? |
| 구현 ↔ 평가 | 공통 질문과 실행 결과를 어디에 어떤 형식으로 기록할까? | ? |

## 4. 저장소(DB) 논의 입력

[데이터 수집](#doc=data/README.md)의 법률·판례 Schema가 저장소 구조·검색(RAG/Vector Search) 요구의 입력입니다. 데이터 담당·LLM 담당과 함께 DB 구조와 Retrieval 요구사항을 검토합니다.
