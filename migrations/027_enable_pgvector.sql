-- Enable pgvector extension and create entity_embeddings table for semantic search
-- This migration is optional - it will fail gracefully if pgvector is not installed

CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS entity_embeddings (
    id              SERIAL PRIMARY KEY,
    page_id         INTEGER NOT NULL REFERENCES raw_pages(page_id),
    source_table    TEXT NOT NULL,
    entity_name     TEXT NOT NULL,
    chunk_text      TEXT NOT NULL,
    chunk_index     INTEGER DEFAULT 0,
    embedding       vector(384),
    UNIQUE(page_id, chunk_index)
);

CREATE INDEX IF NOT EXISTS idx_embeddings_vector
    ON entity_embeddings USING ivfflat (embedding vector_cosine_ops)
    WITH (lists = 100);
CREATE INDEX IF NOT EXISTS idx_embeddings_table ON entity_embeddings(source_table);
CREATE INDEX IF NOT EXISTS idx_embeddings_name ON entity_embeddings(entity_name);
