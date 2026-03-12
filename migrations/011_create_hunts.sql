CREATE TABLE IF NOT EXISTS hunts (
    page_id       INTEGER PRIMARY KEY REFERENCES raw_pages(page_id),
    name          TEXT NOT NULL,
    city          TEXT,
    location      TEXT,
    map_coords    TEXT,
    premium       BOOLEAN,
    difficulty    INTEGER,
    vocation      TEXT,
    level         INTEGER,
    loot_rating   INTEGER,
    exp_rating    INTEGER,
    rare_items    TEXT,
    implemented   TEXT,
    info          TEXT,
    notes         TEXT
);

CREATE INDEX IF NOT EXISTS idx_hunts_name ON hunts (name);
CREATE INDEX IF NOT EXISTS idx_hunts_city ON hunts (city);
