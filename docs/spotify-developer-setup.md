# Spotify Developer Setup (Showcase Web App)

Step-by-step guide for configuring a Spotify Developer app so the Showcase dashboard can **log in**, **read taste signals**, and **create playlists** in Development Mode.

**Official references:**

- [Redirect URIs](https://developer.spotify.com/documentation/web-api/concepts/redirect_uri)
- [February 2026 migration guide](https://developer.spotify.com/documentation/web-api/tutorials/february-2026-migration-guide)

---

## Checklist

Use this before running `npm run dev`:

- [ ] Spotify Developer app created
- [ ] **Redirect URI** registered (`127.0.0.1`, not `localhost`)
- [ ] **Your Spotify account added** under User Management (Development Mode)
- [ ] **App owner has Spotify Premium** (required for dev-mode write access since Feb 2026)
- [ ] `web/.env.local` filled with Client ID and Secret
- [ ] App opened at **http://127.0.0.1:3000** (same host as redirect URI)
- [ ] Connected via **Disconnect → Connect** after any scope or redirect change

---

## 1. Create a Developer App

1. Go to [Spotify Developer Dashboard](https://developer.spotify.com/dashboard)
2. Click **Create app**
3. Name it (e.g. `Showcase`) and accept the terms
4. Copy **Client ID** and **Client Secret** for `web/.env.local`

---

## 2. Redirect URI (Basic Information → Settings)

Spotify **rejects `localhost`** as a redirect host. Use an explicit loopback IP:

```
http://127.0.0.1:3000/api/auth/callback
```

| Do | Don't |
|----|-------|
| `http://127.0.0.1:3000/api/auth/callback` | `http://localhost:3000/api/auth/callback` |
| Exact path `/api/auth/callback` | Trailing slash variants |
| Same host you use in the browser | Mixing `localhost` and `127.0.0.1` |

Click **Add**, then **Save** at the bottom of Settings.

Always open the app at **http://127.0.0.1:3000** — not `http://localhost:3000`.

Docs: [Redirect URI requirements](https://developer.spotify.com/documentation/web-api/concepts/redirect_uri)

---

## 3. User Management (required in Development Mode)

Development Mode apps only work for **allowlisted users**. This is easy to miss.

1. In the Developer Dashboard, open your app
2. Go to the **User Management** tab (next to Basic Information)
3. Enter your **full name** and the **email on your Spotify account**
4. Click **Add user**

You can add up to **5 users** per app. The account you use to click “Connect with Spotify” in Showcase **must** appear on this list.

If your account is not allowlisted:

- Login may appear to work partially
- **Write** operations (create playlist, add tracks) return **403 Forbidden**

---

## 4. Premium requirement (app owner)

Since the [February 2026 Web API changes](https://developer.spotify.com/documentation/web-api/tutorials/february-2026-migration-guide), Development Mode apps require the **app owner** (the developer account that created the app) to have an **active Spotify Premium** subscription.

If the owner's Premium lapses, API write calls stop working until Premium is restored.

---

## 5. Environment variables

From `web/`:

```bash
cp .env.example .env.local
```

Set:

```env
SPOTIFY_CLIENT_ID=your_client_id
SPOTIFY_CLIENT_SECRET=your_client_secret
SPOTIFY_REDIRECT_URI=http://127.0.0.1:3000/api/auth/callback
NEXT_PUBLIC_APP_URL=http://127.0.0.1:3000
```

The Python CLI uses `SPOTIPY_*` names in the repo root `.env`; the web app accepts those as fallbacks, but the **redirect URI for the web app must be the 127.0.0.1 URL above**, not the CLI's `http://127.0.0.1:8888/callback`.

---

## 6. OAuth scopes

Showcase requests:

| Scope | Purpose |
|-------|---------|
| `playlist-modify-private` | Create and update your playlist |
| `playlist-modify-public` | Required by some dev-mode write paths |
| `user-read-private` | Identify your account |
| `user-read-email` | Profile display |
| `user-library-read` | Liked songs for taste analysis |
| `user-top-read` | Top artists for taste analysis |

After changing scopes or fixing dashboard settings:

1. Click **Disconnect** in the Showcase header
2. Click **Connect with Spotify** again and approve all permissions

Old sessions do not pick up new scopes automatically.

---

## 7. Run the web app

```bash
cd web
npm install
npm run dev
```

Open **http://127.0.0.1:3000** (not localhost).

---

## Troubleshooting

### `redirect_uri: Not matching configuration`

- URI in dashboard must **exactly** match `SPOTIFY_REDIRECT_URI` in `.env.local`
- Use `127.0.0.1`, not `localhost`
- Open the app at the same host you registered

### `This redirect URI is not secure`

- Spotify blocked `localhost` — switch to `http://127.0.0.1:PORT/...`

### `403 Forbidden` when creating a playlist

Check in order:

1. **User Management** — your Spotify email is on the allowlist
2. **Premium** — app owner has active Spotify Premium
3. **Re-connect** — disconnect and connect again after scope updates
4. **API migration** — Showcase uses `POST /me/playlists` and `/playlists/{id}/items` (Feb 2026 endpoints). Pull latest `web/` code if you see errors mentioning `/tracks`

### Taste analysis fails but login works

- Disconnect and reconnect to grant `user-library-read` and `user-top-read`
- You can still use manual language/genre filters on the taste screen

### Works in Postman but not the app

- Postman may use a different token or app. Confirm the same Client ID and that your user is allowlisted for that app.

---

## Production (later)

When deploying (e.g. Vercel):

1. Add an **HTTPS** redirect URI: `https://your-domain.com/api/auth/callback`
2. Update env vars on the host
3. Extended Quota Mode (if applicable) has different limits — see Spotify's dashboard docs

Local loopback HTTP URIs are for development only.
