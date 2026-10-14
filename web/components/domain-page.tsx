import Link from "next/link";
import { ArrowLeft, FlaskConical, FolderOpen, ListChecks } from "lucide-react";
import { ChatPanel } from "./chat-panel";
import { domains } from "@/lib/agents/domains";
import type { Domain } from "@/lib/types";
export function DomainPage({ domain }: { domain: Domain }) {
  const c = domains[domain];
  const chat = <ChatPanel key={domain} domain={domain} />;
  const aside = (
    <aside className="space-y-4">
      {domain === "visa" && (
        <section className="rounded-2xl border border-emerald-200 bg-emerald-50/70 p-5">
          <ListChecks className="text-emerald-600" size={20} />
          <h2 className="mt-3 text-sm font-semibold">준비 단계</h2>
          <ol className="mt-3 space-y-2">
            {domains.visa.steps.map((step, i) => (
              <li key={i} className="flex gap-2 text-xs leading-6 text-slate-600">
                <span className="font-semibold text-emerald-600">{i + 1}.</span>
                {step}
              </li>
            ))}
          </ol>
        </section>
      )}
      <section className="rounded-2xl border border-amber-200 bg-amber-50/70 p-5">
        <FlaskConical className="text-amber-600" size={20} />
        <h2 className="mt-3 text-sm font-semibold">학습용 데모입니다</h2>
        <p className="mt-2 text-xs leading-6 text-slate-600">
          실제 AI 모델은 연결되지 않았습니다. 정해진 규칙으로 검색·읽기를
          실행하고 준비된 설명을 보여줍니다.
        </p>
      </section>
      {c.sidebar.map((item) => (
        <section key={item.title} className="soft-card p-5">
          <FolderOpen size={20} className="text-slate-400" />
          <h2 className="mt-3 text-sm font-semibold">{item.title}</h2>
          <p className="mt-2 text-xs leading-6 text-slate-500">{item.body}</p>
        </section>
      ))}
    </aside>
  );
  const stepsFirst = c.layout === "steps-first";
  return (
    <main id="main" className="page-shell py-9 sm:py-12">
      <Link
        href="/"
        className="inline-flex items-center gap-2 text-xs text-slate-500"
      >
        <ArrowLeft size={13} />
        주제 선택으로
      </Link>
      <div className="mt-7 mb-8">
        <p className="eyebrow mb-3">{c.eyebrow}</p>
        <h1 className="text-3xl font-semibold tracking-tight sm:text-4xl">
          {c.title} 안내
        </h1>
        <p className="mt-3 text-sm leading-7 text-slate-500">{c.description}</p>
      </div>
      <p className="mb-5 rounded-xl border border-amber-200 bg-amber-50 px-4 py-3 text-xs leading-6 text-amber-900">
        학습용 데모 · 실제 AI 미연결 — 정해진 규칙으로 로컬 자료를 검색하고
        읽습니다.
      </p>
      <div
        className={
          stepsFirst
            ? "grid items-start gap-6 lg:grid-cols-[280px_1fr]"
            : "grid items-start gap-6 lg:grid-cols-[1fr_280px]"
        }
      >
        {stepsFirst ? (
          <>
            {aside}
            {chat}
          </>
        ) : (
          <>
            {chat}
            {aside}
          </>
        )}
      </div>
    </main>
  );
}
