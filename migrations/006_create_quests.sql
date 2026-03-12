CREATE TABLE IF NOT EXISTS quests (
    page_id      INTEGER PRIMARY KEY REFERENCES raw_pages(page_id),
    name         TEXT NOT NULL,
    reward       TEXT,
    location     TEXT,
    level        INTEGER,
    level_req    INTEGER,
    duration     TEXT,
    team         TEXT,
    difficulty   INTEGER,
    premium      BOOLEAN,
    dangers      TEXT,
    mini_quests  TEXT,
    bosses       TEXT,
    legend       TEXT,
    spoiler      TEXT,
    implemented  TEXT,
    notes        TEXT
);

CREATE INDEX IF NOT EXISTS idx_quests_name ON quests (name);
