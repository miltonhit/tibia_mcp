CREATE TABLE IF NOT EXISTS npcs (
    page_id       INTEGER PRIMARY KEY REFERENCES raw_pages(page_id),
    name          TEXT NOT NULL,
    job           TEXT,
    job2          TEXT,
    npc_class     TEXT,
    npc_sprite    TEXT,
    city          TEXT,
    subarea       TEXT,
    location      TEXT,
    implemented   TEXT,
    buysell       BOOLEAN,
    buys          TEXT,
    sells         TEXT,
    notes         TEXT
);

CREATE INDEX IF NOT EXISTS idx_npcs_name ON npcs (name);
CREATE INDEX IF NOT EXISTS idx_npcs_city ON npcs (city);
