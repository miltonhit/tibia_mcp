-- Full-text search vectors for intelligent cross-entity search

-- Add tsvector columns
ALTER TABLE creatures ADD COLUMN IF NOT EXISTS search_vector tsvector;
ALTER TABLE items ADD COLUMN IF NOT EXISTS search_vector tsvector;
ALTER TABLE spells ADD COLUMN IF NOT EXISTS search_vector tsvector;
ALTER TABLE npcs ADD COLUMN IF NOT EXISTS search_vector tsvector;
ALTER TABLE quests ADD COLUMN IF NOT EXISTS search_vector tsvector;
ALTER TABLE achievements ADD COLUMN IF NOT EXISTS search_vector tsvector;
ALTER TABLE hunts ADD COLUMN IF NOT EXISTS search_vector tsvector;

-- Populate creatures search vector
UPDATE creatures SET search_vector = to_tsvector('simple',
    coalesce(name, '') || ' ' ||
    coalesce(creature_class, '') || ' ' ||
    coalesce(primary_type, '') || ' ' ||
    coalesce(secondary_type, '') || ' ' ||
    coalesce(immunities, '') || ' ' ||
    coalesce(loot_common, '') || ' ' ||
    coalesce(loot_uncommon, '') || ' ' ||
    coalesce(loot_semi_rare, '') || ' ' ||
    coalesce(loot_rare, '') || ' ' ||
    coalesce(loot_very_rare, '') || ' ' ||
    coalesce(behavior, '') || ' ' ||
    coalesce(location_raid, '') || ' ' ||
    coalesce(notes, '')
);

-- Populate items search vector
UPDATE items SET search_vector = to_tsvector('simple',
    coalesce(name, '') || ' ' ||
    coalesce(item_class, '') || ' ' ||
    coalesce(primary_type, '') || ' ' ||
    coalesce(secondary_type, '') || ' ' ||
    coalesce(voc_required, '') || ' ' ||
    coalesce(body_position, '') || ' ' ||
    coalesce(dropped_by, '') || ' ' ||
    coalesce(buy_from, '') || ' ' ||
    coalesce(sell_to, '') || ' ' ||
    coalesce(notes, '')
);

-- Populate spells search vector
UPDATE spells SET search_vector = to_tsvector('simple',
    coalesce(name, '') || ' ' ||
    coalesce(words, '') || ' ' ||
    coalesce(subclass, '') || ' ' ||
    coalesce(magic_type, '') || ' ' ||
    coalesce(vocations, '') || ' ' ||
    coalesce(effect, '') || ' ' ||
    coalesce(notes, '')
);

-- Populate npcs search vector
UPDATE npcs SET search_vector = to_tsvector('simple',
    coalesce(name, '') || ' ' ||
    coalesce(job, '') || ' ' ||
    coalesce(npc_class, '') || ' ' ||
    coalesce(city, '') || ' ' ||
    coalesce(location, '') || ' ' ||
    coalesce(buys, '') || ' ' ||
    coalesce(sells, '') || ' ' ||
    coalesce(notes, '')
);

-- Populate quests search vector
UPDATE quests SET search_vector = to_tsvector('simple',
    coalesce(name, '') || ' ' ||
    coalesce(reward, '') || ' ' ||
    coalesce(location, '') || ' ' ||
    coalesce(dangers, '') || ' ' ||
    coalesce(bosses, '') || ' ' ||
    coalesce(legend, '') || ' ' ||
    coalesce(notes, '')
);

-- Populate achievements search vector
UPDATE achievements SET search_vector = to_tsvector('simple',
    coalesce(name, '') || ' ' ||
    coalesce(description, '') || ' ' ||
    coalesce(notes, '')
);

-- Populate hunts search vector
UPDATE hunts SET search_vector = to_tsvector('simple',
    coalesce(name, '') || ' ' ||
    coalesce(city, '') || ' ' ||
    coalesce(location, '') || ' ' ||
    coalesce(vocation, '') || ' ' ||
    coalesce(rare_items, '') || ' ' ||
    coalesce(info, '') || ' ' ||
    coalesce(notes, '')
);

-- GIN indexes for fast full-text search
CREATE INDEX IF NOT EXISTS idx_creatures_fts ON creatures USING GIN(search_vector);
CREATE INDEX IF NOT EXISTS idx_items_fts ON items USING GIN(search_vector);
CREATE INDEX IF NOT EXISTS idx_spells_fts ON spells USING GIN(search_vector);
CREATE INDEX IF NOT EXISTS idx_npcs_fts ON npcs USING GIN(search_vector);
CREATE INDEX IF NOT EXISTS idx_quests_fts ON quests USING GIN(search_vector);
CREATE INDEX IF NOT EXISTS idx_achievements_fts ON achievements USING GIN(search_vector);
CREATE INDEX IF NOT EXISTS idx_hunts_fts ON hunts USING GIN(search_vector);
