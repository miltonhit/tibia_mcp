CREATE TABLE IF NOT EXISTS items (
    page_id           INTEGER PRIMARY KEY REFERENCES raw_pages(page_id),
    name              TEXT NOT NULL,
    voc_required      TEXT,
    item_class        TEXT,
    primary_type      TEXT,
    secondary_type    TEXT,
    stackable         BOOLEAN,
    imbuement_slots   INTEGER,
    classification    INTEGER,
    max_tier          INTEGER,
    armor             INTEGER,
    attack            INTEGER,
    attack_mod        TEXT,
    hit_percent       INTEGER,
    defense           INTEGER,
    defense_mod       INTEGER,
    hands             TEXT,
    body_position     TEXT,
    weight            NUMERIC(8,2),
    value             TEXT,
    npc_value         INTEGER,
    npc_value_currency TEXT,
    dropped_by        TEXT,
    buy_from          TEXT,
    sell_to           TEXT,
    implemented       TEXT,
    notes             TEXT
);

CREATE INDEX IF NOT EXISTS idx_items_name ON items (name);
CREATE INDEX IF NOT EXISTS idx_items_type ON items (primary_type);
CREATE INDEX IF NOT EXISTS idx_items_class ON items (item_class);
