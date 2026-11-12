---
제목: "FE 설계"
유형: "위키"
설명: "GitHub Wiki 에서 자동 동기화된 문서입니다."
---

# FE 설계

[현재 구조와 기술](#doc=wiki/Home.md) · 영역별 설계: [PO/QA](#doc=wiki/구조-PO-QA.md) · **FE** · [BE](#doc=wiki/구조-BE.md) · [LLM](#doc=wiki/구조-LLM.md) · [데이터 수집](#doc=wiki/구조-데이터-수집.md) · [DevOps](#doc=wiki/구조-DevOps.md)

사용자가 직접 보고 조작하는 웹 화면을 개발하는 역할입니다. 현재 데모 화면은 `web/`에 있습니다.

## 1. 선택한 기술

웹 화면은 **Next.js**(React 기반 프레임워크)로 만듭니다.

- **React:** 버튼·입력창·채팅창처럼 화면 조각을 만들고 데이터에 따라 화면을 바꿈
- **Next.js:** 화면을 페이지로 연결하고 이동·자료 불러오기·서버 처리·배포 준비를 구성
- 이 프로젝트에서는 질문 입력, 답변·출처 표시 화면의 기반으로 사용

Next.js에 서버 기능이 있다고 해서 별도 백엔드 서버의 언어·프레임워크까지 정해진 것은 아닙니다. 자세한 설명: [docs/fe/tech-stack.md](https://github.com/ai-agent-study-group/german-legal-agent/blob/main/docs/fe/tech-stack.md)

## 2. 현재 들어 있는 주요 라이브러리

`web/package.json` 기준입니다. 새로 설치하자는 제안 목록이 아닙니다.

| 이름 · 패키지 | 하는 일 |
| --- | --- |
| Next.js · `next` | 페이지 구성·화면 실행·서버 기능 |
| React · `react`, `react-dom` | 화면 부품 생성·표시 |
| Tailwind CSS · `tailwindcss` | 작은 스타일 규칙 조합 |
| Base UI · `@base-ui/react` | 버튼·입력창 등 기본 동작 구성 |
| Lucide React · `lucide-react` | 아이콘 |

**shadcn/ui**는 부품 코드를 프로젝트에 가져와 직접 고치는 방식입니다. 설정은 `web/components.json`, 공통 부품 코드는 `web/components/ui/`에 있습니다.

## 3. 현재 화면 (web/app)

| 경로 | 화면 |
| --- | --- |
| `app/page.tsx` | 메인 |
| `app/housing/`, `app/visa/`, `app/study/` | 분야별 페이지 |
| `app/admin/` | 관리 화면 |
| `app/api/chat/route.ts` | 채팅 API(데모) |

## 4. 정할 것 (미정)

- 별도 FE 서버를 둘지, 정적 빌드로 BE 한 대에 붙일지
- 로직·모델 호출을 FE에 둘지 BE로 옮길지
- MVP 화면 범위: 질문 입력 → 답변·근거·출처(Citation) 표시 → 분야 선택
