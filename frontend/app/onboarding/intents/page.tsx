"use client";

import { ArrowRight, ChevronDown, ChevronUp, Languages, Loader2 } from "lucide-react";
import { useRouter } from "next/navigation";
import { useEffect, useMemo, useState } from "react";
import { toast } from "sonner";

import { Button } from "@/components/ui/Button";
import { TextArea } from "@/components/ui/TextArea";
import { Toggle } from "@/components/ui/Toggle";
import { LOCALE_META } from "@/i18n/config";
import { apiErrorMessage } from "@/lib/api";
import { useBulkConfigureIntents, useMyIntents } from "@/lib/queries";
import { cn } from "@/lib/utils";
import type { BusinessIntent } from "@/types/api";

// Locales offered for per-intent translations (en is the default reply_text)
const TRANSLATION_LOCALES = ["hi", "hinglish", "bn", "ur", "bho"] as const;

interface IntentDraft {
  intent_key: string;
  enabled: boolean;
  reply_text: string;
  reply_translations: Record<string, string>;
  priority: number;
}

export default function IntentsSetupPage() {
  const router = useRouter();
  const { data: intents, isLoading } = useMyIntents();
  const mutation = useBulkConfigureIntents();

  const [drafts, setDrafts] = useState<Record<string, IntentDraft>>({});

  useEffect(() => {
    if (!intents) return;
    setDrafts((current) => {
      if (Object.keys(current).length > 0) return current;
      const initial: Record<string, IntentDraft> = {};
      for (const bi of intents) {
        initial[bi.intent_key] = {
          intent_key: bi.intent_key,
          enabled: bi.enabled,
          reply_text: bi.reply_text,
          reply_translations: bi.reply_translations ?? {},
          priority: bi.priority,
        };
      }
      return initial;
    });
  }, [intents]);

  const enabledCount = useMemo(
    () => Object.values(drafts).filter((d) => d.enabled).length,
    [drafts],
  );

  function update(key: string, patch: Partial<IntentDraft>) {
    setDrafts((prev) => ({
      ...prev,
      [key]: { ...prev[key], ...patch },
    }));
  }

  async function handleSave() {
    try {
      await mutation.mutateAsync({
        intents: Object.values(drafts).map((d) => ({
          intent_key: d.intent_key,
          enabled: d.enabled,
          reply_text: d.reply_text,
          reply_translations: d.reply_translations,
          priority: d.priority,
        })),
      });
      toast.success("Auto-replies saved! 🎉");
      router.replace("/onboarding/done");
    } catch (err) {
      toast.error(apiErrorMessage(err));
    }
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-16">
        <Loader2 className="h-8 w-8 animate-spin text-brand-500" />
      </div>
    );
  }

  return (
    <div className="animate-fade-in">
      <h1 className="text-2xl font-bold text-slate-900 mb-1">
        Customize auto-replies
      </h1>
      <p className="text-slate-600 text-sm mb-2">
        Edit any reply, toggle off what doesn't apply. Add translations for
        customers in other languages.
      </p>
      <div className="text-xs font-medium text-brand-700 bg-brand-50 inline-block px-2.5 py-1 rounded-full mb-5">
        ⚡ {enabledCount} of {intents?.length ?? 0} enabled
      </div>

      <div className="space-y-3 mb-24">
        {intents
          ?.slice()
          .sort((a, b) => b.priority - a.priority)
          .map((bi) => (
            <IntentEditorCard
              key={bi.intent_key}
              intent={bi}
              draft={drafts[bi.intent_key]}
              onChange={(patch) => update(bi.intent_key, patch)}
            />
          ))}
      </div>

      <div className="fixed bottom-0 left-0 right-0 bg-white border-t border-slate-200 p-4">
        <div className="max-w-md mx-auto">
          <Button
            onClick={handleSave}
            loading={mutation.isPending}
            fullWidth
            size="lg"
          >
            Save & Finish Setup
            <ArrowRight className="h-5 w-5" />
          </Button>
        </div>
      </div>
    </div>
  );
}

function IntentEditorCard({
  intent,
  draft,
  onChange,
}: {
  intent: BusinessIntent;
  draft: IntentDraft | undefined;
  onChange: (patch: Partial<IntentDraft>) => void;
}) {
  const [showTranslations, setShowTranslations] = useState(false);

  if (!draft) return null;

  const translationCount = Object.values(draft.reply_translations).filter(
    (v) => v.trim().length > 0,
  ).length;

  function updateTranslation(locale: string, value: string) {
    onChange({
      reply_translations: {
        ...draft!.reply_translations,
        [locale]: value,
      },
    });
  }

  return (
    <div
      className={cn(
        "card transition",
        !draft.enabled && "opacity-60 bg-slate-50",
      )}
    >
      <div className="flex items-start justify-between gap-2 mb-2">
        <div className="flex-1 min-w-0">
          <h3 className="font-semibold text-slate-900 text-sm">
            {intent.name ?? intent.intent_key}
          </h3>
          {intent.description && (
            <p className="text-xs text-slate-500 mt-0.5 line-clamp-2">
              {intent.description}
            </p>
          )}
        </div>
        <Toggle
          checked={draft.enabled}
          onChange={(next) => onChange({ enabled: next })}
        />
      </div>

      {draft.enabled && (
        <>
          <label className="block text-xs font-medium text-slate-500 mt-2 mb-1">
            Default / English
          </label>
          <TextArea
            value={draft.reply_text}
            onChange={(e) => onChange({ reply_text: e.target.value })}
            placeholder="What should we reply with?"
            rows={2}
            maxLength={4000}
            className="text-sm"
          />

          <button
            type="button"
            onClick={() => setShowTranslations(!showTranslations)}
            className={cn(
              "mt-2 inline-flex items-center gap-1.5 text-xs font-medium transition active:scale-95",
              showTranslations ? "text-brand-700" : "text-slate-600",
            )}
          >
            <Languages className="h-3.5 w-3.5" />
            {translationCount > 0
              ? `${translationCount} translation${translationCount > 1 ? "s" : ""}`
              : "Add translation"}
            {showTranslations ? (
              <ChevronUp className="h-3.5 w-3.5" />
            ) : (
              <ChevronDown className="h-3.5 w-3.5" />
            )}
          </button>

          {showTranslations && (
            <div className="mt-2 space-y-2 pl-2 border-l-2 border-brand-100">
              {TRANSLATION_LOCALES.map((locale) => {
                const meta = LOCALE_META[locale];
                const value = draft.reply_translations[locale] ?? "";
                return (
                  <div key={locale}>
                    <label className="flex items-center gap-1.5 text-xs font-medium text-slate-600 mb-1">
                      <span>{meta.emoji}</span>
                      <span>{meta.native}</span>
                      {value.trim() && (
                        <span className="text-emerald-600">✓</span>
                      )}
                    </label>
                    <TextArea
                      value={value}
                      onChange={(e) =>
                        updateTranslation(locale, e.target.value)
                      }
                      placeholder={`Reply in ${meta.native} (leave blank to fall back)`}
                      rows={2}
                      maxLength={4000}
                      className="text-sm"
                    />
                  </div>
                );
              })}
              <p className="text-[10px] text-slate-500 leading-tight">
                💡 Customer's language detected from their message → matching
                translation sent. Blank = fall back to default.
              </p>
            </div>
          )}
        </>
      )}
    </div>
  );
}
