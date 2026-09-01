import type { LanguageCode } from "@/lib/taste/types";

export type Show = {
  id: string;
  bandName: string;
  venue: string;
  showStartTime: string;
  showOrder: "HEADLINER" | "OPENER";
  languageTags: LanguageCode[];
  artistGenres: string[];
  artistPopularity?: number;
  artistImageUrl?: string;
};

export type City = {
  slug: string;
  name: string;
  isSupported: boolean;
  lat: number;
  lng: number;
};

export const CITIES: City[] = [
  {
    slug: "toronto",
    name: "Toronto",
    isSupported: true,
    lat: 43.6532,
    lng: -79.3832,
  },
  {
    slug: "hong-kong",
    name: "Hong Kong",
    isSupported: false,
    lat: 22.3193,
    lng: 114.1694,
  },
  {
    slug: "montreal",
    name: "Montreal",
    isSupported: false,
    lat: 45.5017,
    lng: -73.5673,
  },
  {
    slug: "vancouver",
    name: "Vancouver",
    isSupported: false,
    lat: 49.2827,
    lng: -123.1207,
  },
];

export const MOCK_SHOWS: Show[] = [
  {
    id: "1",
    bandName: "The Messenger Birds",
    venue: "Horseshoe Tavern",
    showStartTime: "2026-11-21T20:00:00",
    showOrder: "HEADLINER",
    languageTags: ["en"],
    artistGenres: ["indie rock", "alternative rock"],
    artistPopularity: 42,
  },
  {
    id: "2",
    bandName: "GHOSTWOMAN",
    venue: "Horseshoe Tavern",
    showStartTime: "2026-11-27T19:00:00",
    showOrder: "HEADLINER",
    languageTags: ["en"],
    artistGenres: ["shoegaze", "dream pop"],
    artistPopularity: 38,
  },
  {
    id: "3",
    bandName: "Early Tombs",
    venue: "Lee's Palace",
    showStartTime: "2026-10-12T20:30:00",
    showOrder: "OPENER",
    languageTags: ["en"],
    artistGenres: ["post-punk", "indie rock"],
    artistPopularity: 28,
  },
  {
    id: "4",
    bandName: "Dogs",
    venue: "Lee's Palace",
    showStartTime: "2026-10-12T21:00:00",
    showOrder: "HEADLINER",
    languageTags: ["en"],
    artistGenres: ["garage rock", "punk"],
    artistPopularity: 22,
  },
  {
    id: "5",
    bandName: "Florence + The Machine",
    venue: "Massey Hall",
    showStartTime: "2026-10-18T19:30:00",
    showOrder: "HEADLINER",
    languageTags: ["en"],
    artistGenres: ["art pop", "indie rock"],
    artistPopularity: 82,
  },
  {
    id: "6",
    bandName: "Eason Chan",
    venue: "Scotiabank Arena",
    showStartTime: "2026-10-25T19:30:00",
    showOrder: "HEADLINER",
    languageTags: ["yue", "cmn"],
    artistGenres: ["cantopop", "mandopop"],
    artistPopularity: 74,
  },
  {
    id: "7",
    bandName: "My Little Airport",
    venue: "The Great Hall",
    showStartTime: "2026-11-05T20:00:00",
    showOrder: "HEADLINER",
    languageTags: ["yue", "en"],
    artistGenres: ["hong kong indie", "indie pop"],
    artistPopularity: 55,
  },
  {
    id: "8",
    bandName: "DJ Snake",
    venue: "Rebel",
    showStartTime: "2026-10-30T22:00:00",
    showOrder: "HEADLINER",
    languageTags: ["en"],
    artistGenres: ["edm", "electronic"],
    artistPopularity: 85,
  },
];

export function formatShowDate(iso: string): string {
  const d = new Date(iso);
  return d.toLocaleDateString("en-CA", {
    weekday: "short",
    month: "short",
    day: "numeric",
    hour: "numeric",
    minute: "2-digit",
  });
}

export function nearestCity(lat: number, lng: number): City {
  let best = CITIES[0];
  let bestDist = Infinity;
  for (const city of CITIES) {
    const dist = (city.lat - lat) ** 2 + (city.lng - lng) ** 2;
    if (dist < bestDist) {
      bestDist = dist;
      best = city;
    }
  }
  return best;
}
