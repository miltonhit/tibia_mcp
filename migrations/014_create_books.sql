CREATE TABLE IF NOT EXISTS books (
    page_id         INTEGER PRIMARY KEY REFERENCES raw_pages(page_id),
    name            TEXT NOT NULL,
    title           TEXT,
    flavortext      TEXT,
    location        TEXT,
    author          TEXT,
    blurb           TEXT,
    book_type       TEXT,
    translated      BOOLEAN,
    prev_book       TEXT,
    next_book       TEXT,
    related_pages   TEXT,
    text            TEXT,
    implemented     TEXT,
    notes           TEXT
);

CREATE INDEX IF NOT EXISTS idx_books_name ON books (name);
CREATE INDEX IF NOT EXISTS idx_books_author ON books (author);
