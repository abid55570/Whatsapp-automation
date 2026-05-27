"use client";

import { ArrowLeft, Globe } from "lucide-react";
import { useRouter } from "next/navigation";
import { useTranslations } from "next-intl";

import { LangSwitcher } from "@/components/LangSwitcher";

export default function LanguageSettingsPage() {
  const router = useRouter();
  const t = useTranslations();

  return (
    <div className="animate-fade-in">
      <header className="sticky top-0 bg-white border-b border-slate-200 z-10 p-4">
        <div className="flex items-center gap-3">
          <button
            onClick={() => router.back()}
            className="p-1 hover:bg-slate-100 rounded-lg active:scale-95"
          >
            <ArrowLeft className="h-5 w-5 text-slate-700" />
          </button>
          <div className="flex items-center gap-2">
            <Globe className="h-5 w-5 text-brand-600" />
            <h1 className="text-xl font-bold text-slate-900">
              {t("settings.row_app_language")}
            </h1>
          </div>
        </div>
      </header>

      <div className="p-4">
        <p className="text-xs text-slate-500 mb-4">
          {t("lang_picker.subtitle")}
        </p>
        <LangSwitcher variant="full" />
      </div>
    </div>
  );
}
