import { NextResponse } from "next/server";
import { analyzeSpotifyTaste } from "@/lib/spotify/taste-analyze";
import { getSession } from "@/lib/spotify/session";

export async function GET() {
  const session = await getSession();
  if (!session) {
    return NextResponse.json({ error: "Not authenticated" }, { status: 401 });
  }

  try {
    const snapshot = await analyzeSpotifyTaste();
    return NextResponse.json(snapshot);
  } catch (err) {
    const message = err instanceof Error ? err.message : "Analysis failed";
    return NextResponse.json({ error: message }, { status: 500 });
  }
}
