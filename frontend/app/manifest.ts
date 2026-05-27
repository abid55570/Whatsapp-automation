import type { MetadataRoute } from "next";

export default function manifest(): MetadataRoute.Manifest {
  return {
    id: "/?source=pwa",
    name: "WhatsApp Auto — Business Automation",
    short_name: "WA Auto",
    description:
      "Affordable WhatsApp auto-reply, orders, payments for Indian small businesses",
    start_url: "/dashboard",
    scope: "/",
    display: "standalone",
    background_color: "#FAFAF9",
    theme_color: "#16A34A",
    orientation: "portrait",
    categories: ["business", "productivity", "shopping"],
    lang: "en-IN",
    dir: "ltr",
    icons: [
      // Dynamic — served by app/icon.tsx (32x32) + app/apple-icon.tsx (180x180)
      // For Android PWA install card we serve 192/512 via the same dynamic route.
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
