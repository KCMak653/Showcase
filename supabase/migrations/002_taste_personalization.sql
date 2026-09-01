-- Taste personalization: extend user_subscriptions and shows for language/genre filtering
-- See docs/taste-personalization.md

-- ---------------------------------------------------------------------------
-- shows: enrich catalog rows for taste matching
-- ---------------------------------------------------------------------------
ALTER TABLE shows
    ADD COLUMN IF NOT EXISTS artist_genres TEXT[] DEFAULT '{}',
    ADD COLUMN IF NOT EXISTS language_tags TEXT[] DEFAULT '{}',
    ADD COLUMN IF NOT EXISTS artist_popularity INT
        CHECK (artist_popularity IS NULL OR artist_popularity BETWEEN 0 AND 100);

COMMENT ON COLUMN shows.artist_genres IS 'Spotify artist genres at ingest time.';
COMMENT ON COLUMN shows.language_tags IS 'Inferred language codes: en, yue, cmn, ja, ko, other.';
COMMENT ON COLUMN shows.artist_popularity IS 'Spotify artist popularity 0-100 for mainstream penalty.';

CREATE INDEX IF NOT EXISTS idx_shows_language_tags ON shows USING GIN (language_tags);
CREATE INDEX IF NOT EXISTS idx_shows_artist_genres ON shows USING GIN (artist_genres);

-- ---------------------------------------------------------------------------
-- user_subscriptions: taste preferences and cached Spotify snapshot
-- ---------------------------------------------------------------------------
ALTER TABLE user_subscriptions
    ADD COLUMN IF NOT EXISTS language_filters TEXT[] DEFAULT '{en}',
    ADD COLUMN IF NOT EXISTS genre_filters TEXT[] DEFAULT '{}',
    ADD COLUMN IF NOT EXISTS discovery_level INT NOT NULL DEFAULT 30
        CHECK (discovery_level BETWEEN 0 AND 100),
    ADD COLUMN IF NOT EXISTS exclude_mainstream BOOLEAN NOT NULL DEFAULT FALSE,
    ADD COLUMN IF NOT EXISTS min_match_score INT NOT NULL DEFAULT 30
        CHECK (min_match_score BETWEEN 0 AND 100),
    ADD COLUMN IF NOT EXISTS taste_snapshot JSONB,
    ADD COLUMN IF NOT EXISTS taste_updated_at TIMESTAMPTZ;

COMMENT ON COLUMN user_subscriptions.language_filters IS 'User-selected language codes; empty means any.';
COMMENT ON COLUMN user_subscriptions.taste_snapshot IS 'Cached top artists, genres, inferred languages from Spotify.';
COMMENT ON COLUMN user_subscriptions.discovery_level IS '0 = stick to lane; 100 = maximize local discovery.';
