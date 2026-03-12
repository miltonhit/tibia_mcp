-- Migration 001: Raw pages table
-- Stores all downloaded wiki pages before parsing.
-- Enables re-parsing without re-downloading.

CREATE TABLE IF NOT EXISTS schema_migrations (
    version     INTEGER PRIMARY KEY,
    filename    TEXT NOT NULL,
    applied_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS raw_pages (
    page_id       INTEGER PRIMARY KEY,
    title         TEXT NOT NULL,
    namespace     INTEGER NOT NULL DEFAULT 0,
    content       TEXT,
    is_redirect   BOOLEAN NOT NULL DEFAULT FALSE,
    downloaded_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_raw_pages_title ON raw_pages (title);
CREATE INDEX IF NOT EXISTS idx_raw_pages_redirect ON raw_pages (is_redirect);
