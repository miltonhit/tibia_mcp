CREATE TABLE IF NOT EXISTS imbuements (
    page_id            INTEGER PRIMARY KEY REFERENCES raw_pages(page_id),
    name               TEXT NOT NULL,
    modifier           TEXT,
    applicable_to      TEXT,
    duration           TEXT,
    imbuement_class    TEXT,
    effect_basic       TEXT,
    effect_intricate   TEXT,
    effect_powerful    TEXT,
    item_basic         TEXT,
    item_basic_qty     INTEGER,
    item_intricate     TEXT,
    item_intricate_qty INTEGER,
    item_powerful      TEXT,
    item_powerful_qty  INTEGER,
    implemented        TEXT,
    notes              TEXT
);

CREATE INDEX IF NOT EXISTS idx_imbuements_name ON imbuements (name);
