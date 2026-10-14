import Link from "next/link";
import { Compass } from "lucide-react";
export function SiteHeader() {
  return (
    <header className="border-b border-slate-200/70 bg-white/80">
      <div className="page-shell flex min-h-20 flex-wrap items-center justify-between gap-3 py-4">
        <Link
          href="/"
          className="flex items-center gap-3"
          aria-label="Germany Life Agent 홈"
        >
          <span className="flex size-10 items-center justify-center rounded-2xl bg-slate-900 text-white">
            <Compass size={23} />
          </span>
          <span className="text-sm font-semibold tracking-tight">
            Germany Life <span className="text-slate-500">/</span> Agent
          </span>
        </Link>
        <nav
          aria-label="주 메뉴"
          className="flex items-center gap-5 text-sm text-slate-600"
        >
          <Link href="/housing" className="hover:text-blue-600">
            주거·임대
          </Link>
          <Link href="/visa" className="hover:text-blue-600">
            체류·비자
          </Link>
        </nav>
      </div>
    </header>
  );
}
