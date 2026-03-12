CREATE TABLE IF NOT EXISTS outfits (
    page_id       INTEGER PRIMARY KEY REFERENCES raw_pages(page_id),
    name          TEXT NOT NULL,
    outfit_type   TEXT,
    premium       BOOLEAN,
    outfit_access TEXT,
    addon1_access TEXT,
    addon2_access TEXT,
    value         TEXT,
    achievement   TEXT,
    implemented   TEXT,
    notes         TEXT
);

CREATE INDEX IF NOT EXISTS idx_outfits_name ON outfits (name);
