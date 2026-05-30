import Link from "next/link";

export const metadata = {
  title: "Blog — Whatly",
  description: "Playbooks and stories on WhatsApp automation for Indian SMBs.",
};

export default function BlogPage() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center bg-white px-6 text-center">
      <span className="mb-5 inline-flex items-center gap-2 rounded-full border border-[#25d366]/30 bg-[#25d366]/10 px-4 py-1.5 text-xs font-semibold uppercase tracking-[0.25em] text-[#1faa59]">
        Whatly Blog
      </span>
      <h1 className="font-display-serif text-5xl italic leading-[0.95] text-slate-900 md:text-7xl">
        Coming <span className="text-emerald-500">soon</span>
      </h1>
      <p className="mt-5 max-w-md text-base leading-relaxed text-slate-600">
        Playbooks, owner stories and WhatsApp automation tips for Indian shops
        are on the way.
      </p>
      <Link
        href="/"
        className="accent-gradient mt-8 inline-block rounded-full px-7 py-3 text-sm font-semibold text-white transition-transform duration-300 hover:scale-105"
      >
        ← Back to home
      </Link>
    </main>
  );
}
