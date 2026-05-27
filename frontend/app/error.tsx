"use client";

import { AlertCircle, RefreshCw } from "lucide-react";
import { useEffect } from "react";

export default function GlobalError({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    // TODO: pipe to Sentry once configured
    // eslint-disable-next-line no-console
    console.error("App error boundary:", error);
  }, [error]);

  return (
    <div className="min-h-screen flex items-center justify-center bg-slate-50 p-6">
      <div className="max-w-md w-full bg-white border border-slate-200 rounded-2xl p-8 text-center shadow-soft">
        <AlertCircle className="h-12 w-12 mx-auto text-red-500 mb-4" />
        <h1 className="text-xl font-bold text-slate-900 mb-2">
          Something went wrong
        </h1>
        <p className="text-sm text-slate-600 mb-6">
          We hit an unexpected error. Try again — if it keeps happening, message
          us on WhatsApp and we'll fix it.
        </p>
        {error.digest && (
          <p className="text-[10px] font-mono text-slate-400 mb-4">
            ref: {error.digest}
          </p>
        )}
        <button
          onClick={reset}
          className="inline-flex items-center gap-2 bg-brand-600 hover:bg-brand-700 text-white font-semibold px-5 py-2.5 rounded-lg transition active:scale-95 min-h-[44px]"
        >
          <RefreshCw className="h-4 w-4" />
          Try again
        </button>
      </div>
    </div>
  );
}
