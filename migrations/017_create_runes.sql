CREATE TABLE IF NOT EXISTS runes (
    page_id         INTEGER PRIMARY KEY REFERENCES raw_pages(page_id),
    name            TEXT NOT NULL,
    subclass        TEXT,
    damage_type     TEXT,
    words           TEXT,
    make_mana       INTEGER,
    weight          NUMERIC(6,2),
    ml_required     INTEGER,
    level_required  INTEGER,
    soul            INTEGER,
    make_qty        INTEGER,
    make_voc        TEXT,
    premium         BOOLEAN,
    make_level      INTEGER,
    dropped_by      TEXT,
    dropped_raid_by TEXT,
    learn_from      TEXT,
    buy_from        TEXT,
    learn_cost      TEXT,
    npc_price       INTEGER,
    store_value     INTEGER,
    effect          TEXT,
    history         TEXT,
    implemented     TEXT,
    notes           TEXT
);

CREATE INDEX IF NOT EXISTS idx_runes_name ON runes (name);
CREATE INDEX IF NOT EXISTS idx_runes_damage_type ON runes (damage_type);
