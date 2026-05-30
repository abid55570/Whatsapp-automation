import { ImageResponse } from "next/og";

export const runtime = "edge";
export const size = { width: 32, height: 32 };
export const contentType = "image/png";

/** Whatly favicon — WhatsApp green "W". */
export default function Icon() {
  return new ImageResponse(
    (
      <div
        style={{
          background: "#25D366",
          width: "100%",
          height: "100%",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          borderRadius: 8,
          color: "white",
          fontSize: 20,
          fontFamily: "system-ui, sans-serif",
          fontWeight: 900,
          letterSpacing: "-1px",
        }}
      >
        W
      </div>
    ),
    { ...size },
  );
}
