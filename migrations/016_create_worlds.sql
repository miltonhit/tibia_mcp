CREATE TABLE IF NOT EXISTS worlds (
    page_id         INTEGER PRIMARY KEY REFERENCES raw_pages(page_id),
    name            TEXT NOT NULL,
    world_type      TEXT,
    online_since    TEXT,
    free_since      TEXT,
    offline         TEXT,
    location        TEXT,
    transfer        BOOLEAN,
    battleye        TEXT,
    implemented     TEXT,
    notes           TEXT
);

CREATE INDEX IF NOT EXISTS idx_worlds_name ON worlds (name);
CREATE INDEX IF NOT EXISTS idx_worlds_type ON worlds (world_type);
CREATE INDEX IF NOT EXISTS idx_worlds_location ON worlds (location);
