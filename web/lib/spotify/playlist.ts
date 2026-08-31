import { spotifyFetch } from "./client";

export type SyncShow = {
  bandName: string;
  showOrder: "HEADLINER" | "OPENER";
};

export type SyncOptions = {
  cityName: string;
  citySlug: string;
  shows: SyncShow[];
  includeOpeners: boolean;
  tracksPerArtist: number;
  existingPlaylistId?: string;
  userId: string;
};

export type SyncResult = {
  playlistId: string;
  playlistUrl: string;
  playlistName: string;
  trackCount: number;
  artistCount: number;
  skippedArtists: string[];
};

const REPLACE_LIMIT = 100;

async function searchTrackUris(
  bandName: string,
  limit: number,
): Promise<string[]> {
  // artist top-tracks removed in Spotify Feb 2026 dev-mode migration
  const q = encodeURIComponent(`artist:${bandName}`);
  const data = await spotifyFetch<{
    tracks: { items: { uri: string }[] };
  }>(`/search?q=${q}&type=track&limit=${Math.min(limit, 10)}`);

  return data.tracks.items.slice(0, limit).map((t) => t.uri);
}

export async function syncShowcasePlaylist(
  options: SyncOptions,
): Promise<SyncResult> {
  const filtered = options.includeOpeners
    ? options.shows
    : options.shows.filter((s) => s.showOrder === "HEADLINER");

  const trackUris: string[] = [];
  const seen = new Set<string>();
  const skippedArtists: string[] = [];
  let artistCount = 0;

  for (const show of filtered) {
    const uris = await searchTrackUris(show.bandName, options.tracksPerArtist);
    if (!uris.length) {
      skippedArtists.push(show.bandName);
      continue;
    }

    artistCount += 1;
    for (const uri of uris) {
      if (!seen.has(uri)) {
        seen.add(uri);
        trackUris.push(uri);
      }
    }
  }

  const playlistName = `Showcase · ${options.cityName}`;
  let playlistId = options.existingPlaylistId;

  if (!playlistId) {
    const created = await spotifyFetch<{
      id: string;
      external_urls: { spotify: string };
    }>(`/me/playlists`, {
      method: "POST",
      body: JSON.stringify({
        name: playlistName,
        description: `Upcoming local acts in ${options.cityName}. Built by Showcase.`,
        public: false,
      }),
    });
    playlistId = created.id;
  }

  // Feb 2026 migration: /tracks → /items
  if (trackUris.length === 0) {
    await spotifyFetch(`/playlists/${playlistId}/items`, {
      method: "PUT",
      body: JSON.stringify({ uris: [] }),
    });
  } else {
    const head = trackUris.slice(0, REPLACE_LIMIT);
    const tail = trackUris.slice(REPLACE_LIMIT);

    await spotifyFetch(`/playlists/${playlistId}/items`, {
      method: "PUT",
      body: JSON.stringify({ uris: head }),
    });

    if (tail.length > 0) {
      for (let i = 0; i < tail.length; i += REPLACE_LIMIT) {
        const chunk = tail.slice(i, i + REPLACE_LIMIT);
        await spotifyFetch(`/playlists/${playlistId}/items`, {
          method: "POST",
          body: JSON.stringify({ uris: chunk }),
        });
      }
    }
  }

  const playlist = await spotifyFetch<{ external_urls: { spotify: string } }>(
    `/playlists/${playlistId}`,
  );

  return {
    playlistId,
    playlistUrl: playlist.external_urls.spotify,
    playlistName,
    trackCount: trackUris.length,
    artistCount,
    skippedArtists,
  };
}
