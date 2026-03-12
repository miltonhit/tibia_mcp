CREATE TABLE IF NOT EXISTS world_changes (
    page_id         INTEGER PRIMARY KEY REFERENCES raw_pages(page_id),
    name            TEXT NOT NULL,
    change_type     TEXT,
    frequency       TEXT,
    reward          TEXT,
    location        TEXT,
    level           INTEGER,
    premium         BOOLEAN,
    dangers         TEXT,
    bosses          TEXT,
    legend          TEXT,
    implemented     TEXT,
    notes           TEXT
);

CREATE INDEX IF NOT EXISTS idx_world_changes_name ON world_changes (name);
