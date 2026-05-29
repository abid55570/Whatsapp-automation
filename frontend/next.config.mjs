import createNextIntlPlugin from "next-intl/plugin";

const withNextIntl = createNextIntlPlugin("./i18n/request.ts");

/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  poweredByHeader: false, // don't leak X-Powered-By: Next.js
  compress: true,
  experimental: {
    optimizePackageImports: [
      "lucide-react",
      "sonner",
      "@tanstack/react-query",
      "zustand",
      "next-intl",
    ],
  },
  // Proxy API calls to the backend server-side. The browser hits
  // /api/* on the SAME origin it loaded (localhost / LAN IP / tunnel),
  // and Next forwards to the backend over the internal docker network.
  // → no CORS, no hardcoded :8000, works from any device / tunnel.
  async rewrites() {
    const backend = process.env.BACKEND_INTERNAL_URL || "http://backend:8000";
    return [
      { source: "/api/:path*", destination: `${backend}/api/:path*` },
      { source: "/health", destination: `${backend}/health` },
    ];
  },
  // Tighten security headers globally
  async headers() {
    return [
      {
        source: "/:path*",
        headers: [
          { key: "X-DNS-Prefetch-Control", value: "on" },
          { key: "X-Content-Type-Options", value: "nosniff" },
          { key: "X-Frame-Options", value: "SAMEORIGIN" },
          { key: "Referrer-Policy", value: "strict-origin-when-cross-origin" },
          {
            key: "Permissions-Policy",
            value: "camera=(), microphone=(), geolocation=(self), payment=(self)",
          },
        ],
      },
    ];
  },
};

export default withNextIntl(nextConfig);
