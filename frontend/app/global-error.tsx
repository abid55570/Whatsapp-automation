"use client";

/**
 * Top-level error boundary — catches errors thrown in the root layout.
 * Must include its own <html> and <body>.
 */
export default function GlobalError({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  return (
    <html lang="en">
      <body
        style={{
          fontFamily: "system-ui, -apple-system, sans-serif",
          margin: 0,
          padding: "24px",
          minHeight: "100vh",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          background: "#f8fafc",
        }}
      >
        <div
          style={{
            maxWidth: 420,
            background: "white",
            border: "1px solid #e2e8f0",
            borderRadius: 16,
            padding: 32,
            textAlign: "center",
          }}
        >
          <div style={{ fontSize: 48, marginBottom: 12 }}>⚠️</div>
          <h1 style={{ fontSize: 22, margin: "8px 0", color: "#0f172a" }}>
            Application crashed
          </h1>
          <p style={{ color: "#475569", marginBottom: 24, fontSize: 14 }}>
            Refresh the page to try again. If the problem persists, contact
            support.
          </p>
          <button
            onClick={reset}
            style={{
              background: "#16A34A",
              color: "white",
              padding: "10px 20px",
              borderRadius: 8,
              border: "none",
              fontWeight: 600,
              cursor: "pointer",
              minHeight: 44,
            }}
          >
            Try again
          </button>
        </div>
      </body>
    </html>
  );
}
