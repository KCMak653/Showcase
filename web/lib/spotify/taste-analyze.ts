import { spotifyFetch } from "./client";
import {
  buildTasteSummary,
  inferLanguagesFromGenres,
  type LanguageCode,
  type TasteSnapshot,
} from "@/lib/taste/types";

type SpotifyArtist = {
  id: string;
  name: string;
  genres: string[];
  popularity: number;
};

export async function analyzeSpotifyTaste(): Promise<TasteSnapshot> {
  const topArtistsData = await spotifyFetch<{
    items: { id: string; name: string; genres: string[]; popularity: number }[];
  }>("/me/top/artists?limit=50&time_range=medium_term");

  const topArtists = topArtistsData.items;

  const genreCounts = new Map<string, number>();
  for (const artist of topArtists) {
    for (const genre of artist.genres) {
      genreCounts.set(genre, (genreCounts.get(genre) ?? 0) + 1);
    }
  }

  const topGenres = [...genreCounts.entries()]
    .sort((a, b) => b[1] - a[1])
    .slice(0, 12)
    .map(([g]) => g);

  const inferredLanguages = inferLanguagesFromGenres(topGenres);
  const topArtistNames = topArtists.slice(0, 8).map((a) => a.name);

  let savedGenreBoost: string[] = [];
  try {
    const saved = await spotifyFetch<{
      items: { track: { artists: { id: string; name: string }[] } }[];
    }>("/me/tracks?limit=20");

    const savedArtistIds = new Set<string>();
    for (const item of saved.items) {
      for (const artist of item.track.artists) {
        savedArtistIds.add(artist.id);
      }
    }

    if (savedArtistIds.size > 0) {
      const ids = [...savedArtistIds].slice(0, 20).join(",");
      const artistsData = await spotifyFetch<{ artists: SpotifyArtist[] }>(
        `/artists?ids=${ids}`,
      );
      for (const artist of artistsData.artists) {
        for (const g of artist.genres) {
          genreCounts.set(g, (genreCounts.get(g) ?? 0) + 0.5);
        }
      }
      savedGenreBoost = artistsData.artists.flatMap((a) => a.genres);
    }
  } catch {
    // Saved tracks optional if scope missing on older sessions
  }

  const mergedGenres = [...genreCounts.entries()]
    .sort((a, b) => b[1] - a[1])
    .slice(0, 12)
    .map(([g]) => g);

  const languagesFromSaved = inferLanguagesFromGenres(savedGenreBoost);
  const allLanguages = [
    ...new Set<LanguageCode>([...inferredLanguages, ...languagesFromSaved]),
  ];

  return {
    topArtistNames,
    topGenres: mergedGenres.length ? mergedGenres : topGenres,
    inferredLanguages: allLanguages,
    summary: buildTasteSummary(mergedGenres, allLanguages),
    analyzedAt: new Date().toISOString(),
  };
}
