# Showcase Web Dashboard

Next.js dashboard with **real Spotify OAuth** and playlist creation.

**Full Spotify setup guide:** [`docs/spotify-developer-setup.md`](../docs/spotify-developer-setup.md) — redirect URI, **User Management allowlist**, Premium requirement, troubleshooting.

## Setup (quick)

### 1. Spotify Developer App

1. Go to [Spotify Developer Dashboard](https://developer.spotify.com/dashboard)
2. Create an app
3. **Settings → Redirect URIs** — add (Spotify rejects `localhost`):
   ```
   http://127.0.0.1:3000/api/auth/callback
   ```
4. **User Management tab** — add **your** Spotify name + email (required in Development Mode; max 5 users). Without this, playlist creation returns **403 Forbidden**.
5. Confirm the **app owner** has **Spotify Premium** ([Feb 2026 dev-mode requirement](https://developer.spotify.com/documentation/web-api/tutorials/february-2026-migration-guide))
6. Copy Client ID and Client Secret

See the [full setup guide](../docs/spotify-developer-setup.md) for screenshots-level detail and troubleshooting.

### 2. Environment

```bash
cp .env.example .env.local
# Fill in SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET
```

You can reuse the same credentials as the Python CLI (`SPOTIPY_*` vars are also supported), but the **web redirect URI** must be `http://127.0.0.1:3000/api/auth/callback`, not the CLI's port 8888 callback.

### 3. Run

```bash
npm install
npm run dev
```

Open [http://127.0.0.1:3000](http://127.0.0.1:3000) — use this URL, not `localhost`.

After changing dashboard settings or scopes: **Disconnect → Connect with Spotify** in the app.

## Flow

1. **Connect with Spotify** — OAuth PKCE login (includes library read for taste)
2. **Set your taste** — analyzes liked songs & top artists; language + genre filters
3. **Pick a city** — Toronto live; Hong Kong and others show coming soon
4. **Preview shows** — ranked by taste with match badges
5. **Start my Showcase** — only matched artists go into the playlist
6. **Living view** — open in Spotify, sync again to refresh

## API routes

| Route | Method | Purpose |
|-------|--------|---------|
| `/api/auth/login` | GET | Redirect to Spotify authorize |
| `/api/auth/callback` | GET | OAuth callback, store session cookies |
| `/api/auth/me` | GET | Current user + playlist metadata |
| `/api/auth/logout` | POST | Clear session |
| `/api/taste` | GET, POST | Read / save taste preferences |
| `/api/taste/analyze` | GET | Build taste snapshot from Spotify library |
| `/api/playlist/sync` | POST | Create or update playlist (taste-filtered) |

## What's next

- [ ] Supabase show catalog (replace mock data; persist taste in DB)
- [ ] Scheduled sync cron
- [ ] Artist images from Spotify search in preview cards
