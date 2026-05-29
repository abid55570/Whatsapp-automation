import {
  Bot,
  Check,
  FileSpreadsheet,
  Languages,
  MessageCircle,
  Package,
  Shield,
  Sparkles,
  Zap,
} from "lucide-react";
import Link from "next/link";

import { getTranslations } from "next-intl/server";

import { DemoReels } from "@/components/DemoReels";
import { HookReel } from "@/components/HookReel";
import { LangSwitcher } from "@/components/LangSwitcher";

const SITE_URL = process.env.NEXT_PUBLIC_SITE_URL || "https://yourdomain.com";

const STRUCTURED_DATA = {
  "@context": "https://schema.org",
  "@graph": [
    {
      "@type": "Organization",
      "@id": `${SITE_URL}/#org`,
      name: "Whatly",
      url: SITE_URL,
      logo: `${SITE_URL}/icon-512.png`,
      sameAs: [],
      contactPoint: {
        "@type": "ContactPoint",
        contactType: "customer support",
        availableLanguage: ["en", "hi", "bn", "ur"],
      },
    },
    {
      "@type": "SoftwareApplication",
      name: "Whatly",
      applicationCategory: "BusinessApplication",
      operatingSystem: "Web, iOS, Android (PWA)",
      offers: [
        {
          "@type": "Offer",
          name: "Starter",
          price: "399",
          priceCurrency: "INR",
          priceSpecification: {
            "@type": "UnitPriceSpecification",
            price: "399",
            priceCurrency: "INR",
            referenceQuantity: { "@type": "QuantitativeValue", value: 1, unitCode: "MON" },
          },
        },
        {
          "@type": "Offer",
          name: "Growth",
          price: "999",
          priceCurrency: "INR",
        },
        {
          "@type": "Offer",
          name: "Pro",
          price: "1999",
          priceCurrency: "INR",
        },
      ],
    },
    {
      "@type": "FAQPage",
      mainEntity: [
        {
          "@type": "Question",
          name: "Is there a free trial?",
          acceptedAnswer: {
            "@type": "Answer",
            text: "Yes — 14 days, 100 conversations free. No card needed. After trial, plans start at ₹399/month.",
          },
        },
        {
          "@type": "Question",
          name: "Which languages does the bot understand?",
          acceptedAnswer: {
            "@type": "Answer",
            text: "Hindi, Hinglish, English, Bengali, Urdu, Bhojpuri — all six are first-class. The bot replies in the customer's language automatically.",
          },
        },
        {
          "@type": "Question",
          name: "Do I need to install software?",
          acceptedAnswer: {
            "@type": "Answer",
            text: "No. Everything runs on the web — install our PWA on your phone or open in any browser. Works on existing WhatsApp Business app, no migration needed.",
          },
        },
        {
          "@type": "Question",
          name: "How is this different from Wati or AiSensy?",
          acceptedAnswer: {
            "@type": "Answer",
            text: "We start at ₹399 (vs ₹2,499+ for Wati), are built for Hindi/Hinglish-first owners, use Google Sheets as your CMS, and include Hindi number order parsing ('do atta, ek dal') out of the box.",
          },
        },
      ],
    },
  ],
};

export default async function HomePage() {
  const t = await getTranslations("landing");
  return (
    <main className="min-h-screen bg-white">
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(STRUCTURED_DATA) }}
      />
      {/* ============================================================ */}
      {/* HEADER                                                       */}
      {/* ============================================================ */}
      <header className="sticky top-0 z-30 bg-white/90 backdrop-blur border-b border-slate-100">
        <div className="max-w-5xl mx-auto px-4 py-3 flex items-center justify-between">
          <Link href="/" className="flex items-center gap-2">
            <span
              className="w-9 h-9 rounded-xl text-white flex items-center justify-center text-lg font-black shadow-soft"
              style={{ background: "linear-gradient(135deg, #25D366 0%, #128C7E 100%)" }}
              aria-label="Whatly logo"
            >
              W
            </span>
            <span className="font-bold text-slate-900 hidden sm:inline">
              Whatly
            </span>
          </Link>
          <div className="flex items-center gap-2">
            <LangSwitcher variant="compact" />
            <Link
              href="/signup"
              className="hidden sm:inline-flex items-center gap-1 text-sm font-semibold text-slate-700 hover:text-slate-900 px-3 py-2 min-h-[44px]"
            >
              {t("log_in")}
            </Link>
            <Link
              href="/language?next=/signup"
              className="inline-flex items-center gap-1 bg-brand-500 hover:bg-brand-600 text-white text-sm font-semibold px-4 py-2.5 min-h-[44px] rounded-lg transition active:scale-95"
            >
              {t("start_free")}
            </Link>
          </div>
        </div>
      </header>

      {/* ============================================================ */}
      {/* HERO                                                         */}
      {/* ============================================================ */}
      <section className="bg-gradient-to-br from-brand-50 via-white to-accent-50 px-4 py-12 sm:py-20">
        <div className="max-w-3xl mx-auto text-center">
          <div className="inline-flex items-center gap-1.5 bg-brand-100 text-brand-700 text-xs font-semibold px-3 py-1 rounded-full mb-6">
            <Sparkles className="h-3 w-3" />
            {t("built_for")}
          </div>
          <h1 className="text-4xl sm:text-5xl font-extrabold text-slate-900 mb-4 font-display leading-tight">
            {t("hero_title_a")}{" "}
            <span className="text-brand-600">{t("hero_title_b")}</span>
          </h1>
          <p className="text-lg text-slate-600 mb-8 max-w-2xl mx-auto">
            {t("hero_subtitle")}{" "}
            <span className="font-semibold text-slate-900">
              {t("hero_price_inline")}
            </span>
          </p>
          <div className="flex flex-col sm:flex-row gap-3 justify-center items-center mb-6">
            <Link
              href="/language?next=/signup"
              className="btn-primary w-full sm:w-auto text-lg px-8"
            >
              {t("cta")}
            </Link>
            <Link
              href="#pricing"
              className="btn-secondary w-full sm:w-auto text-lg px-8"
            >
              {t("see_pricing")}
            </Link>
          </div>
          <p className="text-xs text-slate-500">
            {t("no_card_cancel")}
          </p>
        </div>
      </section>

      {/* ============================================================ */}
      {/* HOOK REEL — Without vs With Whatly                           */}
      {/* ============================================================ */}
      <HookReel />

      {/* ============================================================ */}
      {/* DEMO REELS — 6 industries rotate (chat follows the locale)   */}
      {/* ============================================================ */}
      <section className="px-4 py-12 sm:py-16 bg-white">
        <DemoReels />
      </section>

      {/* ============================================================ */}
      {/* USE CASES                                                    */}
      {/* ============================================================ */}
      <section className="px-4 py-16 max-w-5xl mx-auto">
        <h2 className="text-3xl font-bold text-slate-900 text-center mb-2">
          {t("uc_title")}
        </h2>
        <p className="text-slate-600 text-center mb-10">
          {t("uc_sub")}
        </p>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          <UseCaseCard emoji="🍕" title={t("uc_restaurant")} lines={["Menu", "Orders", "Pickup"]} />
          <UseCaseCard emoji="🛒" title={t("uc_kirana")} lines={["Items list", "COD orders", "Pickup"]} />
          <UseCaseCard emoji="💇" title={t("uc_salon")} lines={["Services", "Bookings", "Reminders"]} />
          <UseCaseCard emoji="🏥" title={t("uc_clinic")} lines={["Hours", "Appointments", "FAQs"]} />
          <UseCaseCard emoji="💪" title={t("uc_gym")} lines={["Classes", "Membership", "Hours"]} />
          <UseCaseCard emoji="📚" title={t("uc_coaching")} lines={["Batches", "Fees", "Schedule"]} />
          <UseCaseCard emoji="📦" title={t("uc_d2c")} lines={["Catalog", "Orders", "Tracking"]} />
          <UseCaseCard emoji="✨" title={t("uc_anything")} lines={["Custom FAQs", "From Google Sheet"]} />
        </div>
      </section>

      {/* ============================================================ */}
      {/* FEATURES                                                     */}
      {/* ============================================================ */}
      <section className="bg-slate-50 px-4 py-16">
        <div className="max-w-5xl mx-auto">
          <h2 className="text-3xl font-bold text-slate-900 text-center mb-2">
            {t("feat_title")}
          </h2>
          <p className="text-slate-600 text-center mb-10">
            {t("feat_sub")}
          </p>
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
            <Feature
              icon={Zap}
              title={t("feat_reply_title")}
              body={t("feat_reply_body")}
              bg="bg-amber-100"
              color="text-amber-600"
            />
            <Feature
              icon={FileSpreadsheet}
              title={t("feat_sheets_title")}
              body={t("feat_sheets_body")}
              bg="bg-green-100"
              color="text-green-600"
            />
            <Feature
              icon={Package}
              title={t("feat_orders_title")}
              body={t("feat_orders_body")}
              bg="bg-indigo-100"
              color="text-indigo-600"
            />
            <Feature
              icon={MessageCircle}
              title={t("feat_inbox_title")}
              body={t("feat_inbox_body")}
              bg="bg-brand-100"
              color="text-brand-600"
            />
            <Feature
              icon={Languages}
              title={t("feat_lang_title")}
              body={t("feat_lang_body")}
              bg="bg-pink-100"
              color="text-pink-600"
            />
            <Feature
              icon={Bot}
              title={t("feat_ai_title")}
              body={t("feat_ai_body")}
              bg="bg-purple-100"
              color="text-purple-600"
            />
          </div>
        </div>
      </section>

      {/* ============================================================ */}
      {/* HOW IT WORKS                                                 */}
      {/* ============================================================ */}
      <section className="px-4 py-16 max-w-4xl mx-auto">
        <h2 className="text-3xl font-bold text-slate-900 text-center mb-2">
          {t("how_title")}
        </h2>
        <p className="text-slate-600 text-center mb-10">
          {t("how_sub")}
        </p>
        <div className="space-y-3">
          {[
            { n: 1, title: t("step1_title"), body: t("step1_body") },
            { n: 2, title: t("step2_title"), body: t("step2_body") },
            { n: 3, title: t("step3_title"), body: t("step3_body") },
            { n: 4, title: t("step4_title"), body: t("step4_body") },
          ].map((s) => (
            <div
              key={s.n}
              className="flex items-start gap-4 p-4 rounded-2xl bg-white border border-slate-200"
            >
              <div className="w-10 h-10 rounded-full bg-brand-500 text-white font-bold flex items-center justify-center flex-shrink-0">
                {s.n}
              </div>
              <div>
                <h3 className="font-semibold text-slate-900 mb-1">{s.title}</h3>
                <p className="text-sm text-slate-600">{s.body}</p>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* ============================================================ */}
      {/* PRICING                                                      */}
      {/* ============================================================ */}
      <section id="pricing" className="bg-slate-50 px-4 py-16">
        <div className="max-w-5xl mx-auto">
          <h2 className="text-3xl font-bold text-slate-900 text-center mb-2">
            {t("price_title")}
          </h2>
          <p className="text-slate-600 text-center mb-10">
            {t("price_sub")}
          </p>
          <div className="grid md:grid-cols-3 gap-4">
            <PricingCard
              ctaLabel={t("price_card_btn")}
              name="Starter"
              price={399}
              conv={1000}
              features={[
                "Auto-reply (6 languages)",
                "1,000 conversations/mo",
                "FAQ bot",
                "Inbox + dashboard",
                "Google Sheets sync",
              ]}
            />
            <PricingCard
              ctaLabel={t("price_card_btn")}
              name="Growth"
              price={999}
              conv={3000}
              recommended
              features={[
                "Everything in Starter",
                "3,000 conversations/mo",
                "Orders + Pickup flow",
                "Bookings + Calendar",
                "Razorpay payment links",
                "Analytics",
              ]}
            />
            <PricingCard
              ctaLabel={t("price_card_btn")}
              name="Pro"
              price={1999}
              conv={6000}
              features={[
                "Everything in Growth",
                "6,000 conversations/mo",
                "Broadcasts",
                "API + Webhooks",
                "Priority support",
              ]}
            />
          </div>

          <div className="mt-6 max-w-2xl mx-auto card bg-gradient-to-br from-indigo-50 to-purple-50 border border-indigo-200 text-center">
            <div className="flex items-center justify-center gap-3 mb-2">
              <span className="text-3xl">🤖</span>
              <div className="text-left">
                <div className="font-bold text-slate-900">AI Add-on</div>
                <div className="text-xs text-slate-600">Optional · Any plan</div>
              </div>
              <div className="text-2xl font-bold text-slate-900 ml-auto">
                +₹699/mo
              </div>
            </div>
            <p className="text-sm text-slate-700">
              Smart-reply fallback · Auto-translate to customer's language ·
              1,500 AI replies/month
            </p>
          </div>

          <p className="text-center text-xs text-slate-500 mt-6">
            All prices excl. GST · UPI / cards / net banking via Razorpay ·
            Free 14-day trial · No commitment
          </p>
        </div>
      </section>

      {/* ============================================================ */}
      {/* SOCIAL PROOF / TRUST                                         */}
      {/* ============================================================ */}
      <section className="px-4 py-12 max-w-5xl mx-auto">
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 text-center">
          <TrustStat number="6" label={t("trust_languages")} />
          <TrustStat number="₹399" label={t("trust_starts")} />
          <TrustStat number="10 min" label={t("trust_live")} />
          <TrustStat number="14-day" label={t("trust_trial")} />
        </div>
      </section>

      {/* ============================================================ */}
      {/* FAQ                                                          */}
      {/* ============================================================ */}
      <section className="bg-slate-50 px-4 py-16">
        <div className="max-w-3xl mx-auto">
          <h2 className="text-3xl font-bold text-slate-900 text-center mb-10">
            {t("faq_title")}
          </h2>
          <div className="space-y-3">
            <FAQ
              q="Will my customers know it's a bot?"
              a="They get instant, accurate answers in their language. Most assume it's you typing fast. You can mark some replies with 🤖 if you want full transparency."
            />
            <FAQ
              q="Do I need a special WhatsApp number?"
              a="Yes — a WhatsApp Business number (free, get it from the WhatsApp Business app). We connect to it via Meta's official integration."
            />
            <FAQ
              q="What if a customer asks something my FAQs don't cover?"
              a="The message lands in your inbox marked 'Needs reply'. You reply manually. Or enable AI add-on (₹699/mo) — it generates smart fallback replies."
            />
            <FAQ
              q="Which languages exactly?"
              a="English, Hindi (देवनागरी), Hinglish (Roman Hindi), Bengali, Urdu, Bhojpuri. The bot detects what customer wrote and replies in same language."
            />
            <FAQ
              q="How do I add new items / FAQs?"
              a="Two ways: (1) Edit directly in the dashboard, or (2) Edit your Google Sheet — bot auto-syncs every 15 minutes. Most shop owners prefer the Sheet."
            />
            <FAQ
              q="What if I want to cancel?"
              a="Cancel anytime from Settings. Service continues till end of paid period. No questions asked, no penalty."
            />
            <FAQ
              q="Is there a setup fee or commitment?"
              a="No setup fee. No commitment. 14-day free trial. Card not required for trial."
            />
            <FAQ
              q="How are payments handled?"
              a="Customer pays you via Razorpay (UPI / card / net banking) or COD on pickup. You configure both. We never touch your customer payments."
            />
          </div>
        </div>
      </section>

      {/* ============================================================ */}
      {/* FINAL CTA                                                    */}
      {/* ============================================================ */}
      <section className="px-4 py-20 bg-gradient-to-br from-brand-500 to-emerald-600 text-white text-center">
        <h2 className="text-3xl sm:text-4xl font-bold mb-3">
          {t("final_title")}
        </h2>
        <p className="text-lg text-brand-50 mb-8 max-w-xl mx-auto">
          {t("final_sub")}
        </p>
        <Link
          href="/language?next=/signup"
          className="inline-flex items-center gap-2 bg-white text-brand-700 font-bold px-8 py-4 rounded-2xl shadow-lg text-lg hover:bg-brand-50 transition active:scale-[0.98]"
        >
          <Sparkles className="h-5 w-5" />
          {t("final_btn")}
        </Link>
        <p className="text-xs text-brand-100 mt-4">
          {t("final_card")}
        </p>
      </section>

      {/* ============================================================ */}
      {/* FOOTER                                                       */}
      {/* ============================================================ */}
      <footer className="bg-slate-900 text-slate-400 px-4 py-12">
        <div className="max-w-5xl mx-auto">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-6 mb-8">
            <div>
              <div className="flex items-center gap-2 mb-3">
                <span
                  className="w-8 h-8 rounded-xl text-white flex items-center justify-center text-sm font-black"
                  style={{ background: "linear-gradient(135deg, #25D366 0%, #128C7E 100%)" }}
                  aria-hidden
                >
                  W
                </span>
                <span className="font-bold text-white">Whatly</span>
              </div>
              <p className="text-xs leading-relaxed">
                Affordable WhatsApp automation for Indian small businesses.
              </p>
            </div>
            <div>
              <h4 className="font-semibold text-white text-sm mb-3">{t("footer_product")}</h4>
              <ul className="text-xs space-y-2">
                <li>
                  <Link href="#pricing" className="hover:text-white">
                    {t("footer_pricing")}
                  </Link>
                </li>
                <li>
                  <Link href="/signup" className="hover:text-white">
                    {t("footer_signup")}
                  </Link>
                </li>
                <li>
                  <Link href="/signup" className="hover:text-white">
                    {t("footer_login")}
                  </Link>
                </li>
              </ul>
            </div>
            <div>
              <h4 className="font-semibold text-white text-sm mb-3">{t("footer_legal")}</h4>
              <ul className="text-xs space-y-2">
                <li>
                  <Link href="/terms" className="hover:text-white">
                    {t("footer_terms")}
                  </Link>
                </li>
                <li>
                  <Link href="/privacy" className="hover:text-white">
                    {t("footer_privacy")}
                  </Link>
                </li>
                <li>
                  <Link href="/refund" className="hover:text-white">
                    Refund Policy
                  </Link>
                </li>
              </ul>
            </div>
            <div>
              <h4 className="font-semibold text-white text-sm mb-3">Support</h4>
              <ul className="text-xs space-y-2">
                <li>
                  <a
                    href="mailto:help@example.com"
                    className="hover:text-white"
                  >
                    help@example.com
                  </a>
                </li>
                <li>
                  <a
                    href="https://wa.me/919999999999"
                    className="hover:text-white"
                  >
                    WhatsApp us
                  </a>
                </li>
              </ul>
            </div>
          </div>
          <div className="border-t border-slate-800 pt-6 flex flex-col sm:flex-row justify-between gap-3 text-xs">
            <p>© 2026 Whatly. All rights reserved.</p>
            <p className="flex items-center gap-1">
              <Shield className="h-3 w-3" />
              Powered by Meta WhatsApp Cloud API
            </p>
          </div>
        </div>
      </footer>
    </main>
  );
}


function UseCaseCard({
  emoji,
  title,
  lines,
}: {
  emoji: string;
  title: string;
  lines: string[];
}) {
  return (
    <div className="bg-white rounded-2xl p-4 shadow-soft border border-slate-100 text-center">
      <div className="text-3xl mb-1.5">{emoji}</div>
      <h3 className="font-semibold text-slate-900 text-sm mb-2">{title}</h3>
      <ul className="text-[11px] text-slate-500 space-y-0.5">
        {lines.map((l) => (
          <li key={l}>• {l}</li>
        ))}
      </ul>
    </div>
  );
}


function Feature({
  icon: Icon,
  title,
  body,
  bg,
  color,
}: {
  icon: React.ComponentType<{ className?: string }>;
  title: string;
  body: string;
  bg: string;
  color: string;
}) {
  return (
    <div className="card bg-white">
      <div className={`w-10 h-10 rounded-xl ${bg} flex items-center justify-center mb-3`}>
        <Icon className={`h-5 w-5 ${color}`} />
      </div>
      <h3 className="font-semibold text-slate-900 mb-1.5">{title}</h3>
      <p className="text-sm text-slate-600 leading-relaxed">{body}</p>
    </div>
  );
}


function PricingCard({
  name,
  price,
  conv,
  features,
  recommended,
  ctaLabel,
}: {
  name: string;
  price: number;
  conv: number;
  features: string[];
  recommended?: boolean;
  ctaLabel: string;
}) {
  return (
    <div
      className={`relative card bg-white ${
        recommended ? "ring-2 ring-brand-500 shadow-lg" : ""
      }`}
    >
      {recommended && (
        <span className="absolute -top-3 left-1/2 -translate-x-1/2 bg-brand-500 text-white text-[10px] font-bold uppercase tracking-wider px-3 py-1 rounded-full shadow">
          Most Popular
        </span>
      )}
      <h3 className="font-bold text-xl text-slate-900 mb-1">{name}</h3>
      <div className="flex items-baseline gap-1 mb-1">
        <span className="text-3xl font-extrabold text-slate-900">₹{price}</span>
        <span className="text-sm text-slate-500">/month</span>
      </div>
      <p className="text-xs text-slate-500 mb-4">
        {conv.toLocaleString("en-IN")} conversations included
      </p>
      <ul className="space-y-2 mb-6">
        {features.map((f) => (
          <li
            key={f}
            className="flex items-start gap-2 text-sm text-slate-700"
          >
            <Check className="h-4 w-4 text-emerald-500 flex-shrink-0 mt-0.5" />
            <span>{f}</span>
          </li>
        ))}
      </ul>
      <Link
        href="/language?next=/signup"
        className={`w-full block text-center font-semibold py-2.5 rounded-xl transition active:scale-[0.98] ${
          recommended
            ? "bg-brand-500 text-white hover:bg-brand-600"
            : "bg-slate-100 text-slate-900 hover:bg-slate-200"
        }`}
      >
        {ctaLabel}
      </Link>
    </div>
  );
}


function TrustStat({ number, label }: { number: string; label: string }) {
  return (
    <div>
      <div className="text-3xl font-extrabold text-brand-600">{number}</div>
      <div className="text-xs text-slate-600 mt-1">{label}</div>
    </div>
  );
}


function FAQ({ q, a }: { q: string; a: string }) {
  return (
    <details className="group bg-white rounded-2xl border border-slate-200 overflow-hidden">
      <summary className="cursor-pointer p-4 font-semibold text-slate-900 flex items-center justify-between gap-3 hover:bg-slate-50">
        <span className="text-sm">{q}</span>
        <span className="text-slate-400 group-open:rotate-45 transition-transform text-xl leading-none">
          +
        </span>
      </summary>
      <div className="px-4 pb-4 text-sm text-slate-600 leading-relaxed">
        {a}
      </div>
    </details>
  );
}
