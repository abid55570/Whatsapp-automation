/** Smooth-scroll to a landing section by id (used by nav + CTAs). */
export function scrollToSection(sectionId: string) {
  if (typeof document === "undefined") return;
  if (sectionId === "hero") {
    window.scrollTo({ top: 0, behavior: "smooth" });
    return;
  }
  document.getElementById(sectionId)?.scrollIntoView({ behavior: "smooth" });
}
