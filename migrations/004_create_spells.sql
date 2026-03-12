CREATE TABLE IF NOT EXISTS spells (
    page_id          INTEGER PRIMARY KEY REFERENCES raw_pages(page_id),
    name             TEXT NOT NULL,
    subclass         TEXT,
    cooldown_group   INTEGER,
    cooldown_own     INTEGER,
    words            TEXT,
    premium          BOOLEAN,
    mana             INTEGER,
    mag_level        INTEGER,
    exp_level        INTEGER,
    vocations        TEXT,
    learn_druid      TEXT,
    learn_paladin    TEXT,
    learn_sorcerer   TEXT,
    learn_knight     TEXT,
    spell_cost       TEXT,
    base_power       INTEGER,
    scale_with       TEXT,
    spell_range      TEXT,
    magic_type       TEXT,
    aim_at_target    TEXT,
    effect           TEXT,
    implemented      TEXT,
    notes            TEXT
);

CREATE INDEX IF NOT EXISTS idx_spells_name ON spells (name);
CREATE INDEX IF NOT EXISTS idx_spells_type ON spells (magic_type);
