CREATE TABLE IF NOT EXISTS familiars (
    page_id         INTEGER PRIMARY KEY REFERENCES raw_pages(page_id),
    name            TEXT NOT NULL,
    hp              INTEGER,
    summon_cost     INTEGER,
    vocation        TEXT,
    illusionable    BOOLEAN,
    pushable        BOOLEAN,
    push_objects    BOOLEAN,
    behavior        TEXT,
    obtain          TEXT,
    implemented     TEXT,
    notes           TEXT,
    history         TEXT
);

CREATE INDEX IF NOT EXISTS idx_familiars_name ON familiars (name);
CREATE INDEX IF NOT EXISTS idx_familiars_vocation ON familiars (vocation);
