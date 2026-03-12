CREATE TABLE IF NOT EXISTS tasks (
    page_id         INTEGER PRIMARY KEY REFERENCES raw_pages(page_id),
    name            TEXT NOT NULL,
    premium         BOOLEAN,
    reward          TEXT,
    location        TEXT,
    time            TEXT,
    level           INTEGER,
    dangers         TEXT,
    implemented     TEXT,
    notes           TEXT
);

CREATE INDEX IF NOT EXISTS idx_tasks_name ON tasks (name);
