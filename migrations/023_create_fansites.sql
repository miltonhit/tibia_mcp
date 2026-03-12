CREATE TABLE IF NOT EXISTS fansites (
    page_id         INTEGER PRIMARY KEY REFERENCES raw_pages(page_id),
    name            TEXT NOT NULL,
    fansite_type    TEXT,
    status          TEXT,
    language        TEXT,
    content         TEXT,
    contact         TEXT,
    website         TEXT,
    implemented     TEXT,
    notes           TEXT
);

CREATE INDEX IF NOT EXISTS idx_fansites_name ON fansites (name);
