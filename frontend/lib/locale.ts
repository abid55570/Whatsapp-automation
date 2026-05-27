"use server";
/** Server actions for locale cookie management. */
import { cookies } from "next/headers";

import { type Locale } from "@/i18n/config";

const COOKIE_NAME = "locale";
const ONE_YEAR_SECONDS = 60 * 60 * 24 * 365;

export async function setLocaleCookie(locale: Locale): Promise<void> {
  const store = await cookies();
  store.set(COOKIE_NAME, locale, {
    path: "/",
    maxAge: ONE_YEAR_SECONDS,
    sameSite: "lax",
    secure: process.env.NODE_ENV === "production",
  });
}

export async function getLocaleCookie(): Promise<string | undefined> {
  const store = await cookies();
  return store.get(COOKIE_NAME)?.value;
}
