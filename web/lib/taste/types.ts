export type LanguageCode = "en" | "yue" | "cmn" | "ja" | "ko" | "other";

export type TasteSnapshot = {
  topArtistNames: string[];
  topGenres: string[];
  inferredLanguages: LanguageCode[];
  summary: string;
  analyzedAt: string;
};

export type TastePreferences = {
  languageFilters: LanguageCode[];
  genreFilters: string[];
  discoveryLevel: number;
  excludeMainstream: boolean;
  minMatchScore: number;
  snapshot?: TasteSnapshot;
};

export const DEFAULT_TASTE: TastePreferences = {
  languageFilters: ["en"],
  genreFilters: [],
  discoveryLevel: 30,
  excludeMainstream: false,
  minMatchScore: 30,
};

export const LANGUAGE_OPTIONS: {
  code: LanguageCode;
  label: string;
  native?: string;
}[] = [
  { code: "en", label: "English" },
  { code: "yue", label: "Cantonese", native: "粵語" },
  { code: "cmn", label: "Mandarin", native: "普通話" },
  { code: "ja", label: "Japanese", native: "日本語" },
  { code: "ko", label: "Korean", native: "한국어" },
  { code: "other", label: "Other" },
];

export const GENRE_SUGGESTIONS = [
  "indie",
  "rock",
  "pop",
  "cantopop",
  "mandopop",
  "jazz",
  "electronic",
  "hip-hop",
  "folk",
  "metal",
  "r&b",
  "classical",
  "punk",
  "soul",
  "alternative",
  "shoegaze",
  "psychedelic",
];

/** Map Spotify genre strings to language codes. */
const GENRE_LANGUAGE_MAP: Record<string, LanguageCode> = {
  cantopop: "yue",
  "hong kong indie": "yue",
  mandopop: "cmn",
  "chinese indie": "cmn",
  "j-pop": "ja",
  "j-poprock": "ja",
  "k-pop": "ko",
  "k-pop ballad": "ko",
};

export function inferLanguagesFromGenres(genres: string[]): LanguageCode[] {
  const found = new Set<LanguageCode>();
  for (const g of genres) {
    const key = g.toLowerCase();
    if (GENRE_LANGUAGE_MAP[key]) {
      found.add(GENRE_LANGUAGE_MAP[key]);
    }
    if (key.includes("cantopop") || key.includes("canto")) found.add("yue");
    if (key.includes("mandopop") || key.includes("mandarin")) found.add("cmn");
    if (key.includes("j-pop") || key.includes("japanese")) found.add("ja");
    if (key.includes("k-pop") || key.includes("korean")) found.add("ko");
  }
  if (genres.some((g) => !Object.keys(GENRE_LANGUAGE_MAP).includes(g.toLowerCase()))) {
    found.add("en");
  }
  return found.size ? [...found] : ["en"];
}

export function buildTasteSummary(
  genres: string[],
  languages: LanguageCode[],
): string {
  const langLabels = languages
    .map((c) => LANGUAGE_OPTIONS.find((o) => o.code === c)?.label)
    .filter(Boolean)
    .slice(0, 3);
  const topGenres = genres.slice(0, 3).map((g) => g.replace(/-/g, " "));
  if (topGenres.length === 0 && langLabels.length > 0) {
    return `Mostly ${langLabels.join(" and ")} — based on your Spotify`;
  }
  if (topGenres.length > 0 && langLabels.length > 0) {
    return `${topGenres.join(", ")} · ${langLabels.join(" & ")} — from your Spotify`;
  }
  return "Based on your Spotify listening";
}
