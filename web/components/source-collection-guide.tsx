import sources from "@/scripts/scrape/sources.json";
import { ExternalLink } from "lucide-react";

const notes: Record<
  string,
  { purpose: string; section: string; question: string }
> = {
  "housing-deposit": {
    purpose: "보증금",
    section: "제목 아래 (1)~(4)항: 보증금 상한·분할 납부·보관 관련 본문",
    question: "보증금은 나눠 낼 수 있나요?",
  },
  "housing-termination": {
    purpose: "계약 종료 통지",
    section: "제목 아래 (1)~(2)항: 통지 형식과 이의제기 안내 관련 본문",
    question: "임대계약 종료 통지는 어떤 형식인가요?",
  },
  "visa-study-law": {
    purpose: "유학 목적 체류",
    section:
      "Studium 제목 아래 각 항의 본문. 먼저 (1)항의 학업 목적과 (2)항의 기간·연장 부분을 살펴봅니다.",
    question: "유학 체류 연장에 관한 자료는 어디서 보나요?",
  },
  "visa-work-law": {
    purpose: "대학 학위 소지 전문인력",
    section:
      "Fachkräfte mit akademischer Ausbildung 제목 아래 본문. 이 한 조문만으로 모든 취업 요건을 판단하지 않습니다.",
    question: "학위 소지 전문인력의 취업 체류 근거를 찾아주세요.",
  },
};
const sample = {
  id: sources[0].id,
  domain: sources[0].domain,
  title: sources[0].title,
  url: sources[0].url,
  keywords: sources[0].keywords.slice(0, 3),
  language: "de",
  body: "여기에 원문에서 추출한 독일어 본문이 저장됩니다.",
  collectedAt: "<실제 수집 시각: UTC>",
  reviewed: false,
  reviewedAt: "",
  kind: "scraped",
};
export function SourceCollectionGuide() {
  return (
    <section
      id="collection-examples"
      aria-labelledby="collection-title"
      className="mt-10 space-y-5"
    >
      <div>
        <p className="eyebrow mb-3">DATA COLLECTION EXAMPLES</p>
        <h2 id="collection-title" className="section-title">
          어느 페이지에서 무엇을 가져오나요?
        </h2>
        <p className="mt-4 text-sm leading-7 text-slate-600">
          아래 링크로 실제 공식 페이지를 열어보세요. Python은 페이지를
          다운로드하고 조문 본문만 골라 파일로 저장합니다. 이번 예제에서는
          마우스로 스크롤하거나 화면을 촬영할 필요가 없습니다.
        </p>
      </div>
      <div className="grid gap-4 md:grid-cols-2">
        {sources.map((source) => {
          const note = notes[source.id] ?? {
            purpose: "추가 자료",
            section:
              "수집 목록에 지정한 본문 위치를 확인하고 필요한 문단을 검토합니다.",
            question: "이 자료로 답할 수 있는 질문을 팀에서 작성해보세요.",
          };
          return (
            <article key={source.id} className="soft-card p-6">
              <p className="eyebrow text-blue-600">
                {source.domain === "housing" ? "주거·임대" : "체류·비자"} ·{" "}
                {note.purpose}
              </p>
              <h3 className="mt-3 text-lg font-semibold">{source.title}</h3>
              <a
                href={source.url}
                target="_blank"
                rel="noopener noreferrer"
                className="mt-3 inline-flex items-center gap-2 text-sm font-medium text-blue-700"
              >
                공식 페이지 열기
                <ExternalLink size={14} />
              </a>
              <p className="mt-2 break-all text-xs leading-6 text-slate-600">
                {source.url}
              </p>
              <dl className="mt-4 space-y-3 text-sm leading-7">
                <div>
                  <dt className="font-medium">가져올 부분</dt>
                  <dd className="text-slate-600">{note.section}</dd>
                </div>
                <div>
                  <dt className="font-medium">연결할 질문 예시</dt>
                  <dd className="text-slate-600">{note.question}</dd>
                </div>
                <div>
                  <dt className="font-medium">저장할 파일</dt>
                  <dd className="break-all font-mono text-xs text-slate-600">
                    data/pending/{source.id}.json
                  </dd>
                </div>
              </dl>
              <details className="mt-4 border-t border-slate-100 pt-3">
                <summary className="cursor-pointer text-xs font-medium text-slate-600">
                  개발자용: 본문 위치와 설정
                </summary>
                <p className="mt-3 text-xs leading-6 text-slate-600">
                  본문 위치(selector)는 <code>{source.selector}</code>입니다.
                  웹페이지 안에서 조문 문단에 붙은 이름을 이용해 해당 부분만
                  선택합니다. 수집 대상은 scripts/scrape/sources.json에서
                  지정합니다.
                </p>
              </details>
            </article>
          );
        })}
      </div>
      <article className="soft-card p-6">
        <h3 className="text-lg font-semibold">
          첫 실습: 보증금 페이지 한 개부터
        </h3>
        <ol className="mt-4 list-decimal space-y-3 pl-5 text-sm leading-7 text-slate-600">
          <li>
            위의 BGB §551 링크를 열고 제목 아래 번호가 붙은 문단을 찾아봅니다.
          </li>
          <li>Python 가상환경과 의존성을 준비한 뒤 아래 명령을 실행합니다.</li>
          <li>data/pending/housing-deposit.json을 열고 원문과 비교합니다.</li>
          <li>
            메뉴나 누락이 없는지 확인하고, 필요하면 한국어 요약과 검색 키워드를
            보완합니다.
          </li>
          <li>
            사람이 검토를 마친 뒤 승인 명령을 실행합니다. 이후 주거 채팅에서
            검색·출처를 확인합니다.
          </li>
        </ol>
        <pre
          tabIndex={0}
          role="region"
          aria-label="한 페이지 수집과 승인 명령"
          className="mt-4 overflow-x-auto rounded-xl bg-slate-900 p-4 text-xs leading-7 text-slate-100"
        >
          <code>
            {
              "# 1. 보증금 페이지 한 건 수집\npython3 scripts/scrape/collect.py --manifest scripts/scrape/deposit-example.json\n\n# 2. 생성 파일을 직접 검토한 뒤에만 승인\npython3 scripts/scrape/review.py --approve housing-deposit"
            }
          </code>
        </pre>
        <p className="mt-3 text-xs leading-6 text-slate-600">
          명령은 개발자가 프로젝트 폴더에서 실행합니다. 비개발자는 원문과 파일을
          비교하고 검색 키워드를 제안합니다. 승인하면 같은 ID의 기존 앱 자료가
          교체됩니다.
        </p>
      </article>
      <article className="soft-card p-6">
        <h3 className="text-lg font-semibold">
          수집 후 파일은 이렇게 생깁니다
        </h3>
        <p className="mt-3 text-sm leading-7 text-slate-600">
          아래는 구조를 설명하는 예시입니다. 실제 파일에는 독일어 원문과 실제
          수집 시각이 들어갑니다. 아직 검토하지 않았으므로 reviewed는 false이고,
          채팅에서 읽지 않습니다.
        </p>
        <pre
          tabIndex={0}
          role="region"
          aria-label="수집 결과 JSON 예시"
          className="mt-4 overflow-x-auto rounded-xl bg-slate-50 p-4 text-xs leading-6 text-slate-700"
        >
          <code>{JSON.stringify(sample, null, 2)}</code>
        </pre>
        <p className="mt-4 text-sm leading-7 text-slate-600">
          공식 페이지 → Python 수집 → 검토 대기 파일 → 사람의 검토·승인 →
          data/housing.json 또는 data/visa.json → 채팅의 검색·읽기 도구
        </p>
        <p className="mt-3 text-xs leading-6 text-slate-600">
          기본 앱의 체류 자료는 사람이 작성한 포털 안내 요약이고, 위 수집 예제는
          체류 법령 원문입니다. 수집했다고 자동으로 앱 자료에 추가되지는
          않습니다.
        </p>
      </article>
      <p className="rounded-xl bg-amber-50 p-4 text-sm leading-7 text-amber-900">
        Make it in Germany 포털은 앞선 실행에서 자동 수집 요청에 브라우저 확인
        화면을 반환했습니다. 우회하지 않고 기본 실습은 공식 법령 사이트로
        진행합니다. 나중에 스크롤해야 새 내용이 나타나는 사이트를 다룬다면
        별도의 브라우저 수집 방식을 검토합니다.
      </p>
    </section>
  );
}
