-- Positions table: stores map coordinates extracted from {{mapa|X,Y,Z:zoom|text}} patterns
-- across all wiki content. Links back to source entity via page_id + source_table.
CREATE TABLE IF NOT EXISTS positions (
    id              SERIAL PRIMARY KEY,
    page_id         INTEGER NOT NULL REFERENCES raw_pages(page_id),
    source_table    TEXT NOT NULL,       -- e.g. 'npcs', 'buildings', 'hunts'
    entity_name     TEXT NOT NULL,       -- name of the entity for quick lookups
    x               INTEGER NOT NULL,
    y               INTEGER NOT NULL,
    z               INTEGER NOT NULL,
    context         TEXT,                -- surrounding text snippet where coord was found
    UNIQUE(page_id, x, y, z)
);

CREATE INDEX IF NOT EXISTS idx_positions_xyz ON positions (x, y, z);
CREATE INDEX IF NOT EXISTS idx_positions_page ON positions (page_id);
CREATE INDEX IF NOT EXISTS idx_positions_table ON positions (source_table);
CREATE INDEX IF NOT EXISTS idx_positions_name ON positions (entity_name);

-- Spatial-like index for proximity queries (cube-distance sorting)
-- We use a composite index on (z, x, y) so same-floor queries are fast
CREATE INDEX IF NOT EXISTS idx_positions_zxy ON positions (z, x, y);
