-- Add missing item fields for complete wiki data capture

ALTER TABLE items ADD COLUMN IF NOT EXISTS level_required INTEGER;
ALTER TABLE items ADD COLUMN IF NOT EXISTS resist TEXT;
ALTER TABLE items ADD COLUMN IF NOT EXISTS skillboost TEXT;
ALTER TABLE items ADD COLUMN IF NOT EXISTS damage TEXT;
ALTER TABLE items ADD COLUMN IF NOT EXISTS damage_type TEXT;
ALTER TABLE items ADD COLUMN IF NOT EXISTS element_attack TEXT;
ALTER TABLE items ADD COLUMN IF NOT EXISTS mana INTEGER;
ALTER TABLE items ADD COLUMN IF NOT EXISTS range INTEGER;
ALTER TABLE items ADD COLUMN IF NOT EXISTS augments TEXT;
ALTER TABLE items ADD COLUMN IF NOT EXISTS charges INTEGER;
ALTER TABLE items ADD COLUMN IF NOT EXISTS attrib TEXT;
ALTER TABLE items ADD COLUMN IF NOT EXISTS flavor_text TEXT;
ALTER TABLE items ADD COLUMN IF NOT EXISTS enchantable BOOLEAN;
ALTER TABLE items ADD COLUMN IF NOT EXISTS item_type TEXT;
ALTER TABLE items ADD COLUMN IF NOT EXISTS npc_price INTEGER;
ALTER TABLE items ADD COLUMN IF NOT EXISTS duration TEXT;

-- Index on level_required for equipment queries by level
CREATE INDEX IF NOT EXISTS idx_items_level_required ON items (level_required);

-- Backfill body_position from primary_type for existing rows
UPDATE items SET body_position = CASE primary_type
    WHEN 'Armaduras' THEN 'armor'
    WHEN 'Capacetes' THEN 'helmet'
    WHEN 'Calças' THEN 'legs'
    WHEN 'Botas' THEN 'boots'
    WHEN 'Escudos' THEN 'shield'
    WHEN 'Spellbooks' THEN 'shield'
    WHEN 'Espadas' THEN 'weapon'
    WHEN 'Machados' THEN 'weapon'
    WHEN 'Clavas' THEN 'weapon'
    WHEN 'Distância' THEN 'weapon'
    WHEN 'Armas de Arremesso' THEN 'weapon'
    WHEN 'Punhos' THEN 'weapon'
    WHEN 'Wands' THEN 'weapon'
    WHEN 'Rods' THEN 'weapon'
    WHEN 'Armas Obsoletas' THEN 'weapon'
    WHEN 'Anéis' THEN 'ring'
    WHEN 'Amuletos e Colares' THEN 'amulet'
    WHEN 'Antigos Amuletos e Colares' THEN 'amulet'
    WHEN 'Munição' THEN 'ammo'
    ELSE body_position
END
WHERE body_position IS NULL AND primary_type IS NOT NULL;
