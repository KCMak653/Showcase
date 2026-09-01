import { cookies } from "next/headers";
import type { TastePreferences } from "@/lib/taste/types";
import { DEFAULT_TASTE } from "@/lib/taste/types";

export type SpotifyUser = {
  id: string;
  displayName: string;
  email?: string;
  imageUrl?: string;
};

export type SpotifySession = {
  accessToken: string;
  refreshToken: string;
  expiresAt: number;
  user: SpotifyUser;
  playlistId?: string;
  playlistCity?: string;
};

const COOKIE_OPTIONS = {
  httpOnly: true,
  secure: process.env.NODE_ENV === "production",
  sameSite: "lax" as const,
  path: "/",
};

export async function getSession(): Promise<SpotifySession | null> {
  const jar = await cookies();
  const accessToken = jar.get("showcase_access_token")?.value;
  const refreshToken = jar.get("showcase_refresh_token")?.value;
  const expiresAt = jar.get("showcase_expires_at")?.value;
  const userRaw = jar.get("showcase_user")?.value;

  if (!accessToken || !refreshToken || !expiresAt || !userRaw) {
    return null;
  }

  let user: SpotifyUser;
  try {
    user = JSON.parse(userRaw) as SpotifyUser;
  } catch {
    return null;
  }

  return {
    accessToken,
    refreshToken,
    expiresAt: Number(expiresAt),
    user,
    playlistId: jar.get("showcase_playlist_id")?.value,
    playlistCity: jar.get("showcase_playlist_city")?.value,
  };
}

export async function setSession(
  session: Omit<SpotifySession, "playlistId" | "playlistCity">,
): Promise<void> {
  const jar = await cookies();
  const maxAge = 60 * 60 * 24 * 30;

  jar.set("showcase_access_token", session.accessToken, {
    ...COOKIE_OPTIONS,
    maxAge,
  });
  jar.set("showcase_refresh_token", session.refreshToken, {
    ...COOKIE_OPTIONS,
    maxAge,
  });
  jar.set("showcase_expires_at", String(session.expiresAt), {
    ...COOKIE_OPTIONS,
    maxAge,
  });
  jar.set("showcase_user", JSON.stringify(session.user), {
    ...COOKIE_OPTIONS,
    maxAge,
  });
}

export async function setPlaylistMeta(
  playlistId: string,
  citySlug: string,
): Promise<void> {
  const jar = await cookies();
  const maxAge = 60 * 60 * 24 * 30;
  jar.set("showcase_playlist_id", playlistId, { ...COOKIE_OPTIONS, maxAge });
  jar.set("showcase_playlist_city", citySlug, { ...COOKIE_OPTIONS, maxAge });
}

export async function clearSession(): Promise<void> {
  const jar = await cookies();
  for (const name of [
    "showcase_access_token",
    "showcase_refresh_token",
    "showcase_expires_at",
    "showcase_user",
    "showcase_playlist_id",
    "showcase_playlist_city",
    "showcase_pkce_verifier",
    "showcase_taste",
  ]) {
    jar.delete(name);
  }
}

export async function setPkceVerifier(verifier: string): Promise<void> {
  const jar = await cookies();
  jar.set("showcase_pkce_verifier", verifier, {
    ...COOKIE_OPTIONS,
    maxAge: 600,
  });
}

export async function consumePkceVerifier(): Promise<string | null> {
  const jar = await cookies();
  const verifier = jar.get("showcase_pkce_verifier")?.value ?? null;
  jar.delete("showcase_pkce_verifier");
  return verifier;
}

export async function getTastePreferences(): Promise<TastePreferences | null> {
  const jar = await cookies();
  const raw = jar.get("showcase_taste")?.value;
  if (!raw) return null;
  try {
    return JSON.parse(raw) as TastePreferences;
  } catch {
    return null;
  }
}

export async function setTastePreferences(
  taste: TastePreferences,
): Promise<void> {
  const jar = await cookies();
  jar.set("showcase_taste", JSON.stringify(taste), {
    ...COOKIE_OPTIONS,
    maxAge: 60 * 60 * 24 * 30,
  });
}

export async function hasTastePreferences(): Promise<boolean> {
  const taste = await getTastePreferences();
  return taste != null && taste.languageFilters.length > 0;
}

export { DEFAULT_TASTE };
