import { NextRequest, NextResponse } from "next/server";
import { getSpotifyConfig } from "@/lib/spotify/config";
import { exchangeCodeForTokens } from "@/lib/spotify/client";
import {
  consumePkceVerifier,
  setSession,
} from "@/lib/spotify/session";

export async function GET(request: NextRequest) {
  const { appUrl } = getSpotifyConfig();
  const code = request.nextUrl.searchParams.get("code");
  const error = request.nextUrl.searchParams.get("error");

  if (error) {
    return NextResponse.redirect(
      `${appUrl}/?error=${encodeURIComponent(error)}`,
    );
  }

  if (!code) {
    return NextResponse.redirect(`${appUrl}/?error=missing_code`);
  }

  const verifier = await consumePkceVerifier();
  if (!verifier) {
    return NextResponse.redirect(`${appUrl}/?error=missing_verifier`);
  }

  try {
    const session = await exchangeCodeForTokens(code, verifier);
    await setSession(session);
    return NextResponse.redirect(`${appUrl}/?connected=1`);
  } catch (err) {
    const message = err instanceof Error ? err.message : "callback_failed";
    return NextResponse.redirect(
      `${appUrl}/?error=${encodeURIComponent(message)}`,
    );
  }
}
