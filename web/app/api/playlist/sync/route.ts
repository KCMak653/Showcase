import { NextRequest, NextResponse } from "next/server";
import { getSession, setPlaylistMeta, getTastePreferences } from "@/lib/spotify/session";
import { syncShowcasePlaylist } from "@/lib/spotify/playlist";
import { scoreAndRankShows, type ScorableShow } from "@/lib/taste/scoring";

export async function POST(request: NextRequest) {
  const session = await getSession();
  if (!session) {
    return NextResponse.json({ error: "Not authenticated" }, { status: 401 });
  }

  const taste = await getTastePreferences();
  if (!taste) {
    return NextResponse.json(
      { error: "Complete taste setup before creating a playlist" },
      { status: 400 },
    );
  }

  let body: {
    cityName?: string;
    citySlug?: string;
    includeOpeners?: boolean;
    tracksPerArtist?: number;
    shows?: ScorableShow[];
  };

  try {
    body = await request.json();
  } catch {
    return NextResponse.json({ error: "Invalid JSON body" }, { status: 400 });
  }

  const { cityName, citySlug, includeOpeners, tracksPerArtist, shows } = body;

  if (!cityName || !citySlug || !shows?.length) {
    return NextResponse.json(
      { error: "cityName, citySlug, and shows are required" },
      { status: 400 },
    );
  }

  const { ranked } = scoreAndRankShows(
    shows,
    taste,
    includeOpeners ?? false,
  );

  if (ranked.length === 0) {
    return NextResponse.json(
      {
        error:
          "No upcoming shows match your taste in this city. Try widening languages or raising discovery.",
      },
      { status: 400 },
    );
  }

  const tracks = Math.min(5, Math.max(1, tracksPerArtist ?? 2));
  const reusePlaylist =
    session.playlistId && session.playlistCity === citySlug
      ? session.playlistId
      : undefined;

  try {
    const result = await syncShowcasePlaylist({
      cityName,
      citySlug,
      shows: ranked.map((s) => ({
        bandName: s.bandName,
        showOrder: s.showOrder,
      })),
      includeOpeners: true,
      tracksPerArtist: tracks,
      existingPlaylistId: reusePlaylist,
      userId: session.user.id,
    });

    await setPlaylistMeta(result.playlistId, citySlug);

    return NextResponse.json({
      ...result,
      matchedShows: ranked.length,
      syncedAt: new Date().toISOString(),
    });
  } catch (err) {
    const message = err instanceof Error ? err.message : "Sync failed";
    return NextResponse.json({ error: message }, { status: 500 });
  }
}
