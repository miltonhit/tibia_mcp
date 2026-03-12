CREATE TABLE IF NOT EXISTS mounts (
    page_id        INTEGER PRIMARY KEY REFERENCES raw_pages(page_id),
    name           TEXT NOT NULL,
    speed          INTEGER,
    premium        BOOLEAN,
    implemented    TEXT,
    arena_mount    BOOLEAN DEFAULT FALSE,
    champ_mount    BOOLEAN DEFAULT FALSE,
    color_mount    BOOLEAN DEFAULT FALSE,
    event_mount    BOOLEAN DEFAULT FALSE,
    offer_mount    BOOLEAN DEFAULT FALSE,
    quest_mount    BOOLEAN DEFAULT FALSE,
    raid_mount     BOOLEAN DEFAULT FALSE,
    rent_mount     BOOLEAN DEFAULT FALSE,
    store_mount    BOOLEAN DEFAULT FALSE,
    tame_mount     BOOLEAN DEFAULT FALSE,
    wchange_mount  BOOLEAN DEFAULT FALSE,
    attrib         TEXT,
    method         TEXT,
    notes          TEXT
);

CREATE INDEX IF NOT EXISTS idx_mounts_name ON mounts (name);
