const SCOPES = [
  "playlist-modify-private",
  "playlist-modify-public",
  "user-read-private",
  "user-read-email",
  "user-library-read",
  "user-top-read",
].join(" ");

export function getSpotifyConfig() {
  const clientId =
    process.env.SPOTIFY_CLIENT_ID ?? process.env.SPOTIPY_CLIENT_ID;
  const clientSecret =
    process.env.SPOTIFY_CLIENT_SECRET ?? process.env.SPOTIPY_CLIENT_SECRET;
  const redirectUri =
    process.env.SPOTIFY_REDIRECT_URI ??
    process.env.SPOTIPY_REDIRECT_URI ??
    "http://127.0.0.1:3000/api/auth/callback";
  const appUrl = process.env.NEXT_PUBLIC_APP_URL ?? "http://127.0.0.1:3000";

  if (!clientId || !clientSecret) {
    throw new Error(
      "Missing Spotify credentials. Set SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET in web/.env.local",
    );
  }

  return { clientId, clientSecret, redirectUri, appUrl, scopes: SCOPES };
}
