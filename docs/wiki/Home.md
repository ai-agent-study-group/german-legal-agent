---
제목: "현재 구조와 기술"
유형: "위키"
설명: "GitHub Wiki 에서 자동 동기화된 문서입니다."
---

# 현재 구조와 기술

영역별 설계: [BE](#doc=wiki/구조-BE.md) · [LLM](#doc=wiki/구조-LLM.md) · [FE](#doc=wiki/구조-FE.md) · [데이터 수집](#doc=wiki/구조-데이터-수집.md) · [DevOps](#doc=wiki/구조-DevOps.md) · [PO/QA](#doc=wiki/구조-PO-QA.md)

독일 법률 정보를 제공하는 agent를 함께 만드는 스터디입니다. 현재는 **킥오프·기획 단계**입니다. 최종 폴더 구조·언어·서버 구성은 아직 정해지지 않았고, 아래는 현재 데모의 위치와 분리 후보를 정리한 참고 자료입니다.

## 전체 구조

1. **기능 흐름 후보:** 공식 자료 수집 → 분류·검토·저장 → 질문에 맞는 검색 → agent 응답 → 웹에서 설명·출처 확인
2. **현재 데모:** 사용자 화면은 `web/`(Next.js)에 있음. 서버(BE)·수집(ingestion)·평가(eval)·인프라(infra)는 README만 있는 논의용 폴더
3. **아직 정하지 않은 것:** Python 별도 BE를 둘지 Next.js 서버를 유지할지, 역할별 폴더 내부를 어떻게 나눌지, 데이터 저장소·모델 선택

한 저장소 안에서 폴더를 나누는 것과 여러 서버로 배포하는 것은 별개의 결정입니다. 먼저 무엇을 어느 역할로 나눌지 논의한 뒤 언어·실행 방식에 맞춰 폴더·패키지 구조를 정합니다.

<a id="scope"></a>

## 1. 첫 구현 범위 (MVP)

- **법률 영역:** 독일 임대차법(**Mietrecht**)을 우선 대상으로 함. 세입자(Mieter)·임대인(Vermieter) 간 주거용 임대차 분쟁 ([데이터 수집](#doc=wiki/구조-데이터-수집.md) 참고)
- **대표 흐름:** 질문 입력 → 관련 법률·판례 검색(RAG) → agent가 근거·출처와 함께 답변 → 웹에서 설명·Citation 확인
- **미정:** MVP에 필요한 기능 단위, 첫 분야의 대표 질문, 꼭 필요한 기능과 보류할 것 → 미팅에서 논의
- **제외·추후:** Gewerbemietrecht, 형사 사건, 독일 전 지역 전체 판례 등은 추후 검토

<a id="collaboration"></a>

## 2. 협업 방식

**정기 모임: 매주 목요일 18:00 (Europe/Berlin).** Discord에서 진행합니다.

- **문서:** 저장소의 Markdown 파일로 관리. Markdown 문서·문서용 이미지만 바꾸면 변경 검토 요청(PR) 없이 `main`에 직접 저장 가능
- **코드:** 코드·사이트 화면·설정 변경은 [기여 규칙](https://github.com/ai-agent-study-group/german-legal-agent/blob/main/CONTRIBUTING.md)의 변경 검토 절차(브랜치 → PR → 자동 검사 → 병합)를 따름
- **자동 검사(CI):** Lint · Typecheck · Test. 설정은 [`.github/workflows/ci.yml`](https://github.com/ai-agent-study-group/german-legal-agent/blob/main/.github/workflows/ci.yml)

### 진행 방식

1. 역할별로 필요한 작업을 각 직군 폴더·회의에서 정리
2. MVP 범위와 역할 경계, 함께 수정할 데이터 형식을 논의해 구체화
3. 그 경계에 맞는 언어·프레임워크·구조를 정하고 작업 시작

<a id="roles"></a>

## 3. 역할 분담

주 담당은 아래와 같고, 누구나 관심 있는 분야 채널에 참여해 함께 작업할 수 있습니다. 자세한 내용은 [역할](#doc=wiki/역할.md) 참고.

| 역할 | 주 담당 | 설계 문서 |
| --- | --- | --- |
| 기획·제품 책임자(PO) | charlotte · 희정 | [구조 PO/QA](#doc=wiki/구조-PO-QA.md) |
| 프론트엔드(FE) | 호수 | [구조 FE](#doc=wiki/구조-FE.md) |
| 백엔드(BE) | 지연 | [구조 BE](#doc=wiki/구조-BE.md) |
| 인공지능·언어 모델(AI/LLM) | 승재 | [구조 LLM](#doc=wiki/구조-LLM.md) |
| 데이터 수집 | 성환 | [구조 데이터 수집](#doc=wiki/구조-데이터-수집.md) |
| 인프라·개발 운영(DevOps) | 해윤 | [구조 DevOps](#doc=wiki/구조-DevOps.md) |

## 참고 자료

- [README.md](https://github.com/ai-agent-study-group/german-legal-agent/blob/main/README.md): 스터디 목표·모임 일정·현재 개발 상태
- [docs/STRUCTURE.md](https://github.com/ai-agent-study-group/german-legal-agent/blob/main/docs/STRUCTURE.md): 현재 코드 구조와 연결 지점
- [docs/TEAM.md](https://github.com/ai-agent-study-group/german-legal-agent/blob/main/docs/TEAM.md): 역할·팀원
- [CONTRIBUTING.md](https://github.com/ai-agent-study-group/german-legal-agent/blob/main/CONTRIBUTING.md): 브랜치·PR 규칙
- [문서 사이트 안내(GITHUB_GUIDE)](https://github.com/ai-agent-study-group/german-legal-agent/blob/main/docs/GITHUB_GUIDE.md): 누구나 문서 작성·수정하기
