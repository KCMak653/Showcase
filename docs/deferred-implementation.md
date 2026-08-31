# Deferred: listener web app implementation

Items intentionally **not** built on `planning/ui-and-features`. Pick up on branch `feat/listener-web-app` (or similar) after the brief and schema are reviewed.

## Web application

- [ ] Next.js (App Router) project under `web/` or repo root
- [ ] Landing, auth callback, place picker, preview grid, subscription status pages
- [ ] Dark editorial UI (sparse layout, large type, minimal chrome)
- [ ] Geolocation + city search with unsupported-city waitlist form

## Spotify web OAuth

- [ ] Authorization Code + PKCE flow
- [ ] Scopes: `playlist-modify-private`, `user-read-private`
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

- [docs/listener-web-app.md](listener-web-app.md) — product brief, screens, architecture
- [docs/playlist-sync.md](playlist-sync.md) — sync algorithm and API notes
- [supabase/migrations/001_listener_web_app.sql](../supabase/migrations/001_listener_web_app.sql) — schema
- [showcase/playlist_creator/playlist_creator.py](../showcase/playlist_creator/playlist_creator.py) — `sync_playlist()`, `collect_track_uris_from_shows()`
