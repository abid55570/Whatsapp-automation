import { ImageResponse } from "next/og";

export const runtime = "edge";
export const size = { width: 180, height: 180 };
export const contentType = "image/png";

/** Whatly Apple-touch icon — green chat bubble with "W". */
export default function AppleIcon() {
  return new ImageResponse(
    (
      <div
        style={{
          width: "100%",
          height: "100%",
          background: "linear-gradient(135deg, #25D366 0%, #128C7E 100%)",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          position: "relative",
        }}
      >
        <svg
          width="120"
          height="120"
          viewBox="0 0 24 24"
          fill="none"
          xmlns="http://www.w3.org/2000/svg"
        >
          <path
            d="M12 2C6.5 2 2 6.04 2 11c0 2.06.78 3.97 2.1 5.51L3 22l5.7-1.84A10.9 10.9 0 0 0 12 21c5.5 0 10-4.03 10-9s-4.5-10-10-10z"
            fill="white"
          />
        </svg>
        <div
          style={{
            position: "absolute",
            color: "#128C7E",
            fontSize: 58,
            fontWeight: 900,
            fontFamily: "system-ui, sans-serif",
            letterSpacing: "-3px",
            marginTop: -6,
          }}
        >
          W
        </div>
      </div>
    ),
    { ...size },
  );
}
