"use client";

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
          margin: 0,
          minHeight: "100vh",
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          justifyContent: "center",
          background: "#0a0a0b",
          color: "#f5f0e8",
          fontFamily: "system-ui, sans-serif",
          padding: "1.5rem",
        }}
      >
        <h1 style={{ fontSize: "1.75rem", margin: 0 }}>Showcase error</h1>
        <p style={{ marginTop: "1rem", color: "#a39e94", textAlign: "center" }}>
          {error.message || "Something went wrong."}
        </p>
        <button
          type="button"
          onClick={reset}
          style={{
            marginTop: "2rem",
            padding: "0.75rem 1.5rem",
            borderRadius: "9999px",
            border: "none",
            background: "#f5f0e8",
            color: "#000",
            cursor: "pointer",
          }}
        >
          Try again
        </button>
      </body>
    </html>
  );
}
