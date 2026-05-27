/** next-intl request config — picks locale from cookie or default. */
import { cookies } from "next/headers";
import { getRequestConfig } from "next-intl/server";

import { DEFAULT_LOCALE, isLocale, type Locale } from "./config";

export default getRequestConfig(async () => {
  const cookieStore = await cookies();
  const raw = cookieStore.get("locale")?.value;
  const locale: Locale = isLocale(raw) ? raw : DEFAULT_LOCALE;

  const messages = (await import(`@/messages/${locale}.json`)).default;

  return {
    locale,
    messages,
  };
});
