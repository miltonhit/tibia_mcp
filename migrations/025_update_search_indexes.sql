-- Full-text search vectors for new entity tables

ALTER TABLE books ADD COLUMN IF NOT EXISTS search_vector tsvector;
ALTER TABLE buildings ADD COLUMN IF NOT EXISTS search_vector tsvector;
ALTER TABLE worlds ADD COLUMN IF NOT EXISTS search_vector tsvector;
ALTER TABLE runes ADD COLUMN IF NOT EXISTS search_vector tsvector;
ALTER TABLE world_quests ADD COLUMN IF NOT EXISTS search_vector tsvector;
ALTER TABLE world_changes ADD COLUMN IF NOT EXISTS search_vector tsvector;
ALTER TABLE familiars ADD COLUMN IF NOT EXISTS search_vector tsvector;
ALTER TABLE tasks ADD COLUMN IF NOT EXISTS search_vector tsvector;
ALTER TABLE updates ADD COLUMN IF NOT EXISTS search_vector tsvector;
ALTER TABLE fansites ADD COLUMN IF NOT EXISTS search_vector tsvector;

-- Populate books search vector
UPDATE books SET search_vector = to_tsvector('simple',
    coalesce(name, '') || ' ' ||
    coalesce(title, '') || ' ' ||
    coalesce(author, '') || ' ' ||
    coalesce(blurb, '') || ' ' ||
    coalesce(location, '') || ' ' ||
    coalesce(text, '') || ' ' ||
    coalesce(notes, '')
);

-- Populate buildings search vector
UPDATE buildings SET search_vector = to_tsvector('simple',
    coalesce(name, '') || ' ' ||
    coalesce(building_type, '') || ' ' ||
    coalesce(street, '') || ' ' ||
    coalesce(payrent, '') || ' ' ||
    coalesce(location, '') || ' ' ||
    coalesce(notes, '')
);

-- Populate worlds search vector
UPDATE worlds SET search_vector = to_tsvector('simple',
    coalesce(name, '') || ' ' ||
    coalesce(world_type, '') || ' ' ||
    coalesce(location, '') || ' ' ||
    coalesce(battleye, '') || ' ' ||
    coalesce(notes, '')
);

-- Populate runes search vector
UPDATE runes SET search_vector = to_tsvector('simple',
    coalesce(name, '') || ' ' ||
    coalesce(subclass, '') || ' ' ||
    coalesce(damage_type, '') || ' ' ||
    coalesce(words, '') || ' ' ||
    coalesce(effect, '') || ' ' ||
    coalesce(notes, '')
);

-- Populate world_quests search vector
UPDATE world_quests SET search_vector = to_tsvector('simple',
    coalesce(name, '') || ' ' ||
    coalesce(reward, '') || ' ' ||
    coalesce(location, '') || ' ' ||
    coalesce(dangers, '') || ' ' ||
    coalesce(bosses, '') || ' ' ||
    coalesce(legend, '') || ' ' ||
    coalesce(notes, '')
);

-- Populate world_changes search vector
UPDATE world_changes SET search_vector = to_tsvector('simple',
    coalesce(name, '') || ' ' ||
    coalesce(reward, '') || ' ' ||
    coalesce(location, '') || ' ' ||
    coalesce(dangers, '') || ' ' ||
    coalesce(bosses, '') || ' ' ||
    coalesce(legend, '') || ' ' ||
    coalesce(notes, '')
);

-- Populate familiars search vector
UPDATE familiars SET search_vector = to_tsvector('simple',
    coalesce(name, '') || ' ' ||
    coalesce(vocation, '') || ' ' ||
    coalesce(behavior, '') || ' ' ||
    coalesce(obtain, '') || ' ' ||
    coalesce(notes, '')
);

-- Populate tasks search vector
UPDATE tasks SET search_vector = to_tsvector('simple',
    coalesce(name, '') || ' ' ||
    coalesce(reward, '') || ' ' ||
    coalesce(location, '') || ' ' ||
    coalesce(dangers, '') || ' ' ||
    coalesce(notes, '')
);

-- Populate updates search vector
UPDATE updates SET search_vector = to_tsvector('simple',
    coalesce(name, '') || ' ' ||
    coalesce(update_version, '') || ' ' ||
    coalesce(update_new, '') || ' ' ||
    coalesce(update_changed, '') || ' ' ||
    coalesce(notes, '')
);

-- Populate fansites search vector
UPDATE fansites SET search_vector = to_tsvector('simple',
    coalesce(name, '') || ' ' ||
    coalesce(fansite_type, '') || ' ' ||
    coalesce(language, '') || ' ' ||
    coalesce(content, '') || ' ' ||
    coalesce(notes, '')
);

-- GIN indexes for fast full-text search
CREATE INDEX IF NOT EXISTS idx_books_fts ON books USING GIN(search_vector);
CREATE INDEX IF NOT EXISTS idx_buildings_fts ON buildings USING GIN(search_vector);
CREATE INDEX IF NOT EXISTS idx_worlds_fts ON worlds USING GIN(search_vector);
CREATE INDEX IF NOT EXISTS idx_runes_fts ON runes USING GIN(search_vector);
CREATE INDEX IF NOT EXISTS idx_world_quests_fts ON world_quests USING GIN(search_vector);
CREATE INDEX IF NOT EXISTS idx_world_changes_fts ON world_changes USING GIN(search_vector);
CREATE INDEX IF NOT EXISTS idx_familiars_fts ON familiars USING GIN(search_vector);
CREATE INDEX IF NOT EXISTS idx_tasks_fts ON tasks USING GIN(search_vector);
CREATE INDEX IF NOT EXISTS idx_updates_fts ON updates USING GIN(search_vector);
CREATE INDEX IF NOT EXISTS idx_fansites_fts ON fansites USING GIN(search_vector);
