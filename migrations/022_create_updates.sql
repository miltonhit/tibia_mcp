CREATE TABLE IF NOT EXISTS updates (
    page_id             INTEGER PRIMARY KEY REFERENCES raw_pages(page_id),
    name                TEXT NOT NULL,
    update_version      TEXT,
    update_previous     TEXT,
    update_next         TEXT,
    update_season       BOOLEAN,
    update_new          TEXT,
    update_changed      TEXT,
    update_fixed        TEXT,
    implemented         TEXT,
    notes               TEXT
);

CREATE INDEX IF NOT EXISTS idx_updates_name ON updates (name);
CREATE INDEX IF NOT EXISTS idx_updates_version ON updates (update_version);
