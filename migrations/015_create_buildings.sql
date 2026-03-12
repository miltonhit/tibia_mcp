CREATE TABLE IF NOT EXISTS buildings (
    page_id         INTEGER PRIMARY KEY REFERENCES raw_pages(page_id),
    name            TEXT NOT NULL,
    building_type   TEXT,
    location        TEXT,
    street          TEXT,
    size            INTEGER,
    beds            INTEGER,
    rent            INTEGER,
    payrent         TEXT,
    openwindows     INTEGER,
    floors          INTEGER,
    rooms           INTEGER,
    furnishings     TEXT,
    implemented     TEXT,
    notes           TEXT
);

CREATE INDEX IF NOT EXISTS idx_buildings_name ON buildings (name);
CREATE INDEX IF NOT EXISTS idx_buildings_street ON buildings (street);
CREATE INDEX IF NOT EXISTS idx_buildings_payrent ON buildings (payrent);
