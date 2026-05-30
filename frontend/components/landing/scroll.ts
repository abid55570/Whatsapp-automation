import type Lenis from "lenis";

/** Smooth-scroll to a landing section by id (used by nav + CTAs). Routes
 *  through Lenis when available so the jump matches the page's momentum feel. */
export function scrollToSection(sectionId: string) {
  if (typeof window === "undefined") return;
  const lenis = (window as unknown as { lenis?: Lenis }).lenis;

  if (sectionId === "hero") {
    if (lenis) lenis.scrollTo(0, { duration: 1.4 });
    else window.scrollTo({ top: 0, behavior: "smooth" });
    return;
  }

  const el = document.getElementById(sectionId);
  if (!el) return;
  if (lenis) lenis.scrollTo(el, { offset: -24, duration: 1.4 });
  else el.scrollIntoView({ behavior: "smooth" });
}
