import Link from "next/link";

export const metadata = {
  title: "Terms of Service",
  description:
    "Terms of Service for WhatsApp Auto — the WhatsApp automation platform for Indian small businesses.",
  alternates: { canonical: "/terms" },
};

export default function TermsPage() {
  return (
    <LegalLayout title="Terms of Service" lastUpdated="20 May 2026">
      <Section title="1. Acceptance">
        By creating an account or using <strong>WhatsApp Auto</strong> ("the
        Service"), you agree to these Terms. If you do not agree, do not use
        the Service.
      </Section>

      <Section title="2. What we provide">
        WhatsApp Auto is a SaaS platform that helps Indian small businesses
        automate WhatsApp customer conversations via Meta's WhatsApp Cloud
        API. We provide auto-reply, order management, sheet sync, and related
        tooling. We are <em>not</em> Meta and do not own WhatsApp.
      </Section>

      <Section title="3. Your account">
        <ul className="list-disc pl-5 space-y-1">
          <li>
            You must provide accurate phone number, business name, and contact
            info.
          </li>
          <li>
            You are responsible for keeping your login credentials secure. We
            verify via WhatsApp — anyone with access to your WhatsApp can log
            in.
          </li>
          <li>
            One business profile per user. You may not resell or sub-license
            the Service.
          </li>
        </ul>
      </Section>

      <Section title="4. Plans and payment">
        <p className="mb-2">
          Plans: <strong>Starter ₹399/mo</strong>, <strong>Growth ₹999/mo</strong>,
          <strong> Pro ₹1,999/mo</strong>. Optional AI Add-on ₹699/mo. All
          prices exclusive of GST.
        </p>
        <p className="mb-2">
          14-day free trial. No credit card required. After trial, service
          freezes until you upgrade. Payments are processed by Razorpay.
        </p>
        <p>
          Plan limits apply per billing cycle (conversations, AI replies).
          Usage beyond the limit blocks outbound sends until next cycle or
          upgrade.
        </p>
      </Section>

      <Section title="5. WhatsApp Business policies">
        You agree to comply with{" "}
        <a
          href="https://business.whatsapp.com/policy"
          className="underline"
          target="_blank"
          rel="noopener noreferrer"
        >
          WhatsApp Business Policy
        </a>{" "}
        and{" "}
        <a
          href="https://www.whatsapp.com/legal/commerce-policy"
          className="underline"
          target="_blank"
          rel="noopener noreferrer"
        >
          Commerce Policy
        </a>
        . Spam, adult content, regulated goods (alcohol/tobacco/firearms),
        and pyramid schemes will get your WhatsApp Business Account banned by
        Meta and your platform account terminated by us.
      </Section>

      <Section title="6. Customer data">
        You are the data controller for messages from your customers. We
        process them on your behalf as your data processor. See our{" "}
        <Link href="/privacy" className="underline">
          Privacy Policy
        </Link>{" "}
        for details.
      </Section>

      <Section title="7. Service availability">
        We target 99.5% monthly uptime but make no guarantees. We are not
        liable for losses caused by Meta outages, your internet, or your
        customers' WhatsApp.
      </Section>

      <Section title="8. Cancellation">
        You may cancel anytime from Settings → Billing. Service continues
        till the end of the paid period. See{" "}
        <Link href="/refund" className="underline">
          Refund Policy
        </Link>
        .
      </Section>

      <Section title="9. Termination">
        We may suspend or terminate your account if you violate these Terms,
        Meta's policies, or applicable law. Egregious violations (fraud,
        scam, mass-spam) → immediate termination, no refund.
      </Section>

      <Section title="10. Limitation of liability">
        To the extent permitted by law, our total liability is limited to the
        fees you paid in the past 3 months. We are not liable for
        consequential, incidental, or punitive damages.
      </Section>

      <Section title="11. Governing law">
        These Terms are governed by Indian law. Disputes resolved in courts
        of Bangalore, Karnataka.
      </Section>

      <Section title="12. Changes">
        We may update these Terms. Material changes will be notified via
        WhatsApp or email 14 days in advance. Continued use = acceptance.
      </Section>

      <Section title="13. Contact">
        Questions:{" "}
        <a href="mailto:legal@example.com" className="underline">
          legal@example.com
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
      <article className="max-w-3xl mx-auto px-4 py-12 prose-slate">
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
