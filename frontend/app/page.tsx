import Landing from "@/components/landing/Landing";

const SITE_URL = process.env.NEXT_PUBLIC_SITE_URL || "https://yourdomain.com";

const STRUCTURED_DATA = {
  "@context": "https://schema.org",
  "@graph": [
    {
      "@type": "Organization",
      "@id": `${SITE_URL}/#org`,
      name: "WhatsApp Auto",
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
      name: "WhatsApp Auto",
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
        { "@type": "Offer", name: "Growth", price: "999", priceCurrency: "INR" },
        { "@type": "Offer", name: "Pro", price: "1999", priceCurrency: "INR" },
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

export default function HomePage() {
  return (
    <>
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(STRUCTURED_DATA) }}
      />
      <Landing />
    </>
  );
}
