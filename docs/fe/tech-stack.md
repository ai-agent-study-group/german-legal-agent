---
제목: "프론트엔드 기술 안내"
유형: "기술 안내"
설명: "프론트엔드에 사용하는 Next.js의 개념과 선택 배경, 현재 라이브러리의 역할을 설명합니다."
관련문서: []
---

# 프론트엔드 기술 안내

## 선택한 기술

웹 화면을 만드는 프론트엔드(Front End, FE)는 **Next.js**를 사용합니다.

## Next.js는 무엇인가요?

**Next.js는 React로 웹 서비스를 만들 때 필요한 구조와 기능을 제공하는 프레임워크입니다.**
프레임워크는 개발할 때 반복해서 만드는 뼈대와 기본 도구를 묶어 제공하는 기반을 말합니다.

- **React**는 버튼·입력창·채팅창처럼 화면의 작은 조각을 만들고, 데이터에 따라 화면을 바꾸는 도구입니다.
- **Next.js**는 이 화면들을 페이지로 연결하고, 페이지 이동·자료 불러오기·서버에서의 처리·배포 준비를 구성할 수 있게 돕습니다.
- 이 프로젝트에서는 질문 입력, 답변과 출처 표시 같은 사용자 화면을 만드는 기반으로 사용합니다.

이 설명은 [Next.js 공식 소개](https://nextjs.org/learn/react-foundations/what-is-react-and-nextjs)를 바탕으로 정리했습니다.

## 왜 이 프로젝트에서 사용하나요?

기존 화면 기반을 활용하면서 채팅·자료 확인 화면을 공통 구조로 만들 수 있습니다.
화면을 작은 부품으로 나누고 여러 페이지에서 재사용하기에도 적합합니다.
이는 현재 코드와 프로젝트 상황을 바탕으로 정리한 설명이며, 성능 비교 실험의 결과를 뜻하지는 않습니다.

Next.js에 서버 기능이 있다고 해서 별도 백엔드 서버의 언어·프레임워크까지 정해진 것은 아닙니다.

## 자주 나오는 말

| 용어 · 전체 이름 | 쉬운 설명 | 현재 파일 예시 |
| --- | --- | --- |
| Component (컴포넌트) | 여러 곳에서 다시 쓸 수 있는 화면 부품 | 버튼, 답변 카드, 채팅 입력창 |
| App Router (앱 라우터) | 폴더와 파일로 페이지 주소를 구성하는 Next.js 방식 | `web/app/` |
| Page (페이지) | 특정 주소를 열었을 때 보이는 화면 | `app/page.tsx` |
| Layout (레이아웃) | 여러 페이지가 공유하는 바깥 화면 구조 | `app/layout.tsx` |
| Client Component (클라이언트 컴포넌트) | 클릭·입력처럼 브라우저에서의 상호작용을 담당하는 화면 부품 | 채팅 입력·초기화 기능 |
| Server Component (서버 컴포넌트) | 서버 쪽에서 자료를 읽거나 화면을 준비할 수 있는 부품 | 서버에서 준비하는 페이지 부분 |
| TypeScript | JavaScript에 자료의 종류를 검사하는 기능을 더한 개발 언어 | `.ts`, `.tsx` 파일 |
| User Interface (사용자 인터페이스, UI) | 사용자가 보고 조작하는 버튼·입력창·목록 등 | 화면 전체의 표시와 조작 요소 |
| Cascading Style Sheets (종속형 스타일 시트, CSS) | 글자·색·간격·화면 배치를 정하는 규칙 | `app/globals.css` |

페이지 주소와 공통 화면의 개념은 [페이지·레이아웃 설명](https://nextjs.org/docs/app/getting-started/layouts-and-pages),
서버와 브라우저 역할의 구분은 [서버·클라이언트 컴포넌트 설명](https://nextjs.org/docs/app/getting-started/server-and-client-components)을 참고하세요.

## 현재 프로젝트에 들어 있는 라이브러리와 도구

라이브러리는 필요한 기능을 가져다 쓸 수 있는 코드 묶음입니다.
아래는 현재 `web/package.json`과 화면 코드를 확인해 정리한 목록입니다. 새로 설치하자는 제안 목록이 아닙니다.

### 화면과 스타일

| 이름 · 패키지 | 하는 일 | 쉬운 예시 |
| --- | --- | --- |
| Next.js · `next` | 페이지 구성·화면 실행·서버 기능을 제공하는 기반 | 주소별 화면과 자료 연결 |
| React · `react`, `react-dom` | 화면 부품을 만들고 브라우저에 표시 | 질문을 입력하면 화면이 갱신됨 |
| Tailwind CSS · `tailwindcss` | 작은 스타일 규칙을 조합해 디자인 | 글자 크기·여백·색·모바일 배치 |
| Base UI · `@base-ui/react` | 버튼·입력창 등의 기본 동작을 구성하는 화면 부품 | 현재 공통 버튼과 입력창의 기반 |
| Lucide React · `lucide-react` | React 화면에서 사용하는 아이콘 | 화살표·책·검색 아이콘 |
| `class-variance-authority` | 같은 부품의 크기·모양별 스타일 정리 | 기본 버튼·테두리 버튼·작은 버튼 |
| `cn` | 여러 스타일 클래스 이름을 조합 | 공통 스타일과 추가 스타일 결합 |
| `tw-animate-css` | 스타일 기반의 애니메이션 규칙 제공 | 화면 요소가 나타나는 효과 |

**shadcn/ui**는 화면 부품 코드를 프로젝트에 가져와 직접 고치는 방식입니다.
현재 `web/components.json`에 관련 설정이 있고, 공통 부품 코드는 `web/components/ui/`에 있습니다.
하나의 완제품 패키지를 설치해 쓰는 일반 라이브러리와 관리 방식이 다릅니다. [shadcn/ui 공식 설명](https://ui.shadcn.com/docs)

### 개발과 확인 도구

| 이름 | 하는 일 |
| --- | --- |
| TypeScript · `typescript` | 자료의 종류가 맞는지 검사하며 개발 |
| ESLint · `eslint`, `eslint-config-next` | 코드 스타일과 흔한 실수를 자동 검사하는 린트 도구 |
| `tsx` | TypeScript로 작성된 테스트 등을 실행 |
| `server-only` | 서버 전용 코드를 브라우저 코드로 가져오는 실수를 방지 |
| `@types/node`, `@types/react`, `@types/react-dom` | 개발 도구가 Node.js·React의 자료 종류를 이해하도록 돕는 정의 |
| `@tailwindcss/postcss` | 화면 스타일을 처리하는 과정에서 Tailwind CSS를 연결 |

**버전 번호는 이 문서에 반복해서 적지 않습니다.** 선언된 의존성은 [web/package.json](https://github.com/ai-agent-study-group/german-legal-agent/blob/main/web/package.json),
설치 시 재현할 구체 버전은 [web/package-lock.json](https://github.com/ai-agent-study-group/german-legal-agent/blob/main/web/package-lock.json)을 기준으로 확인합니다.

## 공식 참고 자료

- [Next.js 시작하기](https://nextjs.org/docs/app/getting-started)
- [React 소개](https://react.dev/learn)
- [Tailwind CSS 스타일 작성](https://tailwindcss.com/docs/styling-with-utility-classes)
- [Base UI 소개](https://base-ui.com/react/overview/quick-start)
- [Lucide React 아이콘](https://lucide.dev/guide/react)
