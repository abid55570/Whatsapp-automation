/** i18n config — supported locales for the platform UI. */

export const LOCALES = ["en", "hi", "hinglish", "bn", "ur", "bho"] as const;
export type Locale = (typeof LOCALES)[number];

export const DEFAULT_LOCALE: Locale = "en";

export const LOCALE_META: Record<
  Locale,
  { name: string; native: string; emoji: string; dir: "ltr" | "rtl" }
> = {
  en: { name: "English", native: "English", emoji: "🇬🇧", dir: "ltr" },
  hi: { name: "Hindi", native: "हिन्दी", emoji: "🇮🇳", dir: "ltr" },
  hinglish: { name: "Hinglish", native: "Hinglish", emoji: "🗣️", dir: "ltr" },
  bn: { name: "Bengali", native: "বাংলা", emoji: "🌾", dir: "ltr" },
  ur: { name: "Urdu", native: "اردو", emoji: "🪔", dir: "rtl" },
  bho: { name: "Bhojpuri", native: "भोजपुरी", emoji: "🪕", dir: "ltr" },
};

export function isLocale(v: string | null | undefined): v is Locale {
  return LOCALES.includes(v as Locale);
}
