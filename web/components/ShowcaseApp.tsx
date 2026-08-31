"use client";

import { useMemo, useState } from "react";
import {
  CITIES,
  MOCK_SHOWS,
  type City,
  formatShowDate,
  nearestCity,
} from "@/lib/mock-data";

type Step = "landing" | "place" | "preview" | "living";

export default function ShowcaseApp() {
  const [step, setStep] = useState<Step>("landing");
  const [connected, setConnected] = useState(false);
  const [city, setCity] = useState<City | null>(null);
  const [includeOpeners, setIncludeOpeners] = useState(false);
  const [tracksPerArtist, setTracksPerArtist] = useState(2);
  const [paused, setPaused] = useState(false);
  const [locating, setLocating] = useState(false);
  const [waitlistEmail, setWaitlistEmail] = useState("");
  const [waitlistSent, setWaitlistSent] = useState(false);
  const [lastSynced] = useState(() => new Date());

  const shows = useMemo(() => {
    const filtered = includeOpeners
      ? MOCK_SHOWS
      : MOCK_SHOWS.filter((s) => s.showOrder === "HEADLINER");
    return filtered.sort(
      (a, b) =>
        new Date(a.showStartTime).getTime() -
        new Date(b.showStartTime).getTime(),
    );
  }, [includeOpeners]);

  function connectSpotify() {
    setConnected(true);
    setStep("place");
  }

  function selectCity(selected: City) {
    setCity(selected);
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

  function startPlaylist() {
    setStep("living");
  }

  const nextSync = new Date(lastSynced);
  nextSync.setHours(nextSync.getHours() + 24);

  return (
    <div className="min-h-screen bg-[#0a0a0b] text-[#f5f0e8]">
      <div className="mx-auto flex min-h-screen max-w-2xl flex-col px-6 py-12 sm:px-10 sm:py-16">
        <header className="mb-16">
          <p className="text-xs uppercase tracking-[0.35em] text-[#8a8278]">
            Showcase
          </p>
        </header>

        <main className="flex flex-1 flex-col">
          {step === "landing" && (
            <section className="flex flex-1 flex-col justify-center">
              <h1 className="font-display text-5xl font-medium leading-[1.05] tracking-tight sm:text-6xl">
                Hear who&apos;s playing near you.
              </h1>
              <p className="mt-6 max-w-md text-lg leading-relaxed text-[#a39e94]">
                One living Spotify playlist, refreshed with upcoming local acts
                in your city.
              </p>
              <button
                type="button"
                onClick={connectSpotify}
                className="mt-12 inline-flex w-fit items-center gap-3 rounded-full bg-[#1db954] px-8 py-4 text-base font-medium text-black transition hover:bg-[#1ed760]"
              >
                <SpotifyIcon />
                Connect with Spotify
              </button>
              <p className="mt-4 text-sm text-[#6b6560]">
                Preview mode — OAuth not wired yet
              </p>
            </section>
          )}

          {step === "place" && connected && (
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

              <p className="my-8 text-center text-sm text-[#6b6560]">or pick a city</p>

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
                    We&apos;re building city by city. Join the waitlist and
                    we&apos;ll notify you when {city.name} launches.
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

          {step === "preview" && city?.isSupported && (
            <section className="flex flex-1 flex-col">
              <p className="text-xs uppercase tracking-[0.35em] text-[#8a8278]">
                {city.name}
              </p>
              <h2 className="mt-3 font-display text-4xl font-medium tracking-tight sm:text-5xl">
                Upcoming shows
              </h2>
              <p className="mt-3 text-[#a39e94]">Next 30 days · headliners</p>

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

              <ul className="mt-10 space-y-4">
                {shows.map((show) => (
                  <li
                    key={show.id}
                    className="flex gap-5 rounded-2xl border border-[#2a2826] bg-[#141414] p-5"
                  >
                    <div className="flex h-16 w-16 shrink-0 items-center justify-center rounded-xl bg-[#1a1918] text-2xl font-medium text-[#8a8278]">
                      {show.bandName.charAt(0)}
                    </div>
                    <div className="min-w-0 flex-1">
                      <h3 className="truncate text-lg font-medium">
                        {show.bandName}
                      </h3>
                      <p className="mt-1 text-[#a39e94]">{show.venue}</p>
                      <p className="mt-1 text-sm text-[#6b6560]">
                        {formatShowDate(show.showStartTime)}
                        {show.showOrder === "OPENER" && " · Opener"}
                      </p>
                    </div>
                  </li>
                ))}
              </ul>

              <button
                type="button"
                onClick={startPlaylist}
                className="mt-12 w-full rounded-full bg-[#f5f0e8] py-4 text-base font-medium text-black transition hover:bg-white"
              >
                Start my Showcase
              </button>
              <p className="mt-3 text-center text-sm text-[#6b6560]">
                Creates Showcase · {city.name} in your Spotify library
              </p>
            </section>
          )}

          {step === "living" && city && (
            <section className="flex flex-1 flex-col">
              <div className="rounded-3xl border border-[#2a2826] bg-gradient-to-br from-[#1a1918] to-[#0f0f0f] p-8 sm:p-10">
                <p className="text-xs uppercase tracking-[0.35em] text-[#1db954]">
                  Live
                </p>
                <h2 className="mt-4 font-display text-4xl font-medium tracking-tight">
                  Showcase · {city.name}
                </h2>
                <p className="mt-3 text-[#a39e94]">
                  {shows.length} artists · {shows.length * tracksPerArtist}{" "}
                  tracks · refreshes daily
                </p>

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
                </dl>

                <label className="mt-10 flex cursor-pointer items-center justify-between rounded-2xl border border-[#2a2826] px-5 py-4">
                  <span>Pause updates</span>
                  <input
                    type="checkbox"
                    checked={paused}
                    onChange={(e) => setPaused(e.target.checked)}
                    className="h-5 w-5 rounded border-[#3d3a36]"
                  />
                </label>

                {paused && (
                  <p className="mt-3 text-sm text-[#8a8278]">
                    Your playlist stays as-is until you resume updates.
                  </p>
                )}
              </div>

              <a
                href="https://open.spotify.com"
                target="_blank"
                rel="noopener noreferrer"
                className="mt-8 inline-flex items-center justify-center gap-2 rounded-full border border-[#2a2826] py-4 text-sm transition hover:border-[#3d3a36]"
              >
                <SpotifyIcon className="h-4 w-4" />
                Open in Spotify
              </a>

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

        {step !== "landing" && (
          <footer className="mt-16 border-t border-[#1a1918] pt-6">
            <nav className="flex gap-4 text-xs uppercase tracking-widest text-[#6b6560]">
              {(["landing", "place", "preview", "living"] as Step[]).map(
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
