import { NextResponse } from "next/server";
import {
  getSession,
  getTastePreferences,
  hasTastePreferences,
} from "@/lib/spotify/session";

export async function GET() {
  const session = await getSession();
  if (!session) {
    return NextResponse.json({ authenticated: false });
  }

  const taste = await getTastePreferences();

  return NextResponse.json({
    authenticated: true,
    user: session.user,
    playlistId: session.playlistId ?? null,
    playlistCity: session.playlistCity ?? null,
    tasteConfigured: await hasTastePreferences(),
    taste: taste ?? null,
  });
}
