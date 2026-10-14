import Link from "next/link";
import {
  House,
  MapPin,
  FolderSearch,
  BookOpen,
  MessageCircle,
  ArrowUpRight,
} from "lucide-react";
import { ChatPanel } from "@/components/chat-panel";
export default function Home() {
  return (
    <main id="main" className="page-shell py-12 sm:py-20">
      <section className="grid items-center gap-12 lg:grid-cols-[1.15fr_1fr]">
        <div>
          <p className="eyebrow mb-5">LIFE IN GERMANY</p>
          <h1 className="text-4xl font-semibold leading-[1.25] tracking-tight sm:text-5xl">
            낯선 독일 생활,
            <br />
            자료에서 답을 찾는
            <br />
            <span className="text-blue-600">에이전트와 함께.</span>
          </h1>
          <p className="mt-6 max-w-md text-base leading-8 text-slate-500">
            독일의 주거와 체류에 관한 정보를 한국어로 확인하세요. 관련 공식
            자료와 원문 출처를 함께 안내합니다.
          </p>
          <div className="mt-7 flex flex-wrap gap-3">
            <Link
              href="/housing"
              className="inline-flex items-center gap-2 rounded-full bg-blue-600 px-6 py-3 text-sm font-medium text-white transition hover:bg-blue-700"
            >
              <House size={16} /> 주거·임대 질문
            </Link>
            <Link
              href="/visa"
              className="inline-flex items-center gap-2 rounded-full bg-emerald-600 px-6 py-3 text-sm font-medium text-white transition hover:bg-emerald-700"
            >
              <MapPin size={16} /> 체류·비자 질문
            </Link>
          </div>
          <p className="mt-4 text-xs text-slate-500">
            현재는 AI API 없이 실행하는 학습용 데모입니다.
          </p>
        </div>
        <div>
          <div className="mb-3 flex items-center gap-2 text-xs font-medium text-slate-600">
            <span className="size-2 rounded-full bg-blue-500" />
            아래에서 바로 질문해보세요
          </div>
          <ChatPanel domain="housing" />
          <p className="mt-4 text-center text-xs text-slate-600">
            메인에서 바로 동작하는 실제 데모입니다
          </p>
        </div>
      </section>
      <section className="mt-20">
        <div className="mb-6 flex items-end justify-between">
          <div>
            <p className="eyebrow mb-3">CHOOSE YOUR TOPIC</p>
            <h2 className="section-title">어떤 정보가 궁금한가요?</h2>
          </div>
          <span className="hidden text-xs text-slate-500 sm:block">
            주거와 체류, 필요한 정보부터
          </span>
        </div>
        <div className="grid gap-5 md:grid-cols-2">
          {[
            {
              path: "housing",
              name: "주거·임대",
              icon: House,
              description: "보증금과 임대계약의 기본 정보를 찾아보세요.",
              color: "bg-blue-50 text-blue-600",
              example: "보증금 · 계약 종료",
            },
            {
              path: "visa",
              name: "체류·비자",
              icon: MapPin,
              description: "유학과 취업 체류의 준비 과정을 살펴보세요.",
              color: "bg-emerald-50 text-emerald-600",
              example: "유학 · 취업 · 연장",
            },
          ].map((item) => (
            <Link
              key={item.path}
              href={`/${item.path}`}
              className="soft-card group p-7 transition hover:-translate-y-1 hover:border-blue-200"
            >
              <div className="flex justify-between">
                <span
                  className={`flex size-12 items-center justify-center rounded-2xl ${item.color}`}
                >
                  <item.icon size={24} />
                </span>
                <ArrowUpRight
                  className="text-slate-300 transition group-hover:text-blue-600"
                  size={22}
                />
              </div>
              <h3 className="mt-6 text-xl font-semibold">{item.name}</h3>
              <p className="mt-3 text-sm leading-7 text-slate-500">
                {item.description}
              </p>
              <p className="mt-5 text-xs font-medium text-slate-500">
                {item.example}
              </p>
            </Link>
          ))}
        </div>
      </section>
      <section className="mt-16 rounded-3xl bg-slate-900 px-7 py-9 text-white sm:px-10">
        <h2 className="text-xl font-semibold">정보는 이렇게 확인해보세요</h2>
        <div className="mt-7 grid gap-6 sm:grid-cols-3">
          {[
            [
              FolderSearch,
              "01",
              "질문하기",
              "궁금한 내용을 적고 필요한 상황을 알려주세요.",
            ],
            [
              BookOpen,
              "02",
              "검색과 읽기",
              "질문과 관련된 자료의 설명을 확인합니다.",
            ],
            [
              MessageCircle,
              "03",
              "답변과 출처",
              "답변의 출처를 열어 원문과 적용 조건을 확인하세요.",
            ],
          ].map(([Icon, num, title, text]) => {
            const I = Icon as typeof FolderSearch;
            return (
              <div key={String(num)}>
                <I size={22} className="mb-4 text-blue-300" />
                <p className="text-sm font-semibold">
                  <span className="mr-2 text-slate-400">{String(num)}</span>
                  {String(title)}
                </p>
                <p className="mt-2 text-sm leading-7 text-slate-400">
                  {String(text)}
                </p>
              </div>
            );
          })}
        </div>
      </section>
    </main>
  );
}
