import { NextRequest, NextResponse } from "next/server";
import {
  DEFAULT_TASTE,
  type TastePreferences,
} from "@/lib/taste/types";
import {
  getSession,
  getTastePreferences,
  setTastePreferences,
} from "@/lib/spotify/session";

export async function GET() {
  const session = await getSession();
  if (!session) {
    return NextResponse.json({ error: "Not authenticated" }, { status: 401 });
  }

  const taste = (await getTastePreferences()) ?? DEFAULT_TASTE;
  return NextResponse.json({ taste, configured: (await getTastePreferences()) != null });
}

export async function POST(request: NextRequest) {
  const session = await getSession();
  if (!session) {
    return NextResponse.json({ error: "Not authenticated" }, { status: 401 });
  }

  let body: Partial<TastePreferences>;
  try {
    body = await request.json();
  } catch {
    return NextResponse.json({ error: "Invalid JSON" }, { status: 400 });
  }

  if (!body.languageFilters?.length) {
    return NextResponse.json(
      { error: "Select at least one language" },
      { status: 400 },
    );
  }

  const taste: TastePreferences = {
    languageFilters: body.languageFilters,
    genreFilters: body.genreFilters ?? [],
    discoveryLevel: body.discoveryLevel ?? DEFAULT_TASTE.discoveryLevel,
    excludeMainstream: body.excludeMainstream ?? false,
    minMatchScore: body.minMatchScore ?? DEFAULT_TASTE.minMatchScore,
    snapshot: body.snapshot,
  };

  await setTastePreferences(taste);
  return NextResponse.json({ taste });
}
