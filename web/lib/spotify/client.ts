import { getSpotifyConfig } from "./config";
import {
  getSession,
  setSession,
  type SpotifySession,
  type SpotifyUser,
} from "./session";

type TokenResponse = {
  access_token: string;
  refresh_token?: string;
  expires_in: number;
  token_type: string;
};

async function refreshAccessToken(
  refreshToken: string,
): Promise<{ accessToken: string; expiresAt: number; refreshToken: string }> {
  const { clientId, clientSecret } = getSpotifyConfig();
  const body = new URLSearchParams({
    grant_type: "refresh_token",
    refresh_token: refreshToken,
  });

  const res = await fetch("https://accounts.spotify.com/api/token", {
    method: "POST",
    headers: {
      "Content-Type": "application/x-www-form-urlencoded",
      Authorization: `Basic ${Buffer.from(`${clientId}:${clientSecret}`).toString("base64")}`,
    },
    body,
  });

  if (!res.ok) {
    throw new Error("Failed to refresh Spotify token");
  }

  const data = (await res.json()) as TokenResponse;
  return {
    accessToken: data.access_token,
    refreshToken: data.refresh_token ?? refreshToken,
    expiresAt: Date.now() + data.expires_in * 1000,
  };
}

export async function getValidAccessToken(): Promise<{
  accessToken: string;
  session: SpotifySession;
}> {
  const session = await getSession();
  if (!session) {
    throw new Error("Not authenticated");
  }

  if (Date.now() < session.expiresAt - 60_000) {
    return { accessToken: session.accessToken, session };
  }

  const refreshed = await refreshAccessToken(session.refreshToken);
  await setSession({
    accessToken: refreshed.accessToken,
    refreshToken: refreshed.refreshToken,
    expiresAt: refreshed.expiresAt,
    user: session.user,
  });

  return {
    accessToken: refreshed.accessToken,
    session: {
      ...session,
      accessToken: refreshed.accessToken,
      refreshToken: refreshed.refreshToken,
      expiresAt: refreshed.expiresAt,
    },
  };
}

export async function exchangeCodeForTokens(
  code: string,
  codeVerifier: string,
): Promise<Omit<SpotifySession, "playlistId" | "playlistCity">> {
  const { clientId, redirectUri } = getSpotifyConfig();
  const body = new URLSearchParams({
    grant_type: "authorization_code",
    code,
    redirect_uri: redirectUri,
    client_id: clientId,
    code_verifier: codeVerifier,
  });

  const res = await fetch("https://accounts.spotify.com/api/token", {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body,
  });

  if (!res.ok) {
    const err = await res.text();
    throw new Error(`Token exchange failed: ${err}`);
  }

  const data = (await res.json()) as TokenResponse;
  const user = await fetchSpotifyProfile(data.access_token);

  return {
    accessToken: data.access_token,
    refreshToken: data.refresh_token!,
    expiresAt: Date.now() + data.expires_in * 1000,
    user,
  };
}

async function fetchSpotifyProfile(accessToken: string): Promise<SpotifyUser> {
  const res = await fetch("https://api.spotify.com/v1/me", {
    headers: { Authorization: `Bearer ${accessToken}` },
  });
  if (!res.ok) {
    throw new Error("Failed to fetch Spotify profile");
  }
  const data = (await res.json()) as {
    id: string;
    display_name: string | null;
    email?: string;
    images?: { url: string }[];
  };
  return {
    id: data.id,
    displayName: data.display_name ?? data.id,
    email: data.email,
    imageUrl: data.images?.[0]?.url,
  };
}

export async function spotifyFetch<T>(
  path: string,
  init?: RequestInit,
): Promise<T> {
  const { accessToken } = await getValidAccessToken();
  const res = await fetch(`https://api.spotify.com/v1${path}`, {
    ...init,
    headers: {
      Authorization: `Bearer ${accessToken}`,
      "Content-Type": "application/json",
      ...init?.headers,
    },
  });

  if (!res.ok) {
    const err = await res.text();
    let hint = "";
    if (res.status === 403) {
      hint =
        " Re-connect Spotify after this update. Dev-mode apps need Premium owner + allowlisted user.";
    }
    throw new Error(`Spotify API error (${res.status}): ${err}${hint}`);
  }

  if (res.status === 204) {
    return undefined as T;
  }

  return res.json() as Promise<T>;
}
