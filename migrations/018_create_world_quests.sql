CREATE TABLE IF NOT EXISTS world_quests (
    page_id         INTEGER PRIMARY KEY REFERENCES raw_pages(page_id),
    name            TEXT NOT NULL,
    quest_type      TEXT,
    start_date      TEXT,
    end_date        TEXT,
    frequency       TEXT,
    reward          TEXT,
    location        TEXT,
    level           INTEGER,
    premium         BOOLEAN,
    dangers         TEXT,
    mini_quests     TEXT,
    bosses          TEXT,
    legend          TEXT,
    implemented     TEXT,
    notes           TEXT
);

CREATE INDEX IF NOT EXISTS idx_world_quests_name ON world_quests (name);
