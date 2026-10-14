import type { Metadata } from "next";
import { SiteHeader } from "@/components/site-header";
import "./globals.css";
export const metadata: Metadata = {
  title: {
    default: "Germany Life Agent — 독일 생활 정보 안내",
    template: "%s · Germany Life Agent",
  },
  description:
    "독일의 주거·임대와 체류·비자 정보를 한국어로 확인하고 공식 출처를 살펴보세요.",
};
export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="ko">
      <body>
        <a
          href="#main"
          className="sr-only focus:not-sr-only focus:absolute focus:z-50 focus:bg-white focus:p-4"
        >
          본문으로 건너뛰기
        </a>
        <SiteHeader />
        {children}
        <footer className="page-shell mt-16 flex flex-wrap justify-between gap-3 border-t border-slate-200 py-7 text-xs leading-6 text-slate-500">
          <span>Germany Life Agent · 독일 생활 정보를 한국어로.</span>
          <span>학습용 데모 · 실제 AI 미연결 · 일반 정보 안내</span>
        </footer>
      </body>
    </html>
  );
}
