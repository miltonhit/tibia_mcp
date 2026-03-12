-- Materialized views for cross-entity relationships

-- creature_drops: which creatures drop which items, with rarity tier
CREATE MATERIALIZED VIEW IF NOT EXISTS creature_drops AS
SELECT
    c.page_id AS creature_id,
    c.name AS creature_name,
    c.hp AS creature_hp,
    c.exp AS creature_exp,
    i.page_id AS item_id,
    i.name AS item_name,
    i.npc_value,
    CASE
        WHEN c.loot_common ILIKE '%' || i.name || '%' THEN 'common'
        WHEN c.loot_uncommon ILIKE '%' || i.name || '%' THEN 'uncommon'
        WHEN c.loot_semi_rare ILIKE '%' || i.name || '%' THEN 'semi_rare'
        WHEN c.loot_rare ILIKE '%' || i.name || '%' THEN 'rare'
        WHEN c.loot_very_rare ILIKE '%' || i.name || '%' THEN 'very_rare'
    END AS rarity
FROM creatures c
CROSS JOIN items i
WHERE i.name IS NOT NULL
  AND length(i.name) > 2
  AND (
    c.loot_common ILIKE '%' || i.name || '%'
    OR c.loot_uncommon ILIKE '%' || i.name || '%'
    OR c.loot_semi_rare ILIKE '%' || i.name || '%'
    OR c.loot_rare ILIKE '%' || i.name || '%'
    OR c.loot_very_rare ILIKE '%' || i.name || '%'
  );

CREATE INDEX IF NOT EXISTS idx_creature_drops_creature ON creature_drops(creature_name);
CREATE INDEX IF NOT EXISTS idx_creature_drops_item ON creature_drops(item_name);
CREATE INDEX IF NOT EXISTS idx_creature_drops_rarity ON creature_drops(rarity);

-- npc_trades: which NPCs buy/sell which items
CREATE MATERIALIZED VIEW IF NOT EXISTS npc_trades AS
SELECT
    n.page_id AS npc_id,
    n.name AS npc_name,
    n.city,
    i.page_id AS item_id,
    i.name AS item_name,
    i.npc_value,
    CASE WHEN n.sells ILIKE '%' || i.name || '%' THEN true ELSE false END AS npc_sells,
    CASE WHEN n.buys ILIKE '%' || i.name || '%' THEN true ELSE false END AS npc_buys
FROM npcs n
CROSS JOIN items i
WHERE i.name IS NOT NULL
  AND length(i.name) > 2
  AND (
    n.sells ILIKE '%' || i.name || '%'
    OR n.buys ILIKE '%' || i.name || '%'
  );

CREATE INDEX IF NOT EXISTS idx_npc_trades_npc ON npc_trades(npc_name);
CREATE INDEX IF NOT EXISTS idx_npc_trades_item ON npc_trades(item_name);
CREATE INDEX IF NOT EXISTS idx_npc_trades_city ON npc_trades(city);

-- hunt_creatures: which creatures appear in which hunting places
CREATE MATERIALIZED VIEW IF NOT EXISTS hunt_creatures AS
SELECT
    h.page_id AS hunt_id,
    h.name AS hunt_name,
    h.city,
    h.level AS hunt_level,
    h.vocation,
    h.exp_rating,
    h.loot_rating,
    c.page_id AS creature_id,
    c.name AS creature_name,
    c.hp AS creature_hp,
    c.exp AS creature_exp
FROM hunts h
CROSS JOIN creatures c
WHERE c.name IS NOT NULL
  AND length(c.name) > 2
  AND (
    h.info ILIKE '%' || c.name || '%'
    OR h.rare_items ILIKE '%' || c.name || '%'
    OR h.notes ILIKE '%' || c.name || '%'
  );

CREATE INDEX IF NOT EXISTS idx_hunt_creatures_hunt ON hunt_creatures(hunt_name);
CREATE INDEX IF NOT EXISTS idx_hunt_creatures_creature ON hunt_creatures(creature_name);
CREATE INDEX IF NOT EXISTS idx_hunt_creatures_level ON hunt_creatures(hunt_level);

-- quest_bosses: link quests to their boss creatures
CREATE MATERIALIZED VIEW IF NOT EXISTS quest_bosses AS
SELECT
    q.page_id AS quest_id,
    q.name AS quest_name,
    q.level AS quest_level,
    q.reward,
    c.page_id AS creature_id,
    c.name AS creature_name,
    c.hp AS boss_hp,
    c.exp AS boss_exp
FROM quests q
CROSS JOIN creatures c
WHERE c.name IS NOT NULL
  AND length(c.name) > 2
  AND q.bosses ILIKE '%' || c.name || '%';

CREATE INDEX IF NOT EXISTS idx_quest_bosses_quest ON quest_bosses(quest_name);
CREATE INDEX IF NOT EXISTS idx_quest_bosses_creature ON quest_bosses(creature_name);
