"use client";

import { Check } from "lucide-react";

import { cn } from "@/lib/utils";
import type { Language } from "@/types/api";

export const LANGUAGES: {
  value: Language;
  label: string;
  native: string;
  emoji: string;
}[] = [
  { value: "english", label: "English", native: "English", emoji: "🇬🇧" },
  { value: "hindi", label: "Hindi", native: "हिन्दी", emoji: "🇮🇳" },
  { value: "hinglish", label: "Hinglish", native: "Hinglish", emoji: "🗣️" },
  { value: "urdu", label: "Urdu", native: "اردو", emoji: "🇵🇰" },
  { value: "bhojpuri", label: "Bhojpuri", native: "भोजपुरी", emoji: "🪔" },
  { value: "bengali", label: "Bengali", native: "বাংলা", emoji: "🌾" },
];

interface Props {
  selected: Language[];
  onToggle: (lang: Language) => void;
}

export function LanguageChips({ selected, onToggle }: Props) {
  return (
    <div className="flex flex-wrap gap-2">
      {LANGUAGES.map((lang) => {
        const active = selected.includes(lang.value);
        return (
          <button
            key={lang.value}
            type="button"
            onClick={() => onToggle(lang.value)}
            className={cn(
              "inline-flex items-center gap-1.5 rounded-full px-3.5 py-2 text-sm font-medium transition active:scale-[0.97]",
              "border-2",
              active
                ? "border-brand-500 bg-brand-50 text-brand-700"
                : "border-slate-200 bg-white text-slate-700 hover:border-slate-300",
            )}
          >
            <span>{lang.emoji}</span>
            <span>{lang.native}</span>
            {active && <Check className="h-3.5 w-3.5" strokeWidth={3} />}
          </button>
        );
      })}
    </div>
  );
}
