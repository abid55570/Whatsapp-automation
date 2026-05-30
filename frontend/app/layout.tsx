import type { Metadata, Viewport } from "next";
import { Inter, Noto_Sans_Bengali, Noto_Sans_Devanagari } from "next/font/google";
import { NextIntlClientProvider } from "next-intl";
import { getLocale, getMessages } from "next-intl/server";

import { LOCALE_META, type Locale } from "@/i18n/config";
import { cn } from "@/lib/utils";

import "./globals.css";
import { Providers } from "./providers";

const inter = Inter({ subsets: ["latin"], variable: "--font-inter" });
const notoDevanagari = Noto_Sans_Devanagari({
  subsets: ["devanagari"],
  variable: "--font-devanagari",
});
const notoBengali = Noto_Sans_Bengali({
  subsets: ["bengali"],
  variable: "--font-bengali",
});

const SITE_URL = process.env.NEXT_PUBLIC_SITE_URL || "https://yourdomain.com";

export const metadata: Metadata = {
  metadataBase: new URL(SITE_URL),
  title: {
    default: "Whatly — ₹399/mo Business Automation for Indian SMBs",
    template: "%s · Whatly",
  },
  description:
    "Affordable WhatsApp auto-reply, order taking, and customer support for kirana, restaurant, salon, clinic. Hindi/Hinglish/English/Bengali. 14-day free trial, no card.",
  keywords: [
    "WhatsApp automation India",
    "WhatsApp business bot",
    "kirana WhatsApp order",
    "restaurant WhatsApp menu",
    "Hindi WhatsApp auto reply",
    "WhatsApp chatbot small business",
    "Wati alternative India",
    "AiSensy alternative",
  ],
  applicationName: "Whatly",
  authors: [{ name: "Whatly" }],
  alternates: {
    canonical: "/",
    languages: {
      en: "/",
      hi: "/",
      "hi-IN": "/",
      bn: "/",
      "bn-IN": "/",
      ur: "/",
      "x-default": "/",
    },
  },
  openGraph: {
    type: "website",
    locale: "en_IN",
    alternateLocale: ["hi_IN", "bn_IN", "ur_IN"],
    url: SITE_URL,
    siteName: "Whatly",
    title: "Whatly — ₹399/mo for Indian SMBs",
    description:
      "Auto-reply customers in 6 languages, take orders, send payment links — all on WhatsApp.",
    images: [
      {
        url: "/og-image.png",
        width: 1200,
        height: 630,
        alt: "Whatly for Indian small businesses",
      },
    ],
  },
  twitter: {
    card: "summary_large_image",
    title: "Whatly — ₹399/mo Business Automation",
    description:
      "Affordable WhatsApp auto-reply + order taking for Indian SMBs. 14-day free trial.",
    images: ["/og-image.png"],
  },
  manifest: "/manifest.json",
  icons: {
    icon: [
      { url: "/favicon.svg", type: "image/svg+xml" },
      { url: "/icon", type: "image/png", sizes: "32x32" },
    ],
    shortcut: "/favicon.svg",
    apple: "/apple-icon",
  },
  appleWebApp: {
    capable: true,
    statusBarStyle: "default",
    title: "Whatly",
  },
  formatDetection: {
    telephone: true,
    email: true,
    address: true,
  },
  robots: {
    index: true,
    follow: true,
    googleBot: {
      index: true,
      follow: true,
      "max-image-preview": "large",
      "max-snippet": -1,
    },
  },
};

export const viewport: Viewport = {
  width: "device-width",
  initialScale: 1,
  // intentionally NOT setting maximumScale / userScalable — pinch-zoom is a
  // WCAG 2.1 SC 1.4.4 accessibility requirement
  themeColor: [
    { media: "(prefers-color-scheme: light)", color: "#16A34A" },
    { media: "(prefers-color-scheme: dark)", color: "#0F172A" },
  ],
};

export default async function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const locale = (await getLocale()) as Locale;
  const messages = await getMessages();
  const dir = LOCALE_META[locale]?.dir ?? "ltr";

  return (
    <html
      lang={locale}
      dir={dir}
      className={cn(
        inter.variable,
        notoDevanagari.variable,
        notoBengali.variable,
      )}
    >
      <body className="font-sans">
        <NextIntlClientProvider locale={locale} messages={messages}>
          <Providers>{children}</Providers>
        </NextIntlClientProvider>
      </body>
    </html>
  );
}
