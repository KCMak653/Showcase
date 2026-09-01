"use client";

export default function Error({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  return (
    <div className="flex min-h-screen flex-col items-center justify-center bg-[#0a0a0b] px-6 text-[#f5f0e8]">
      <h1 className="font-display text-3xl">Something went wrong</h1>
      <p className="mt-4 max-w-md text-center text-sm text-[#a39e94]">
        {error.message || "An unexpected error occurred."}
      </p>
      <button
        type="button"
        onClick={reset}
        className="mt-8 rounded-full bg-[#f5f0e8] px-6 py-3 text-sm font-medium text-black"
      >
        Try again
      </button>
    </div>
  );
}
