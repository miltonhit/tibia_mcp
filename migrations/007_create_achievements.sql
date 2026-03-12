CREATE TABLE IF NOT EXISTS achievements (
    page_id       INTEGER PRIMARY KEY REFERENCES raw_pages(page_id),
    name          TEXT NOT NULL,
    identifier    INTEGER,
    status        TEXT,
    grade         INTEGER,
    points        INTEGER,
    obtainable    BOOLEAN,
    secret        BOOLEAN,
    premium       BOOLEAN,
    implemented   TEXT,
    description   TEXT,
    notes         TEXT
);

CREATE INDEX IF NOT EXISTS idx_achievements_name ON achievements (name);
