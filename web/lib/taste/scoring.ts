import type { LanguageCode, TastePreferences } from "./types";

export type ScorableShow = {
  id: string;
  bandName: string;
  venue: string;
  showStartTime: string;
  showOrder: "HEADLINER" | "OPENER";
  languageTags: LanguageCode[];
  artistGenres: string[];
  artistPopularity?: number;
};

export type ScoredShow = ScorableShow & {
  score: number;
  matchLabel: "strong" | "good" | "discovery" | "hidden";
  matchReason?: string;
};

function normalize(s: string): string {
  return s.toLowerCase().replace(/-/g, " ").trim();
}

function genreOverlap(showGenres: string[], filters: string[]): number {
  if (filters.length === 0) return 0.5;
  const showSet = new Set(showGenres.map(normalize));
  let hits = 0;
  for (const f of filters) {
    const nf = normalize(f);
    for (const sg of showSet) {
      if (sg.includes(nf) || nf.includes(sg)) {
        hits += 1;
        break;
      }
    }
  }
  return hits / filters.length;
}

function languageMatch(
  showTags: LanguageCode[],
  filters: LanguageCode[],
): boolean {
  if (filters.length === 0) return true;
  return showTags.some((t) => filters.includes(t));
}

function recencyBoost(iso: string): number {
  const days =
    (new Date(iso).getTime() - Date.now()) / (1000 * 60 * 60 * 24);
  if (days < 0) return 0;
  if (days <= 14) return 15;
  if (days <= 30) return 8;
  return 0;
}

export function scoreShow(
  show: ScorableShow,
  taste: TastePreferences,
): number {
  if (!languageMatch(show.languageTags, taste.languageFilters)) {
    return 0;
  }

  let score = 25;

  const gOverlap = genreOverlap(show.artistGenres, taste.genreFilters);
  score += Math.round(gOverlap * 40);

  if (taste.genreFilters.length === 0 && taste.snapshot?.topGenres.length) {
    score += Math.round(
      genreOverlap(show.artistGenres, taste.snapshot.topGenres) * 30,
    );
  }

  score += recencyBoost(show.showStartTime);

  if (
    taste.excludeMainstream &&
    show.artistPopularity != null &&
    show.artistPopularity > 80
  ) {
    score -= 25;
  }

  const discoveryBoost = Math.round((taste.discoveryLevel / 100) * 20);
  if (score < 50) {
    score += discoveryBoost;
  }

  return Math.max(0, Math.min(100, score));
}

export function scoreAndRankShows(
  shows: ScorableShow[],
  taste: TastePreferences,
  includeOpeners: boolean,
): { ranked: ScoredShow[]; hidden: ScoredShow[] } {
  const pool = includeOpeners
    ? shows
    : shows.filter((s) => s.showOrder === "HEADLINER");

  const scored = pool.map((show) => {
    const score = scoreShow(show, taste);
    let matchLabel: ScoredShow["matchLabel"] = "hidden";
    if (score >= 70) matchLabel = "strong";
    else if (score >= 50) matchLabel = "good";
    else if (score >= taste.minMatchScore) matchLabel = "discovery";

    let matchReason: string | undefined;
    if (show.languageTags.length) {
      const langs = show.languageTags.join(", ");
      matchReason = `${langs} · ${show.artistGenres.slice(0, 2).join(", ") || "local act"}`;
    }

    return { ...show, score, matchLabel, matchReason };
  });

  scored.sort((a, b) => {
    if (b.score !== a.score) return b.score - a.score;
    return (
      new Date(a.showStartTime).getTime() -
      new Date(b.showStartTime).getTime()
    );
  });

  const effectiveMin =
    taste.minMatchScore - Math.round((taste.discoveryLevel / 100) * 15);

  const ranked = scored.filter((s) => s.score >= effectiveMin);
  const hidden = scored.filter((s) => s.score < effectiveMin);

  return { ranked, hidden };
}

export function matchBadge(label: ScoredShow["matchLabel"]): string {
  switch (label) {
    case "strong":
      return "Strong match";
    case "good":
      return "Worth a look";
    case "discovery":
      return "Outside your lane";
    default:
      return "";
  }
}
