import type { MetadataRoute } from "next";

export default function manifest(): MetadataRoute.Manifest {
  return {
    id: "/?source=pwa",
    name: "Whatly — WhatsApp Business Automation",
    short_name: "Whatly",
    description:
      "Affordable WhatsApp auto-reply, orders, payments for Indian small businesses",
    start_url: "/dashboard",
    scope: "/",
    display: "standalone",
    background_color: "#FAFAF9",
    theme_color: "#25D366",
    orientation: "portrait",
    categories: ["business", "productivity", "shopping"],
    lang: "en-IN",
    dir: "ltr",
    icons: [
      {
        src: "/icon",
        sizes: "32x32",
        type: "image/png",
      },
      {
        src: "/apple-icon",
        sizes: "180x180",
        type: "image/png",
        purpose: "any",
      },
      {
        src: "/apple-icon",
        sizes: "180x180",
        type: "image/png",
        purpose: "maskable",
      },
    ],
  };
}
