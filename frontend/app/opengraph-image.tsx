import { ImageResponse } from "next/og";

export const runtime = "edge";
export const alt = "Whatly — ₹399/mo WhatsApp Business Automation for Indian SMBs";
export const size = { width: 1200, height: 630 };
export const contentType = "image/png";

export default function OGImage() {
  return new ImageResponse(
    (
      <div
        style={{
          background: "linear-gradient(135deg, #25D366 0%, #128C7E 100%)",
          color: "white",
          width: "100%",
          height: "100%",
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          justifyContent: "center",
          padding: "80px",
          textAlign: "center",
          fontFamily: "system-ui",
        }}
      >
        <div
          style={{
            width: 140,
            height: 140,
            borderRadius: 32,
            background: "white",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            color: "#128C7E",
            fontWeight: 900,
            fontSize: 96,
            marginBottom: 28,
            letterSpacing: "-6px",
          }}
        >
          W
        </div>
        <div style={{ fontWeight: 800, fontSize: 84, marginBottom: 16 }}>
          Whatly
        </div>
        <div style={{ fontSize: 36, opacity: 0.95, marginBottom: 32 }}>
          ₹399/mo · 6 भाषाएं · 14-day free trial
        </div>
        <div
          style={{
            fontSize: 28,
            opacity: 0.9,
            background: "rgba(255,255,255,0.15)",
            padding: "16px 32px",
            borderRadius: 16,
          }}
        >
          Auto-reply · Orders · Payments · No card needed
        </div>
      </div>
    ),
    { ...size },
  );
}
