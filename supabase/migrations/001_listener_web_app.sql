-- Showcase listener web app schema
-- Replaces ad-hoc toronto_shows table with city-scoped catalog + user subscriptions.
-- Apply via Supabase SQL editor or supabase db push.

-- ---------------------------------------------------------------------------
-- Cities (supported markets)
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS cities (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    slug            TEXT NOT NULL UNIQUE,
    name            TEXT NOT NULL,
    country_code    TEXT NOT NULL DEFAULT 'CA',
    lat             DOUBLE PRECISION,
    lng             DOUBLE PRECISION,
    timezone        TEXT NOT NULL DEFAULT 'America/Toronto',
    is_supported    BOOLEAN NOT NULL DEFAULT FALSE,
    ingest_source   TEXT NOT NULL DEFAULT 'venue_scraper'
        CHECK (ingest_source IN ('venue_scraper', 'ticketmaster', 'manual')),
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

COMMENT ON TABLE cities IS 'Supported (or upcoming) cities for show catalog and user subscriptions.';
COMMENT ON COLUMN cities.is_supported IS 'When false, web UI shows coming-soon instead of preview/sync.';
COMMENT ON COLUMN cities.ingest_source IS 'How shows are ingested for this city.';

-- Seed Toronto as launch city
INSERT INTO cities (slug, name, country_code, lat, lng, timezone, is_supported, ingest_source)
VALUES ('toronto', 'Toronto', 'CA', 43.6532, -79.3832, 'America/Toronto', TRUE, 'venue_scraper')
ON CONFLICT (slug) DO NOTHING;

-- ---------------------------------------------------------------------------
-- Shows (shared catalog)
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS shows (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    city_id             UUID NOT NULL REFERENCES cities(id) ON DELETE CASCADE,
    band_name           TEXT NOT NULL,
    artist_uri          TEXT,
    venue               TEXT NOT NULL,
    show_start_time     TIMESTAMPTZ NOT NULL,
    show_order          TEXT NOT NULL DEFAULT 'UNKNOWN'
        CHECK (show_order IN ('HEADLINER', 'OPENER', 'CLOSER', 'UNKNOWN')),
    source_event_id     TEXT,
    original_band_name  TEXT,
    similarity_score    DOUBLE PRECISION,
    ingested_at         TIMESTAMPTZ NOT NULL DEFAULT now(),
    created_at          TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (city_id, show_start_time, artist_uri)
);

CREATE INDEX IF NOT EXISTS idx_shows_city_start ON shows (city_id, show_start_time);
CREATE INDEX IF NOT EXISTS idx_shows_upcoming ON shows (show_start_time)
    WHERE show_start_time >= now();

COMMENT ON TABLE shows IS 'One row per artist performance; populated by ingest worker, read by web preview and sync job.';
COMMENT ON COLUMN shows.artist_uri IS 'Spotify artist URI; nullable when match failed during ingest.';

-- ---------------------------------------------------------------------------
-- User subscriptions (per-user living playlist)
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS user_subscriptions (
    id                      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    spotify_user_id         TEXT NOT NULL,
    city_id                 UUID NOT NULL REFERENCES cities(id) ON DELETE RESTRICT,
    playlist_id             TEXT,
    refresh_token_encrypted TEXT NOT NULL,
    tracks_per_artist       INT NOT NULL DEFAULT 2
        CHECK (tracks_per_artist BETWEEN 1 AND 5),
    include_openers         BOOLEAN NOT NULL DEFAULT FALSE,
    lookahead_days          INT NOT NULL DEFAULT 30
        CHECK (lookahead_days BETWEEN 7 AND 90),
    sync_cadence_hours      INT NOT NULL DEFAULT 24
        CHECK (sync_cadence_hours BETWEEN 6 AND 168),
    paused                  BOOLEAN NOT NULL DEFAULT FALSE,
    last_synced_at          TIMESTAMPTZ,
    last_sync_status        TEXT
        CHECK (last_sync_status IS NULL OR last_sync_status IN ('ok', 'error', 'no_shows')),
    last_sync_error         TEXT,
    created_at              TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at              TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (spotify_user_id, city_id)
);

CREATE INDEX IF NOT EXISTS idx_subscriptions_active ON user_subscriptions (paused, city_id)
    WHERE paused = FALSE;

COMMENT ON TABLE user_subscriptions IS 'Links Spotify user to a city playlist; sync job iterates non-paused rows.';
COMMENT ON COLUMN user_subscriptions.refresh_token_encrypted IS 'Encrypt at application layer before insert.';
COMMENT ON COLUMN user_subscriptions.playlist_id IS 'Spotify playlist id; set on first successful sync.';

-- ---------------------------------------------------------------------------
-- City waitlist (unsupported locations)
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS city_waitlist (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email           TEXT,
    requested_city  TEXT NOT NULL,
    lat             DOUBLE PRECISION,
    lng             DOUBLE PRECISION,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_waitlist_created ON city_waitlist (created_at DESC);

COMMENT ON TABLE city_waitlist IS 'Interest capture when user picks an unsupported city.';

-- ---------------------------------------------------------------------------
-- Row-level security (sketch — enable when web app connects)
-- ---------------------------------------------------------------------------
-- ALTER TABLE cities ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE shows ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE user_subscriptions ENABLE ROW LEVEL SECURITY;
--
-- CREATE POLICY cities_public_read ON cities FOR SELECT USING (true);
-- CREATE POLICY shows_public_read ON shows FOR SELECT USING (true);
-- CREATE POLICY subscriptions_own ON user_subscriptions
--     FOR ALL USING (auth.jwt() ->> 'sub' = spotify_user_id);

-- ---------------------------------------------------------------------------
-- Migration note: toronto_shows
-- ---------------------------------------------------------------------------
-- Existing pipeline (load_shows.py) writes to toronto_shows. When ingest is
-- updated, map rows to shows with city_id = (SELECT id FROM cities WHERE slug = 'toronto')
-- and use upsert on (city_id, show_start_time, artist_uri) instead of replace_table.
