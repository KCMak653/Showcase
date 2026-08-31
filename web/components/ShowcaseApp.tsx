"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import TasteSetup from "@/components/TasteSetup";
import {
  CITIES,
  MOCK_SHOWS,
  type City,
  formatShowDate,
  nearestCity,
} from "@/lib/mock-data";
import {
  matchBadge,
  scoreAndRankShows,
  type ScoredShow,
} from "@/lib/taste/scoring";
import type { TastePreferences } from "@/lib/taste/types";

type Step = "landing" | "taste" | "place" | "preview" | "living";

type SpotifyUser = {
  id: string;
  displayName: string;
  email?: string;
  imageUrl?: string;
};

type SyncResult = {
  playlistId: string;
  playlistUrl: string;
  playlistName: string;
  trackCount: number;
  artistCount: number;
  skippedArtists: string[];
  matchedShows: number;
  syncedAt: string;
};

export default function ShowcaseApp() {
  const [step, setStep] = useState<Step>("landing");
  const [user, setUser] = useState<SpotifyUser | null>(null);
  const [taste, setTaste] = useState<TastePreferences | null>(null);
  const [authLoading, setAuthLoading] = useState(true);
  const [city, setCity] = useState<City | null>(null);
  const [includeOpeners, setIncludeOpeners] = useState(false);
  const [tracksPerArtist, setTracksPerArtist] = useState(2);
  const [showAllActs, setShowAllActs] = useState(false);
  const [locating, setLocating] = useState(false);
  const [waitlistEmail, setWaitlistEmail] = useState("");
  const [waitlistSent, setWaitlistSent] = useState(false);
  const [syncLoading, setSyncLoading] = useState(false);
  const [syncResult, setSyncResult] = useState<SyncResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  const { ranked, hidden } = useMemo(() => {
    if (!taste) {
      return { ranked: [] as ScoredShow[], hidden: [] as ScoredShow[] };
    }
    return scoreAndRankShows(MOCK_SHOWS, taste, includeOpeners);
  }, [taste, includeOpeners]);

  const displayShows = showAllActs ? [...ranked, ...hidden] : ranked;

  const loadSession = useCallback(async () => {
    try {
      const res = await fetch("/api/auth/me");
      const data = await res.json();
      if (data.authenticated) {
        setUser(data.user);
        if (data.taste) {
          setTaste(data.taste);
          setStep("place");
        } else {
          setStep("taste");
        }
      }
    } catch {
      setError("Could not check login status.");
    } finally {
      setAuthLoading(false);
    }
  }, []);

  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const urlError = params.get("error");
    const connected = params.get("connected");

    if (urlError) {
      setError(decodeURIComponent(urlError));
      window.history.replaceState({}, "", "/");
    } else if (connected) {
      window.history.replaceState({}, "", "/");
    }

    loadSession();
  }, [loadSession]);

  function connectSpotify() {
    window.location.href = "/api/auth/login";
  }

  async function disconnect() {
    await fetch("/api/auth/logout", { method: "POST" });
    setUser(null);
    setTaste(null);
    setSyncResult(null);
    setCity(null);
    setStep("landing");
  }

  function handleTasteComplete(prefs: TastePreferences) {
    setTaste(prefs);
    setStep("place");
  }

  function selectCity(selected: City) {
    setCity(selected);
    setSyncResult(null);
    if (selected.isSupported) {
      setStep("preview");
    }
  }

  function useLocation() {
    if (!navigator.geolocation) return;
    setLocating(true);
    navigator.geolocation.getCurrentPosition(
      (pos) => {
        selectCity(nearestCity(pos.coords.latitude, pos.coords.longitude));
        setLocating(false);
      },
      () => setLocating(false),
    );
  }

  async function syncPlaylist() {
    if (!city || !taste) return;
    setSyncLoading(true);
    setError(null);

    try {
      const res = await fetch("/api/playlist/sync", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          cityName: city.name,
          citySlug: city.slug,
          includeOpeners,
          tracksPerArtist,
          shows: MOCK_SHOWS,
        }),
      });

      const data = await res.json();
      if (!res.ok) {
        throw new Error(data.error ?? "Failed to create playlist");
      }

      setSyncResult(data as SyncResult);
      setStep("living");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Sync failed");
    } finally {
      setSyncLoading(false);
    }
  }

  const lastSynced = syncResult ? new Date(syncResult.syncedAt) : null;
  const nextSync = lastSynced ? new Date(lastSynced) : null;
  if (nextSync) nextSync.setHours(nextSync.getHours() + 24);

  return (
    <div className="min-h-screen bg-[#0a0a0b] text-[#f5f0e8]">
      <div className="mx-auto flex min-h-screen max-w-2xl flex-col px-6 py-12 sm:px-10 sm:py-16">
        <header className="mb-16 flex items-start justify-between gap-4">
          <p className="text-xs uppercase tracking-[0.35em] text-[#8a8278]">
            Showcase
          </p>
          {user && (
            <div className="flex items-center gap-3">
              {user.imageUrl && (
                // eslint-disable-next-line @next/next/no-img-element
                <img
                  src={user.imageUrl}
                  alt=""
                  className="h-8 w-8 rounded-full"
                />
              )}
              <span className="hidden text-sm text-[#a39e94] sm:inline">
                {user.displayName}
              </span>
              {taste && step !== "taste" && (
                <button
                  type="button"
                  onClick={() => setStep("taste")}
                  className="text-xs uppercase tracking-wider text-[#6b6560] hover:text-[#f5f0e8]"
                >
                  Edit taste
                </button>
              )}
              <button
                type="button"
                onClick={disconnect}
                className="text-xs uppercase tracking-wider text-[#6b6560] hover:text-[#f5f0e8]"
              >
                Disconnect
              </button>
            </div>
          )}
        </header>

        {error && (
          <div className="mb-8 rounded-2xl border border-red-900/50 bg-red-950/30 px-5 py-4 text-sm text-red-200">
            {error}
          </div>
        )}

        <main className="flex flex-1 flex-col">
          {authLoading && (
            <p className="text-[#6b6560]">Checking Spotify connection…</p>
          )}

          {!authLoading && step === "landing" && (
            <section className="flex flex-1 flex-col justify-center">
              <h1 className="font-display text-5xl font-medium leading-[1.05] tracking-tight sm:text-6xl">
                Hear who&apos;s playing near you.
              </h1>
              <p className="mt-6 max-w-md text-lg leading-relaxed text-[#a39e94]">
                One living Spotify playlist, tuned to your taste and refreshed
                with upcoming local acts.
              </p>
              <button
                type="button"
                onClick={connectSpotify}
                className="mt-12 inline-flex w-fit items-center gap-3 rounded-full bg-[#1db954] px-8 py-4 text-base font-medium text-black transition hover:bg-[#1ed760]"
              >
                <SpotifyIcon />
                Connect with Spotify
              </button>
            </section>
          )}

          {step === "taste" && user && (
            <TasteSetup initialTaste={taste} onComplete={handleTasteComplete} />
          )}

          {step === "place" && user && taste && (
            <section className="flex flex-1 flex-col">
              <h2 className="font-display text-4xl font-medium tracking-tight sm:text-5xl">
                Where are you listening?
              </h2>
              <button
                type="button"
                onClick={useLocation}
                disabled={locating}
                className="mt-10 w-full rounded-2xl border border-[#2a2826] bg-[#141414] px-6 py-5 text-left transition hover:border-[#3d3a36]"
              >
                <span className="block text-sm uppercase tracking-widest text-[#8a8278]">
                  Location
                </span>
                <span className="mt-1 block text-xl">
                  {locating ? "Finding your city…" : "Use my location"}
                </span>
              </button>

              <p className="my-8 text-center text-sm text-[#6b6560]">
                or pick a city
              </p>

              <ul className="space-y-3">
                {CITIES.map((c) => (
                  <li key={c.slug}>
                    <button
                      type="button"
                      onClick={() => selectCity(c)}
                      className="flex w-full items-center justify-between rounded-2xl border border-[#2a2826] px-6 py-4 text-left transition hover:border-[#3d3a36] hover:bg-[#141414]"
                    >
                      <span className="text-lg">{c.name}</span>
                      {!c.isSupported && (
                        <span className="text-xs uppercase tracking-wider text-[#8a8278]">
                          Coming soon
                        </span>
                      )}
                    </button>
                  </li>
                ))}
              </ul>

              {city && !city.isSupported && (
                <div className="mt-10 rounded-2xl border border-[#2a2826] bg-[#141414] p-6">
                  <h3 className="text-xl font-medium">
                    {city.name} isn&apos;t live yet
                  </h3>
                  <p className="mt-2 text-[#a39e94]">
                    Join the waitlist and we&apos;ll notify you when{" "}
                    {city.name} launches.
                  </p>
                  {!waitlistSent ? (
                    <form
                      className="mt-6 flex gap-3"
                      onSubmit={(e) => {
                        e.preventDefault();
                        setWaitlistSent(true);
                      }}
                    >
                      <input
                        type="email"
                        placeholder="you@email.com"
                        value={waitlistEmail}
                        onChange={(e) => setWaitlistEmail(e.target.value)}
                        className="flex-1 rounded-full border border-[#2a2826] bg-[#0a0a0b] px-5 py-3 text-sm outline-none focus:border-[#8a8278]"
                      />
                      <button
                        type="submit"
                        className="rounded-full bg-[#f5f0e8] px-6 py-3 text-sm font-medium text-black"
                      >
                        Notify me
                      </button>
                    </form>
                  ) : (
                    <p className="mt-6 text-sm text-[#1db954]">
                      You&apos;re on the list for {city.name}.
                    </p>
                  )}
                </div>
              )}
            </section>
          )}

          {step === "preview" && city?.isSupported && taste && (
            <section className="flex flex-1 flex-col">
              <p className="text-xs uppercase tracking-[0.35em] text-[#8a8278]">
                {city.name}
              </p>
              <h2 className="mt-3 font-display text-4xl font-medium tracking-tight sm:text-5xl">
                Shows for you
              </h2>
              <p className="mt-3 text-[#a39e94]">
                {ranked.length} matches · ranked by your taste
              </p>

              <div className="mt-8 flex flex-wrap gap-4 text-sm">
                <label className="flex items-center gap-2">
                  <input
                    type="checkbox"
                    checked={includeOpeners}
                    onChange={(e) => setIncludeOpeners(e.target.checked)}
                    className="rounded border-[#3d3a36]"
                  />
                  Include openers
                </label>
                <label className="flex items-center gap-2">
                  Tracks per artist
                  <select
                    value={tracksPerArtist}
                    onChange={(e) =>
                      setTracksPerArtist(Number(e.target.value))
                    }
                    className="rounded-lg border border-[#2a2826] bg-[#141414] px-2 py-1"
                  >
                    {[1, 2, 3].map((n) => (
                      <option key={n} value={n}>
                        {n}
                      </option>
                    ))}
                  </select>
                </label>
              </div>

              {ranked.length === 0 ? (
                <div className="mt-10 rounded-2xl border border-[#2a2826] bg-[#141414] p-6">
                  <p className="text-[#a39e94]">
                    No shows match your taste filters. Widen languages or raise
                    the discovery slider.
                  </p>
                  <button
                    type="button"
                    onClick={() => setStep("taste")}
                    className="mt-4 text-sm underline underline-offset-4"
                  >
                    Edit taste
                  </button>
                </div>
              ) : (
                <ul className="mt-10 space-y-4">
                  {displayShows.map((show) => (
                    <li
                      key={show.id}
                      className={`flex gap-5 rounded-2xl border bg-[#141414] p-5 ${
                        show.matchLabel === "hidden"
                          ? "border-[#1a1918] opacity-60"
                          : "border-[#2a2826]"
                      }`}
                    >
                      <div className="flex h-16 w-16 shrink-0 items-center justify-center rounded-xl bg-[#1a1918] text-2xl font-medium text-[#8a8278]">
                        {show.bandName.charAt(0)}
                      </div>
                      <div className="min-w-0 flex-1">
                        <div className="flex flex-wrap items-center gap-2">
                          <h3 className="truncate text-lg font-medium">
                            {show.bandName}
                          </h3>
                          {show.matchLabel !== "hidden" && (
                            <span
                              className={`rounded-full px-2.5 py-0.5 text-xs ${
                                show.matchLabel === "strong"
                                  ? "bg-[#1db954]/20 text-[#1db954]"
                                  : show.matchLabel === "good"
                                    ? "bg-[#8a8278]/20 text-[#c4bdb3]"
                                    : "bg-[#2a2826] text-[#6b6560]"
                              }`}
                            >
                              {matchBadge(show.matchLabel)}
                            </span>
                          )}
                        </div>
                        <p className="mt-1 text-[#a39e94]">{show.venue}</p>
                        <p className="mt-1 text-sm text-[#6b6560]">
                          {formatShowDate(show.showStartTime)}
                          {show.showOrder === "OPENER" && " · Opener"}
                        </p>
                      </div>
                    </li>
                  ))}
                </ul>
              )}

              {hidden.length > 0 && !showAllActs && (
                <button
                  type="button"
                  onClick={() => setShowAllActs(true)}
                  className="mt-6 text-sm text-[#6b6560] underline-offset-4 hover:underline"
                >
                  Show {hidden.length} more local acts outside your lane
                </button>
              )}

              <button
                type="button"
                onClick={syncPlaylist}
                disabled={syncLoading || ranked.length === 0}
                className="mt-12 w-full rounded-full bg-[#f5f0e8] py-4 text-base font-medium text-black transition hover:bg-white disabled:opacity-50"
              >
                {syncLoading ? "Creating playlist…" : "Start my Showcase"}
              </button>
              <p className="mt-3 text-center text-sm text-[#6b6560]">
                {ranked.length} artists → Showcase · {city.name}
              </p>
            </section>
          )}

          {step === "living" && city && syncResult && (
            <section className="flex flex-1 flex-col">
              <div className="rounded-3xl border border-[#2a2826] bg-gradient-to-br from-[#1a1918] to-[#0f0f0f] p-8 sm:p-10">
                <p className="text-xs uppercase tracking-[0.35em] text-[#1db954]">
                  Live
                </p>
                <h2 className="mt-4 font-display text-4xl font-medium tracking-tight">
                  {syncResult.playlistName}
                </h2>
                <p className="mt-3 text-[#a39e94]">
                  {syncResult.matchedShows} matched acts ·{" "}
                  {syncResult.trackCount} tracks in Spotify
                </p>

                {syncResult.skippedArtists.length > 0 && (
                  <p className="mt-3 text-sm text-[#8a8278]">
                    Could not match on Spotify:{" "}
                    {syncResult.skippedArtists.join(", ")}
                  </p>
                )}

                {lastSynced && (
                  <dl className="mt-10 grid gap-6 sm:grid-cols-2">
                    <div>
                      <dt className="text-xs uppercase tracking-widest text-[#6b6560]">
                        Last synced
                      </dt>
                      <dd className="mt-1 text-lg">
                        {lastSynced.toLocaleString("en-CA", {
                          dateStyle: "medium",
                          timeStyle: "short",
                        })}
                      </dd>
                    </div>
                    {nextSync && (
                      <div>
                        <dt className="text-xs uppercase tracking-widest text-[#6b6560]">
                          Next refresh
                        </dt>
                        <dd className="mt-1 text-lg">
                          {nextSync.toLocaleString("en-CA", {
                            dateStyle: "medium",
                            timeStyle: "short",
                          })}
                        </dd>
                      </div>
                    )}
                  </dl>
                )}
              </div>

              <a
                href={syncResult.playlistUrl}
                target="_blank"
                rel="noopener noreferrer"
                className="mt-8 inline-flex items-center justify-center gap-2 rounded-full bg-[#1db954] py-4 text-sm font-medium text-black transition hover:bg-[#1ed760]"
              >
                <SpotifyIcon className="h-4 w-4" />
                Open in Spotify
              </a>

              <button
                type="button"
                onClick={syncPlaylist}
                disabled={syncLoading}
                className="mt-4 rounded-full border border-[#2a2826] py-4 text-sm transition hover:border-[#3d3a36] disabled:opacity-50"
              >
                {syncLoading ? "Syncing…" : "Sync playlist now"}
              </button>

              <button
                type="button"
                onClick={() => setStep("preview")}
                className="mt-4 text-sm text-[#6b6560] underline-offset-4 hover:underline"
              >
                Back to preview
              </button>
            </section>
          )}
        </main>

        {step !== "landing" && !authLoading && (
          <footer className="mt-16 border-t border-[#1a1918] pt-6">
            <nav className="flex flex-wrap gap-4 text-xs uppercase tracking-widest text-[#6b6560]">
              {(["landing", "taste", "place", "preview", "living"] as Step[]).map(
                (s, i) => (
                  <span
                    key={s}
                    className={step === s ? "text-[#f5f0e8]" : undefined}
                  >
                    {i + 1}. {s}
                  </span>
                ),
              )}
            </nav>
          </footer>
        )}
      </div>
    </div>
  );
}

function SpotifyIcon({ className = "h-5 w-5" }: { className?: string }) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="currentColor">
      <path d="M12 0C5.4 0 0 5.4 0 12s5.4 12 12 12 12-5.4 12-12S18.66 0 12 0zm5.521 17.34c-.24.359-.66.48-1.021.24-2.82-1.74-6.36-2.101-10.561-1.141-.418.122-.779-.179-.899-.539-.12-.421.18-.78.54-.9 4.56-1.021 8.52-.6 11.64 1.32.42.18.479.659.301 1.02zm1.44-3.3c-.301.42-.841.6-1.262.3-3.239-1.98-8.159-2.58-11.939-1.38-.479.12-1.02-.12-1.14-.6-.12-.48.12-1.021.6-1.141C9.6 9.9 15 10.561 18.72 12.84c.361.181.54.78.241 1.2zm.12-3.36C15.24 8.4 8.82 8.16 5.16 9.301c-.6.179-1.2-.181-1.38-.721-.18-.601.18-1.2.72-1.381 4.26-1.26 11.28-1.02 15.721 1.621.539.3.719 1.02.419 1.56-.299.421-1.02.599-1.559.3z" />
    </svg>
  );
}
