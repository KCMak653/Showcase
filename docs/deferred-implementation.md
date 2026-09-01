# Deferred: listener web app implementation

Items intentionally **not** built on `planning/ui-and-features`. Pick up on branch `feat/listener-web-app` (or similar) after the brief and schema are reviewed.

## Taste personalization

See [`docs/taste-personalization.md`](taste-personalization.md).

### Phase 1 — Explicit filters

- [ ] **Taste step UI** — insert between auth and place in [`web/components/ShowcaseApp.tsx`](../web/components/ShowcaseApp.tsx)
- [ ] Language toggles: English, Cantonese, Mandarin, Japanese, Korean, Other
- [ ] Optional genre chips (manual selection)
- [ ] Persist preferences in cookies / `user_subscriptions` once Supabase is live
- [ ] Apply [`supabase/migrations/002_taste_personalization.sql`](../supabase/migrations/002_taste_personalization.sql)
- [ ] Ingest: enrich `shows` with `artist_genres`, `language_tags`, `artist_popularity` from Spotify

### Phase 2 — Spotify library signals

- [ ] Add scopes: `user-library-read`, `user-top-read`
- [ ] `/api/taste/analyze` — build `taste_snapshot` from liked songs + top artists
- [ ] Pre-fill language and genre chips from snapshot; show summary line

### Phase 3 — Scoring and ranked preview

- [ ] Relevance score per show (genre overlap, language match, similarity, discovery slider)
- [ ] Rank preview cards; hide low scores with “Show all” expander
- [ ] Filter playlist sync to taste-matched shows only
- [ ] “Why this show” badge on cards

## Web application

- [x] Next.js (App Router) project under `web/`
- [x] Landing, auth callback, place picker, preview grid, living status
- [ ] Taste setup step (language filters, Spotify snapshot)
- [ ] Dark editorial UI (sparse layout, large type, minimal chrome)
- [ ] Geolocation + city search with unsupported-city waitlist form

## Spotify web OAuth

- [x] Authorization Code + PKCE flow
- [x] Scopes: `playlist-modify-private`, `user-read-private`
- [ ] Additional scopes for taste: `user-library-read`, `user-top-read`
- [ ] Store encrypted refresh token in `user_subscriptions.refresh_token_encrypted`
- [ ] Re-auth path when sync hits 401

## Supabase integration

- [ ] Apply [`supabase/migrations/001_listener_web_app.sql`](../supabase/migrations/001_listener_web_app.sql)
- [ ] RLS: public read on `cities` and `shows`; user-scoped CRUD on `user_subscriptions`
- [ ] Server-side Supabase client for preview API routes

## Scheduled jobs

- [ ] **Ingest cron** — daily Toronto venue scrape → upsert `shows` (migrate off `load_shows.py` replace_table)
- [ ] **Sync cron** — iterate non-paused `user_subscriptions`; call `PlaylistCreator.sync_playlist()` with per-user Spotify token

## Location expansion

- [ ] Reverse geocode / nearest-city lookup against `cities.lat`, `cities.lng`
- [ ] Ticketmaster Discovery (or similar) ingest adapter for non-Toronto cities

## Ready on planning branch

- [docs/taste-personalization.md](taste-personalization.md) — taste step, language filters, library analysis, scoring
- [docs/playlist-sync.md](playlist-sync.md) — sync algorithm and API notes
- [supabase/migrations/001_listener_web_app.sql](../supabase/migrations/001_listener_web_app.sql) — schema
- [showcase/playlist_creator/playlist_creator.py](../showcase/playlist_creator/playlist_creator.py) — `sync_playlist()`, `collect_track_uris_from_shows()`
