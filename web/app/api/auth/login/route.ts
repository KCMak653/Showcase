import { NextResponse } from "next/server";
import { getSpotifyConfig } from "@/lib/spotify/config";
import {
  generateCodeChallenge,
  generateCodeVerifier,
} from "@/lib/spotify/pkce";
import { setPkceVerifier } from "@/lib/spotify/session";

export async function GET() {
  try {
    const { clientId, redirectUri, scopes } = getSpotifyConfig();
    const verifier = generateCodeVerifier();
    const challenge = await generateCodeChallenge(verifier);
    await setPkceVerifier(verifier);

    const params = new URLSearchParams({
      client_id: clientId,
      response_type: "code",
      redirect_uri: redirectUri,
      scope: scopes,
      code_challenge_method: "S256",
      code_challenge: challenge,
    });

    return NextResponse.redirect(
      `https://accounts.spotify.com/authorize?${params.toString()}`,
    );
  } catch (err) {
    const message = err instanceof Error ? err.message : "Auth failed";
    return NextResponse.redirect(
      `/?error=${encodeURIComponent(message)}`,
    );
  }
}
