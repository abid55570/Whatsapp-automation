import Link from "next/link";

export const metadata = {
  title: "Privacy Policy",
  description:
    "Privacy Policy for WhatsApp Auto — DPDP-compliant data handling for Indian small businesses.",
  alternates: { canonical: "/privacy" },
};

export default function PrivacyPage() {
  return (
    <LegalLayout title="Privacy Policy" lastUpdated="20 May 2026">
      <Section title="1. Who we are">
        WhatsApp Auto ("we", "us") is operated from Bangalore, India. We
        process personal data in accordance with the{" "}
        <strong>Digital Personal Data Protection Act, 2023 (DPDP)</strong>{" "}
        and applicable Indian law.
      </Section>

      <Section title="2. What we collect">
        <strong>From you (business owner):</strong>
        <ul className="list-disc pl-5 space-y-1 mt-1 mb-3">
          <li>Phone number (for WhatsApp verification)</li>
          <li>Name, business name, business type</li>
          <li>Email (optional)</li>
          <li>WhatsApp Business credentials (encrypted at rest)</li>
          <li>Razorpay payment metadata (we never store full card details)</li>
        </ul>
        <strong>From your customers (via your WhatsApp Business):</strong>
        <ul className="list-disc pl-5 space-y-1 mt-1">
          <li>Phone number, display name, profile picture</li>
          <li>Messages they send to your business</li>
          <li>Order history, pickup/delivery details</li>
        </ul>
      </Section>

      <Section title="3. How we use your data">
        <ul className="list-disc pl-5 space-y-1">
          <li>Operate the Service (match intents, send replies, store messages)</li>
          <li>Bill you (Razorpay)</li>
          <li>Send service notifications (trial expiry, payment receipts)</li>
          <li>Improve product quality (aggregate, anonymized)</li>
          <li>Comply with legal obligations (Meta data requests, court orders)</li>
        </ul>
        <p className="mt-3">
          We <strong>do not</strong> sell your data. We <strong>do not</strong>{" "}
          read your customer messages for advertising.
        </p>
      </Section>

      <Section title="4. AI add-on">
        If you enable the AI add-on, customer messages are sent to our AI
        provider (Anthropic or OpenAI) under their data-processing
        agreement. Providers commit to not train on API requests. You can
        disable AI add-on anytime in Settings.
      </Section>

      <Section title="5. Where we store data">
        <ul className="list-disc pl-5 space-y-1">
          <li>Primary database: PostgreSQL hosted in India region</li>
          <li>WhatsApp access tokens: encrypted (AES-128 via Fernet)</li>
          <li>Razorpay credentials: never stored locally</li>
          <li>Backups: daily, retained 30 days</li>
        </ul>
      </Section>

      <Section title="6. How long we keep data">
        <ul className="list-disc pl-5 space-y-1">
          <li>Active accounts: data kept for service operation</li>
          <li>Canceled accounts: 90 days retention, then permanent deletion</li>
          <li>Audit logs (webhooks, payments): 3 years (legal req)</li>
          <li>Messages older than 6 months: archived (still queryable)</li>
        </ul>
      </Section>

      <Section title="7. Your rights (under DPDP)">
        <ul className="list-disc pl-5 space-y-1">
          <li>
            <strong>Access</strong>: request a copy of all data we hold about you
          </li>
          <li>
            <strong>Correction</strong>: fix inaccurate data via dashboard or
            by writing to us
          </li>
          <li>
            <strong>Erasure</strong>: delete your account anytime; data wiped
            within 30 days
          </li>
          <li>
            <strong>Portability</strong>: export your conversations + contacts
            as JSON / CSV
          </li>
          <li>
            <strong>Grievance</strong>: contact our Data Protection Officer at{" "}
            <a href="mailto:privacy@example.com" className="underline">
              privacy@example.com
            </a>{" "}
            — we respond within 7 days
          </li>
        </ul>
      </Section>

      <Section title="8. Cookies + tracking">
        We use a single first-party cookie (<code>locale</code>) to remember
        your chosen language. JWT auth tokens are stored in browser
        localStorage. We do not use third-party analytics, ad pixels, or
        retargeting trackers.
      </Section>

      <Section title="9. Third parties">
        We share data only with the minimum providers needed to operate:
        <ul className="list-disc pl-5 space-y-1 mt-1">
          <li>
            <strong>Meta</strong> (WhatsApp delivery) — covered by Meta's
            terms
          </li>
          <li>
            <strong>Razorpay</strong> (payments) — covered by Razorpay's
            privacy policy
          </li>
          <li>
            <strong>Google</strong> (Sheets API, if you connect a sheet) —
            read-only access
          </li>
          <li>
            <strong>Anthropic / OpenAI</strong> (only if AI add-on enabled)
          </li>
          <li>
            <strong>Resend</strong> (transactional email)
          </li>
        </ul>
      </Section>

      <Section title="10. Security">
        Tokens encrypted at rest. HTTPS everywhere. Rate limiting on auth
        endpoints. Webhook signatures verified. Regular dependency updates.
      </Section>

      <Section title="11. Children">
        Not intended for users under 18. We do not knowingly collect data
        from minors.
      </Section>

      <Section title="12. Changes">
        Updates posted here; material changes notified via WhatsApp or email
        14 days in advance.
      </Section>

      <Section title="13. Contact">
        Privacy concerns:{" "}
        <a href="mailto:privacy@example.com" className="underline">
          privacy@example.com
        </a>
      </Section>
    </LegalLayout>
  );
}


function LegalLayout({
  title,
  lastUpdated,
  children,
}: {
  title: string;
  lastUpdated: string;
  children: React.ReactNode;
}) {
  return (
    <main className="min-h-screen bg-white">
      <header className="border-b border-slate-100 px-4 py-4 sticky top-0 bg-white/95 backdrop-blur">
        <div className="max-w-3xl mx-auto flex items-center justify-between">
          <Link href="/" className="flex items-center gap-2">
            <span className="w-8 h-8 rounded-lg bg-brand-500 text-white flex items-center justify-center">
              💬
            </span>
            <span className="font-bold text-slate-900">WhatsApp Auto</span>
          </Link>
          <Link
            href="/"
            className="text-sm text-slate-600 hover:text-slate-900"
          >
            ← Back
          </Link>
        </div>
      </header>
      <article className="max-w-3xl mx-auto px-4 py-12">
        <h1 className="text-3xl font-bold text-slate-900 mb-2">{title}</h1>
        <p className="text-sm text-slate-500 mb-10">
          Last updated: {lastUpdated}
        </p>
        <div className="space-y-6 text-slate-700 leading-relaxed">
          {children}
        </div>
      </article>
    </main>
  );
}


function Section({
  title,
  children,
}: {
  title: string;
  children: React.ReactNode;
}) {
  return (
    <section>
      <h2 className="text-lg font-bold text-slate-900 mb-2">{title}</h2>
      <div className="text-sm">{children}</div>
    </section>
  );
}
