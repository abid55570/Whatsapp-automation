import { Home } from "lucide-react";
import Link from "next/link";

export const metadata = {
  title: "Page not found",
  description: "404 — this page doesn't exist on Whatly.",
  robots: { index: false, follow: false },
};

export default function NotFound() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-slate-50 p-6">
      <div className="max-w-md w-full bg-white border border-slate-200 rounded-2xl p-8 text-center shadow-soft">
        <div className="text-6xl font-extrabold text-brand-600 mb-2">404</div>
        <h1 className="text-xl font-bold text-slate-900 mb-2">
          Page not found
        </h1>
        <p className="text-sm text-slate-600 mb-6">
          The page you're looking for doesn't exist — or has moved.
        </p>
        <Link
          href="/"
          className="inline-flex items-center gap-2 bg-brand-600 hover:bg-brand-700 text-white font-semibold px-5 py-2.5 rounded-lg transition active:scale-95 min-h-[44px]"
        >
          <Home className="h-4 w-4" />
          Back home
        </Link>
      </div>
    </div>
  );
}
