"use client";

import { useEffect, useState } from "react";
import {
  DEFAULT_TASTE,
  GENRE_SUGGESTIONS,
  LANGUAGE_OPTIONS,
  type LanguageCode,
  type TastePreferences,
  type TasteSnapshot,
} from "@/lib/taste/types";

type Props = {
  initialTaste?: TastePreferences | null;
  onComplete: (taste: TastePreferences) => void;
};

export default function TasteSetup({ initialTaste, onComplete }: Props) {
  const [languages, setLanguages] = useState<LanguageCode[]>(
    initialTaste?.languageFilters ?? DEFAULT_TASTE.languageFilters,
  );
  const [genres, setGenres] = useState<string[]>(
    initialTaste?.genreFilters ?? [],
  );
  const [discoveryLevel, setDiscoveryLevel] = useState(
    initialTaste?.discoveryLevel ?? DEFAULT_TASTE.discoveryLevel,
  );
  const [excludeMainstream, setExcludeMainstream] = useState(
    initialTaste?.excludeMainstream ?? false,
  );
  const [snapshot, setSnapshot] = useState<TasteSnapshot | undefined>(
    initialTaste?.snapshot,
  );
  const [analyzing, setAnalyzing] = useState(!initialTaste?.snapshot);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (initialTaste?.snapshot) {
      setAnalyzing(false);
      return;
    }

    let cancelled = false;
    (async () => {
      try {
        const res = await fetch("/api/taste/analyze");
        const data = await res.json();
        if (cancelled) return;
        if (!res.ok) {
          setError(data.error ?? "Could not analyze your Spotify library.");
          setAnalyzing(false);
          return;
        }
        setSnapshot(data as TasteSnapshot);
        setLanguages(data.inferredLanguages?.length ? data.inferredLanguages : ["en"]);
        if (data.topGenres?.length) {
          setGenres(
            data.topGenres
              .slice(0, 5)
              .map((g: string) => g.replace(/-/g, " ")),
          );
        }
      } catch {
        if (!cancelled) setError("Could not reach Spotify for taste analysis.");
      } finally {
        if (!cancelled) setAnalyzing(false);
      }
    })();

    return () => {
      cancelled = true;
    };
  }, [initialTaste?.snapshot]);

  function toggleLanguage(code: LanguageCode) {
    setLanguages((prev) =>
      prev.includes(code)
        ? prev.length > 1
          ? prev.filter((c) => c !== code)
          : prev
        : [...prev, code],
    );
  }

  function toggleGenre(genre: string) {
    const key = genre.toLowerCase();
    setGenres((prev) =>
      prev.map((g) => g.toLowerCase()).includes(key)
        ? prev.filter((g) => g.toLowerCase() !== key)
        : [...prev, genre],
    );
  }

  async function handleSubmit() {
    setSaving(true);
    setError(null);
    const taste: TastePreferences = {
      languageFilters: languages,
      genreFilters: genres,
      discoveryLevel,
      excludeMainstream,
      minMatchScore: DEFAULT_TASTE.minMatchScore,
      snapshot,
    };

    try {
      const res = await fetch("/api/taste", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(taste),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error ?? "Save failed");
      onComplete(data.taste as TastePreferences);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Save failed");
    } finally {
      setSaving(false);
    }
  }

  return (
    <section className="flex flex-1 flex-col">
      <p className="text-xs uppercase tracking-[0.35em] text-[#8a8278]">
        Your taste
      </p>
      <h2 className="mt-3 font-display text-4xl font-medium tracking-tight sm:text-5xl">
        What do you listen to?
      </h2>
      <p className="mt-4 max-w-md text-[#a39e94]">
        Local lineups aren&apos;t one-size-fits-all. Tell us your languages and
        genres so we surface shows you&apos;d actually go to.
      </p>

      {analyzing && (
        <p className="mt-8 text-sm text-[#6b6560]">
          Reading your Spotify top artists and liked songs…
        </p>
      )}

      {snapshot && !analyzing && (
        <div className="mt-8 rounded-2xl border border-[#2a2826] bg-[#141414] px-5 py-4">
          <p className="text-xs uppercase tracking-widest text-[#1db954]">
            From your Spotify
          </p>
          <p className="mt-2 text-lg">{snapshot.summary}</p>
          {snapshot.topArtistNames.length > 0 && (
            <p className="mt-2 text-sm text-[#6b6560]">
              Top artists: {snapshot.topArtistNames.slice(0, 4).join(", ")}
              {snapshot.topArtistNames.length > 4 ? "…" : ""}
            </p>
          )}
        </div>
      )}

      {error && (
        <p className="mt-4 text-sm text-amber-200/80">{error}</p>
      )}

      <div className="mt-10">
        <h3 className="text-sm uppercase tracking-widest text-[#8a8278]">
          Languages
        </h3>
        <div className="mt-4 flex flex-wrap gap-3">
          {LANGUAGE_OPTIONS.map((opt) => {
            const active = languages.includes(opt.code);
            return (
              <button
                key={opt.code}
                type="button"
                onClick={() => toggleLanguage(opt.code)}
                className={`rounded-full border px-5 py-2.5 text-sm transition ${
                  active
                    ? "border-[#f5f0e8] bg-[#f5f0e8] text-black"
                    : "border-[#2a2826] text-[#a39e94] hover:border-[#3d3a36]"
                }`}
              >
                {opt.label}
                {opt.native ? (
                  <span className="ml-1.5 opacity-70">{opt.native}</span>
                ) : null}
              </button>
            );
          })}
        </div>
      </div>

      <div className="mt-10">
        <h3 className="text-sm uppercase tracking-widest text-[#8a8278]">
          Genres
        </h3>
        <div className="mt-4 flex flex-wrap gap-2">
          {GENRE_SUGGESTIONS.map((genre) => {
            const active = genres
              .map((g) => g.toLowerCase())
              .includes(genre.toLowerCase());
            return (
              <button
                key={genre}
                type="button"
                onClick={() => toggleGenre(genre)}
                className={`rounded-full border px-4 py-2 text-sm capitalize transition ${
                  active
                    ? "border-[#8a8278] bg-[#1a1918] text-[#f5f0e8]"
                    : "border-[#2a2826] text-[#6b6560] hover:border-[#3d3a36]"
                }`}
              >
                {genre}
              </button>
            );
          })}
        </div>
      </div>

      <div className="mt-10">
        <div className="flex items-center justify-between">
          <h3 className="text-sm uppercase tracking-widest text-[#8a8278]">
            Discovery
          </h3>
          <span className="text-sm text-[#6b6560]">{discoveryLevel}%</span>
        </div>
        <p className="mt-2 text-sm text-[#6b6560]">
          Stick to my lane ← → Surprise me with local acts
        </p>
        <input
          type="range"
          min={0}
          max={100}
          value={discoveryLevel}
          onChange={(e) => setDiscoveryLevel(Number(e.target.value))}
          className="mt-4 w-full accent-[#1db954]"
        />
      </div>

      <label className="mt-8 flex cursor-pointer items-center gap-3 text-sm">
        <input
          type="checkbox"
          checked={excludeMainstream}
          onChange={(e) => setExcludeMainstream(e.target.checked)}
          className="h-4 w-4 rounded border-[#3d3a36]"
        />
        Deprioritize mainstream headliners (stadium / EDM acts)
      </label>

      <button
        type="button"
        onClick={handleSubmit}
        disabled={saving || analyzing}
        className="mt-12 w-full rounded-full bg-[#f5f0e8] py-4 text-base font-medium text-black transition hover:bg-white disabled:opacity-50"
      >
        {saving ? "Saving…" : "Continue to city"}
      </button>
    </section>
  );
}
