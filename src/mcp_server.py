"""MCP Server for TibiaWiki database — optimized for AI agents.

Browse & Drill architecture: discover → filter → detail.
Compact mode by default to minimize context usage.
~17 tools instead of 35+.
"""

import json
import logging
import os

from mcp.server.fastmcp import FastMCP
import psycopg2
from psycopg2.extras import RealDictCursor

from src.config import DATABASE_URL

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

mcp = FastMCP("TibiaWiki", host=os.getenv("MCP_HOST", "127.0.0.1"), instructions="""
You have access to a comprehensive TibiaWiki database (tibiawiki.com.br).
Covers ALL Tibia MMORPG content: creatures, items, spells, NPCs, quests,
achievements, mounts, outfits, imbuements, hunts, books, buildings, worlds,
runes, world quests, world changes, familiars, tasks, updates, fansites.

## HOW TO USE (follow this workflow):

1. DISCOVER what exists:
   -> describe_tables() - see all tables, row counts, column schemas
   -> list_entities(type, limit=25) - browse names with pagination

2. SEARCH by keyword:
   -> search(query, entity_type?) - returns COMPACT results (name + key fields)
   -> Omit entity_type to search ALL tables at once.
   -> Use search_by_tags(type, tags) for tag-based filtering.

3. GET FULL DETAILS for a specific entity:
   -> get_entity(type, name) - returns ALL fields for one entity

4. USE SMART TOOLS for complex cross-entity questions:
   -> creature_full_info(name) - stats + loot + hunts + sell prices
   -> where_to_get_item(name) - drops + NPC shops + quest rewards
   -> where_to_sell_item(name) - NPCs that buy it
   -> recommend_hunt(level, vocation) - best hunts for your level
   -> profit_analysis(creature) - estimated gold/kill
   -> creature_weakness(element) - creatures weak to an element
   -> items_for_vocation(vocation) - equipment for your class
   -> compare_creatures(name1, name2) - side-by-side comparison

5. MAP & POSITIONS:
   -> get_map_url(x, y, z) - TibiaWiki map link
   -> search_by_position(x, y, z, radius) - entities near coordinates
   -> nearby_entities(name, radius) - entities near a named entity

6. SEMANTIC SEARCH (if available):
   -> semantic_search(question) - natural language search via embeddings

7. CUSTOM QUERIES:
   -> query_database(sql) - raw SQL SELECT for anything else

8. RANK & EXPLORE:
   -> rank_entities(type, sort_by) - top items by price, strongest creatures, best armor, etc.

IMPORTANT: ALWAYS start with compact search. Only get_entity for 1-2 specific
entities. Never request full details on broad queries — it wastes context.

## QUICK ANSWERS FOR COMMON QUESTIONS:
- "Most expensive items" -> rank_entities("items", "npc_value")
- "Strongest creatures" -> rank_entities("creatures", "exp") or rank_entities("creatures", "hp")
- "Best weapons" -> rank_entities("items", "attack")
- "Best armor" -> rank_entities("items", "armor", filter_column="body_position", filter_value="armor")
- "What drops item X" -> where_to_get_item(X)
- "Where to sell item X" -> where_to_sell_item(X)
- "Hunting spots for level N" -> recommend_hunt(N, vocation)

## COMMON MISTAKES TO AVOID:
- items.value is TEXT (raw wiki), NOT a price. Use items.npc_value (INTEGER) for gold prices.
- items.sell_to contains NPC names, NOT a price column.
- npc_trades view has ~43 rows (very incomplete). Use items.npc_value directly for prices.
- Creature _mod columns are percentages: 100=normal, >100=weak, 0=immune.
""")


# ─── Database helpers ──────────────────────────────────────────────

def _get_conn():
    return psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)


def _query(sql, params=None, limit=20):
    """Execute a query and return results as list of dicts."""
    conn = _get_conn()
    try:
        with conn.cursor() as cur:
            if params:
                cur.execute(sql, params)
            else:
                cur.execute(sql)
            rows = cur.fetchmany(limit)
            return [dict(r) for r in rows]
    finally:
        conn.close()


def _format(rows):
    """Format query results as readable JSON text."""
    if not rows:
        return "No results found."
    return json.dumps(rows, ensure_ascii=False, indent=2, default=str)


def _has_table(table_name):
    """Check if a table or materialized view exists."""
    try:
        rows = _query(
            "SELECT 1 FROM information_schema.tables WHERE table_name = %s "
            "UNION SELECT 1 FROM pg_matviews WHERE matviewname = %s",
            (table_name, table_name), limit=1
        )
        return len(rows) > 0
    except Exception:
        return False


def _has_column(table_name, column_name):
    """Check if a column exists in a table."""
    try:
        rows = _query(
            "SELECT 1 FROM information_schema.columns "
            "WHERE table_name = %s AND column_name = %s",
            (table_name, column_name), limit=1
        )
        return len(rows) > 0
    except Exception:
        return False


# Compact columns per table — name + 2-4 key fields for search results
COMPACT_COLUMNS = {
    "creatures": ["name", "hp", "exp", "creature_class", "primary_type", "summary"],
    "items": ["name", "item_class", "primary_type", "body_position", "armor", "attack", "defense", "level_required", "npc_value", "summary"],
    "spells": ["name", "words", "subclass", "mana", "mag_level", "vocations", "magic_type"],
    "npcs": ["name", "job", "city", "subarea"],
    "quests": ["name", "level", "reward", "location", "premium"],
    "achievements": ["name", "grade", "points", "description"],
    "mounts": ["name", "speed", "premium", "method"],
    "outfits": ["name", "premium"],
    "imbuements": ["name"],
    "hunts": ["name", "city", "level", "exp_rating", "loot_rating", "vocation"],
    "books": ["name", "title", "author", "location"],
    "buildings": ["name", "building_type", "street", "size", "beds", "rent", "payrent"],
    "worlds": ["name", "world_type", "location", "battleye"],
    "runes": ["name", "damage_type", "words", "level_required", "npc_price"],
    "world_quests": ["name", "quest_type", "frequency", "level"],
    "world_changes": ["name", "change_type", "frequency"],
    "familiars": ["name", "hp", "vocation"],
    "tasks": ["name", "reward", "location", "level"],
    "updates": ["name", "update_version"],
    "fansites": ["name", "fansite_type", "language"],
}

ALL_ENTITY_TABLES = list(COMPACT_COLUMNS.keys())

# Key columns with semantic hints — included in describe_tables() overview
# Format: (column_name, type, hint)
TABLE_COLUMN_HINTS = {
    "creatures": [
        ("name", "TEXT", "creature name"),
        ("hp", "INT", "hit points"),
        ("exp", "INT", "experience on kill"),
        ("creature_class", "TEXT", "category: Demons, Dragons, Undead, etc."),
        ("primary_type", "TEXT", "sub-category within class"),
        ("physical_mod / fire_mod / ice_mod / earth_mod / energy_mod / holy_mod / death_mod", "INT",
         "damage modifier %: 100=normal, >100=weak, 0=immune"),
    ],
    "items": [
        ("name", "TEXT", "item name"),
        ("npc_value", "INT", "gold price NPCs pay — THE price column for value queries"),
        ("value", "TEXT", "raw wiki text, NOT a clean number — do NOT use for prices"),
        ("sell_to", "TEXT", "NPC names who buy it — NOT a price column"),
        ("buy_from", "TEXT", "NPC names who sell it — NOT a price column"),
        ("item_class", "TEXT", "category: Swords, Axes, Armors, Helmets, etc."),
        ("body_position", "TEXT", "equipment slot: helmet, armor, legs, boots, shield, weapon, ring, amulet, ammo"),
        ("armor", "INT", "armor value (for armor pieces)"),
        ("attack", "INT", "attack value (for weapons)"),
        ("defense", "INT", "defense value"),
        ("classification", "INT", "tier 0-4 (higher = better)"),
        ("level_required", "INT", "minimum level to equip"),
        ("resist", "TEXT", "resistance bonuses e.g. 'Physical +12%, Death +6%'"),
        ("skillboost", "TEXT", "skill bonuses e.g. 'Shielding +4'"),
        ("damage_type", "TEXT", "damage element for wands/rods"),
        ("element_attack", "TEXT", "elemental attack on weapons e.g. '+25 Fire'"),
        ("augments", "TEXT", "augment bonuses on endgame items"),
    ],
    "spells": [
        ("name", "TEXT", "spell name"),
        ("words", "TEXT", "incantation words"),
        ("mana", "INT", "mana cost"),
        ("mag_level", "INT", "magic level required"),
        ("vocations", "TEXT", "which vocations can use it"),
    ],
    "hunts": [
        ("name", "TEXT", "hunting place name"),
        ("level", "INT", "recommended level"),
        ("exp_rating", "INT", "exp quality 1-5"),
        ("loot_rating", "INT", "loot quality 1-5"),
        ("vocation", "TEXT", "recommended vocations"),
        ("city", "TEXT", "nearest city"),
    ],
    "npcs": [
        ("name", "TEXT", "NPC name"),
        ("job", "TEXT", "NPC role/job"),
        ("city", "TEXT", "city location"),
        ("buys", "TEXT", "comma-separated item names NPC buys"),
        ("sells", "TEXT", "comma-separated item names NPC sells"),
    ],
    "creature_drops": [
        ("creature_name", "TEXT", "creature that drops the item"),
        ("item_name", "TEXT", "dropped item name"),
        ("npc_value", "INT", "gold price NPCs pay for this item"),
        ("rarity", "TEXT", "common / uncommon / semi_rare / rare / very_rare"),
    ],
    "npc_trades": [
        ("npc_name", "TEXT", "NPC name"),
        ("item_name", "TEXT", "traded item name"),
        ("npc_value", "INT", "gold price"),
        ("npc_sells", "BOOL", "true if NPC sells this item"),
        ("npc_buys", "BOOL", "true if NPC buys this item"),
        ("city", "TEXT", "NPC city"),
    ],
}

# Merge view names into entity table list for rank_entities support
VIEW_TABLES = ["creature_drops", "npc_trades", "hunt_creatures", "quest_bosses"]


def _compact_select(table):
    """Build SELECT clause using only compact columns that exist."""
    desired = COMPACT_COLUMNS.get(table, ["name"])
    # Always include name, filter to existing columns
    cols = [c for c in desired if _has_column(table, c)]
    if not cols:
        cols = ["name"]
    return ", ".join(cols)


# ─── DISCOVERY TOOLS ──────────────────────────────────────────────

@mcp.tool()
def describe_tables(table_name: str = "") -> str:
    """Show available tables, row counts, and column schemas.

    Without table_name: lists all tables with row counts and descriptions.
    With table_name: shows full column list with types for that table.

    Args:
        table_name: Optional specific table to describe (e.g. "creatures", "items")
    """
    if table_name:
        if not _has_table(table_name):
            return f"Table '{table_name}' not found."

        cols = _query(
            "SELECT column_name, data_type, is_nullable "
            "FROM information_schema.columns "
            "WHERE table_name = %s ORDER BY ordinal_position",
            (table_name,), limit=100
        )

        count = _query(f"SELECT count(*) as cnt FROM {table_name}", limit=1)
        cnt = count[0]["cnt"] if count else "?"

        return json.dumps({
            "table": table_name,
            "row_count": cnt,
            "columns": cols,
        }, indent=2, default=str)

    # List all tables with counts
    table_descriptions = {
        "creatures": "Monsters, bosses, NPCs with stats, loot, elemental mods",
        "items": "Equipment, tools, quest items with stats and prices",
        "spells": "Magic spells with incantation words, mana cost, vocations",
        "npcs": "Non-player characters with jobs, locations, buy/sell lists",
        "quests": "Quest guides with level reqs, rewards, bosses, spoilers",
        "achievements": "In-game achievements with grade, points, descriptions",
        "mounts": "Rideable mounts with speed bonus and obtain method",
        "outfits": "Character outfits/appearances",
        "imbuements": "Item imbuement enchantments",
        "hunts": "Hunting places with level range, exp/loot ratings, creatures",
        "books": "In-game books with lore text, authors, locations",
        "buildings": "Houses/guildhalls with size, rent, beds, locations",
        "worlds": "Game servers with PvP type, location, BattlEye status",
        "runes": "Magic runes with damage type, craft cost, prices",
        "world_quests": "Server-wide periodic events (e.g. Lightbearer)",
        "world_changes": "Dynamic world events that alter the game",
        "familiars": "Summonable companion creatures per vocation",
        "tasks": "Repeatable hunting tasks from NPCs",
        "updates": "Game version history and patch notes",
        "fansites": "Community fansites recognized by CipSoft",
        "positions": "Map coordinates (x, y, z) for entities",
    }

    stats = {}
    conn = _get_conn()
    try:
        with conn.cursor() as cur:
            for table in list(table_descriptions.keys()):
                try:
                    cur.execute(f"SELECT count(*) as cnt FROM {table}")
                    cnt = cur.fetchone()["cnt"]
                    entry = {
                        "rows": cnt,
                        "description": table_descriptions.get(table, ""),
                    }
                    if table in TABLE_COLUMN_HINTS:
                        entry["key_columns"] = [
                            {"column": c, "type": t, "hint": h}
                            for c, t, h in TABLE_COLUMN_HINTS[table]
                        ]
                    stats[table] = entry
                except Exception:
                    conn.rollback()
    finally:
        conn.close()

    # Also show materialized views
    views = {
        "creature_drops": "Which creatures drop which items (with rarity)",
        "npc_trades": "Which NPCs buy/sell which items",
        "hunt_creatures": "Which creatures appear in which hunting places",
        "quest_bosses": "Which bosses appear in which quests",
    }
    conn = _get_conn()
    try:
        with conn.cursor() as cur:
            for view, desc in views.items():
                try:
                    cur.execute(f"SELECT count(*) as cnt FROM {view}")
                    cnt = cur.fetchone()["cnt"]
                    view_entry = {"rows": cnt, "description": desc}
                    if view in TABLE_COLUMN_HINTS:
                        view_entry["key_columns"] = [
                            {"column": c, "type": t, "hint": h}
                            for c, t, h in TABLE_COLUMN_HINTS[view]
                        ]
                    stats[f"[view] {view}"] = view_entry
                except Exception:
                    conn.rollback()
    finally:
        conn.close()

    return json.dumps(stats, indent=2, default=str)


@mcp.tool()
def list_entities(entity_type: str, limit: int = 25, offset: int = 0,
                  sort_by: str = "name", filter: str = "") -> str:
    """List entities of a given type with pagination. Returns ONLY names and key identifiers.

    Use this to browse what exists, then get_entity() for details.

    Args:
        entity_type: Table name (creatures, items, npcs, hunts, etc.)
        limit: Results per page (max 50, default 25)
        offset: Skip first N results for pagination
        sort_by: Column to sort by (default "name")
        filter: Optional ILIKE filter on name (e.g. "dragon%", "%sword%")
    """
    if entity_type not in ALL_ENTITY_TABLES:
        return f"Invalid entity_type '{entity_type}'. Valid: {', '.join(ALL_ENTITY_TABLES)}"

    if not _has_table(entity_type):
        return f"Table '{entity_type}' not available. Run the importer first."

    limit = min(limit, 50)
    cols = _compact_select(entity_type)

    # Validate sort column
    if not _has_column(entity_type, sort_by):
        sort_by = "name"

    conditions = []
    params = []

    if filter:
        conditions.append("name ILIKE %s")
        params.append(filter)

    where = " AND ".join(conditions) if conditions else "TRUE"
    params.extend([limit, offset])

    rows = _query(
        f"SELECT {cols} FROM {entity_type} WHERE {where} "
        f"ORDER BY {sort_by} LIMIT %s OFFSET %s",
        params,
        limit=limit,
    )

    # Get total count for pagination info
    count_rows = _query(
        f"SELECT count(*) as total FROM {entity_type} WHERE {where}",
        params[:-2] if params[:-2] else None,
        limit=1,
    )
    total = count_rows[0]["total"] if count_rows else "?"

    return json.dumps({
        "entity_type": entity_type,
        "total": total,
        "offset": offset,
        "limit": limit,
        "has_more": (offset + limit) < total if isinstance(total, int) else True,
        "results": rows,
    }, ensure_ascii=False, indent=2, default=str)


# ─── UNIFIED SEARCH ────────────────────────────────────────────────

@mcp.tool()
def search(query: str, entity_type: str = "", detail: bool = False,
           limit: int = 10, offset: int = 0) -> str:
    """Search for any entity in the TibiaWiki database.

    COMPACT MODE (default): Returns name + 2-3 key fields per result.
    Use this to find entities, then use get_entity() for full details.

    DETAIL MODE (detail=True): Returns all fields. Use sparingly — only
    when you need full info and know there are few results.

    Args:
        query: Search keywords (e.g. "dragon", "fire sword", "thais")
        entity_type: Filter to specific type. Empty = search all types.
            Options: creatures, items, spells, npcs, quests, achievements,
            mounts, hunts, books, buildings, worlds, runes, world_quests,
            world_changes, familiars, tasks, updates, fansites
        detail: False=compact (default), True=full details
        limit: Max results per type (default 10, max 50)
        offset: Skip N results for pagination
    """
    limit = min(limit, 50)
    tables_to_search = [entity_type] if entity_type else ALL_ENTITY_TABLES

    results = {}

    for table in tables_to_search:
        if not _has_table(table):
            continue

        cols = "*" if detail else _compact_select(table)
        per_table_limit = limit if entity_type else min(limit, 5)

        # Try FTS first, fallback to ILIKE
        if _has_column(table, "search_vector"):
            rows = _query(
                f"SELECT {cols}, "
                f"ts_rank(search_vector, plainto_tsquery('simple', %s)) AS relevance "
                f"FROM {table} "
                f"WHERE search_vector @@ plainto_tsquery('simple', %s) "
                f"ORDER BY relevance DESC LIMIT %s OFFSET %s",
                (query, query, per_table_limit, offset),
                limit=per_table_limit,
            )
        else:
            rows = _query(
                f"SELECT {cols} FROM {table} "
                f"WHERE name ILIKE %s ORDER BY name LIMIT %s OFFSET %s",
                (f"%{query}%", per_table_limit, offset),
                limit=per_table_limit,
            )

        if rows:
            # Remove the relevance score from output
            for r in rows:
                r.pop("relevance", None)
            results[table] = rows

    if not results:
        return f"No results found for '{query}'. Try different keywords or check entity_type."

    if entity_type:
        # Single table search — flat result
        return json.dumps({
            "entity_type": entity_type,
            "query": query,
            "results": results.get(entity_type, []),
        }, ensure_ascii=False, indent=2, default=str)

    # Multi-table — grouped
    output = {"query": query, "results_by_type": {}}
    for table, rows in results.items():
        output["results_by_type"][table] = {
            "count": len(rows),
            "matches": rows,
        }
    return json.dumps(output, ensure_ascii=False, indent=2, default=str)


@mcp.tool()
def get_entity(entity_type: str, name: str) -> str:
    """Get FULL details for a single entity by exact or partial name.

    Use this after finding the entity name via search() or list_entities().
    Returns ALL fields including long text content.

    Args:
        entity_type: Table name (creatures, items, npcs, etc.)
        name: Entity name (exact or partial match, e.g. "Dragon Lord")
    """
    if entity_type not in ALL_ENTITY_TABLES:
        return f"Invalid entity_type '{entity_type}'. Valid: {', '.join(ALL_ENTITY_TABLES)}"

    if not _has_table(entity_type):
        return f"Table '{entity_type}' not available."

    rows = _query(
        f"SELECT * FROM {entity_type} WHERE name ILIKE %s "
        f"ORDER BY CASE WHEN name ILIKE %s THEN 0 ELSE 1 END, name LIMIT 1",
        (f"%{name}%", name),
    )

    if not rows:
        return f"No {entity_type} found matching '{name}'."

    entity = rows[0]

    # Add tags if available
    if _has_column(entity_type, "tags") and entity.get("tags"):
        entity["tags"] = entity["tags"]

    # Add positions if available
    positions = _query(
        "SELECT x, y, z, context FROM positions WHERE entity_name = %s AND source_table = %s",
        (entity.get("name", name), entity_type),
        limit=10,
    )
    if positions:
        entity["map_positions"] = positions
        for p in positions:
            p["map_url"] = f"https://www.tibiawiki.com.br/wiki/Mapper?coords={p['x']},{p['y']},{p['z']},3"

    return json.dumps(entity, ensure_ascii=False, indent=2, default=str)


@mcp.tool()
def search_by_tags(entity_type: str, tags: list, limit: int = 20) -> str:
    """Find entities that match ALL given tags. Returns compact results.

    Tags are generated automatically from entity data. Examples:
    - creatures: boss, high_hp, high_exp, weak_to_fire, immune_to_death, illusionable, has_rare_loot
    - items: high_tier, imbueable, equipment, weapon, shield, valuable, body_position
    - spells: knight, sorcerer, druid, paladin, premium
    - hunts: great_exp, great_loot, knight, paladin, city_name
    - npcs: buys_items, sells_items, city_name
    - quests: premium, high_level, has_bosses

    Args:
        entity_type: Table name (creatures, items, hunts, etc.)
        tags: List of tags to match (ALL must match)
        limit: Max results (default 20, max 50)
    """
    if entity_type not in ALL_ENTITY_TABLES:
        return f"Invalid entity_type. Valid: {', '.join(ALL_ENTITY_TABLES)}"

    if not _has_table(entity_type) or not _has_column(entity_type, "tags"):
        return f"Tags not available for '{entity_type}'. Use search() instead."

    limit = min(limit, 50)
    cols = _compact_select(entity_type)

    # PostgreSQL array containment: tags @> ARRAY[...]
    rows = _query(
        f"SELECT {cols} FROM {entity_type} "
        f"WHERE tags @> %s::text[] ORDER BY name LIMIT %s",
        (tags, limit),
        limit=limit,
    )

    return json.dumps({
        "entity_type": entity_type,
        "tags_filter": tags,
        "count": len(rows),
        "results": rows,
    }, ensure_ascii=False, indent=2, default=str)


# ─── SMART TOOLS ───────────────────────────────────────────────────

@mcp.tool()
def creature_full_info(name: str, compact: bool = False) -> str:
    """Get complete creature profile: stats, loot with sell prices, hunting places, quest appearances.

    Args:
        name: Creature name (e.g. "Dragon", "Demon", "Hydra")
        compact: True = stats summary + loot names only. False (default) = full details.
    """
    creatures = _query(
        "SELECT * FROM creatures WHERE name ILIKE %s ORDER BY "
        "CASE WHEN name ILIKE %s THEN 0 ELSE 1 END, name LIMIT 1",
        (f"%{name}%", name),
    )
    if not creatures:
        return f"Creature '{name}' not found."

    creature = creatures[0]
    creature_name = creature["name"]

    if compact:
        result = {
            "name": creature_name,
            "hp": creature["hp"],
            "exp": creature["exp"],
            "speed": creature.get("speed"),
            "class": creature.get("creature_class"),
            "type": creature.get("primary_type"),
        }
        # Add element mods as compact dict
        mods = {}
        for elem in ("physical", "earth", "fire", "death", "energy", "holy", "ice"):
            val = creature.get(f"{elem}_mod")
            if val is not None and val != 100:
                mods[elem] = val
        if mods:
            result["element_mods"] = mods
    else:
        result = {"creature": creature}

    if _has_table("creature_drops"):
        loot = _query(
            "SELECT item_name, rarity, npc_value "
            "FROM creature_drops WHERE creature_name = %s "
            "ORDER BY CASE rarity "
            "  WHEN 'common' THEN 1 WHEN 'uncommon' THEN 2 "
            "  WHEN 'semi_rare' THEN 3 WHEN 'rare' THEN 4 "
            "  WHEN 'very_rare' THEN 5 END",
            (creature_name,), limit=50
        )
        if compact:
            result["loot"] = [f"{l['item_name']} ({l['rarity']}, {l.get('npc_value', '?')}gp)" for l in loot]
        else:
            result["loot_with_prices"] = loot

    if _has_table("hunt_creatures"):
        hunts = _query(
            "SELECT hunt_name, city, hunt_level, exp_rating, loot_rating "
            "FROM hunt_creatures WHERE creature_name = %s ORDER BY hunt_level",
            (creature_name,), limit=20
        )
        if compact:
            result["hunts"] = [h["hunt_name"] for h in hunts]
        else:
            result["hunting_places"] = hunts

    if _has_table("quest_bosses"):
        quests = _query(
            "SELECT quest_name, quest_level, reward "
            "FROM quest_bosses WHERE creature_name = %s",
            (creature_name,), limit=10
        )
        if quests:
            result["boss_in_quests"] = quests

    return json.dumps(result, ensure_ascii=False, indent=2, default=str)


@mcp.tool()
def where_to_get_item(item_name: str) -> str:
    """Find all ways to obtain an item: creature drops, NPC shops, and quest rewards.

    Args:
        item_name: Item name (e.g. "Magic Plate Armor", "Dragon Scale")
    """
    items = _query(
        "SELECT name, item_class, npc_value, value, dropped_by, buy_from "
        "FROM items WHERE name ILIKE %s ORDER BY "
        "CASE WHEN name ILIKE %s THEN 0 ELSE 1 END, name LIMIT 1",
        (f"%{item_name}%", item_name),
    )
    if not items:
        return f"Item '{item_name}' not found."

    item = items[0]
    real_name = item["name"]
    result = {"item": item}

    if _has_table("creature_drops"):
        drops = _query(
            "SELECT creature_name, rarity, creature_hp, creature_exp "
            "FROM creature_drops WHERE item_name = %s "
            "ORDER BY CASE rarity "
            "  WHEN 'common' THEN 1 WHEN 'uncommon' THEN 2 "
            "  WHEN 'semi_rare' THEN 3 WHEN 'rare' THEN 4 "
            "  WHEN 'very_rare' THEN 5 END",
            (real_name,), limit=30
        )
        result["dropped_by_creatures"] = drops

    if _has_table("npc_trades"):
        sellers = _query(
            "SELECT npc_name, city, npc_value FROM npc_trades "
            "WHERE item_name = %s AND npc_sells = true ORDER BY city",
            (real_name,), limit=20
        )
        result["sold_by_npcs"] = sellers

    quest_rewards = _query(
        "SELECT name, level, level_req, location, reward "
        "FROM quests WHERE reward ILIKE %s ORDER BY name",
        (f"%{real_name}%",), limit=20
    )
    result["quest_rewards"] = quest_rewards

    return json.dumps(result, ensure_ascii=False, indent=2, default=str)


@mcp.tool()
def where_to_sell_item(item_name: str) -> str:
    """Find NPCs that buy a specific item, with city and price.

    Args:
        item_name: Item name (e.g. "Demon Horn", "Dragon Scale")
    """
    items = _query(
        "SELECT name, npc_value FROM items WHERE name ILIKE %s ORDER BY "
        "CASE WHEN name ILIKE %s THEN 0 ELSE 1 END, name LIMIT 1",
        (f"%{item_name}%", item_name),
    )
    if not items:
        return f"Item '{item_name}' not found."

    real_name = items[0]["name"]
    result = {"item": real_name, "npc_value": items[0]["npc_value"]}

    if _has_table("npc_trades"):
        buyers = _query(
            "SELECT npc_name, city, npc_value FROM npc_trades "
            "WHERE item_name = %s AND npc_buys = true ORDER BY city",
            (real_name,), limit=20
        )
        result["buy_npcs"] = buyers

    return json.dumps(result, ensure_ascii=False, indent=2, default=str)


@mcp.tool()
def recommend_hunt(level: int, vocation: str = "", compact: bool = True) -> str:
    """Recommend hunting places for a given level and vocation.

    Args:
        level: Character level (e.g. 80, 150, 300)
        vocation: Vocation name (optional, e.g. "knight", "sorcerer", "paladin", "druid")
        compact: True (default) = name, city, level, ratings only. False = full details + creatures.
    """
    conditions = ["level <= %s", "level >= %s"]
    params = [level + 50, max(1, level - 30)]

    if vocation:
        conditions.append("(vocation ILIKE %s OR vocation ILIKE '%all%' OR vocation IS NULL)")
        params.append(f"%{vocation}%")

    where = " AND ".join(conditions)

    if compact:
        cols = "name, city, level, vocation, exp_rating, loot_rating"
    else:
        cols = ("name, city, location, level, vocation, difficulty, "
                "exp_rating, loot_rating, rare_items, info")

    hunts = _query(
        f"SELECT {cols} FROM hunts WHERE {where} "
        f"ORDER BY exp_rating DESC NULLS LAST, loot_rating DESC NULLS LAST LIMIT 15",
        params,
    )

    if not hunts:
        return f"No hunts found for level {level}. Try adjusting the level range."

    if not compact and _has_table("hunt_creatures"):
        for hunt in hunts:
            creatures = _query(
                "SELECT creature_name, creature_hp, creature_exp "
                "FROM hunt_creatures WHERE hunt_name = %s LIMIT 10",
                (hunt["name"],), limit=10
            )
            hunt["creatures"] = creatures

    return _format(hunts)


@mcp.tool()
def profit_analysis(creature_name: str) -> str:
    """Estimate gold profit per kill for a creature based on NPC loot prices.

    Args:
        creature_name: Creature name (e.g. "Dragon", "Demon", "Hydra")
    """
    creatures = _query(
        "SELECT name, hp, exp FROM creatures WHERE name ILIKE %s ORDER BY "
        "CASE WHEN name ILIKE %s THEN 0 ELSE 1 END, name LIMIT 1",
        (f"%{creature_name}%", creature_name),
    )
    if not creatures:
        return f"Creature '{creature_name}' not found."

    creature = creatures[0]
    real_name = creature["name"]
    result = {"creature": real_name, "hp": creature["hp"], "exp": creature["exp"]}

    if not _has_table("creature_drops"):
        return json.dumps({"error": "creature_drops view not available."}, default=str)

    loot = _query(
        "SELECT item_name, rarity, npc_value "
        "FROM creature_drops WHERE creature_name = %s AND npc_value IS NOT NULL AND npc_value > 0 "
        "ORDER BY npc_value DESC",
        (real_name,), limit=50
    )

    rarity_rates = {
        "common": 0.25, "uncommon": 0.10, "semi_rare": 0.05,
        "rare": 0.02, "very_rare": 0.005,
    }

    total_estimated = 0
    loot_analysis = []
    for item in loot:
        rate = rarity_rates.get(item["rarity"], 0.01)
        expected_gold = round(item["npc_value"] * rate, 1)
        total_estimated += expected_gold
        loot_analysis.append({
            "item": item["item_name"],
            "rarity": item["rarity"],
            "npc_value": item["npc_value"],
            "est_drop_rate": f"{rate*100:.1f}%",
            "est_gold_per_kill": expected_gold,
        })

    result["loot_analysis"] = loot_analysis
    result["estimated_gold_per_kill"] = round(total_estimated, 1)
    result["note"] = "Drop rates are rough estimates. Actual rates vary."
    return json.dumps(result, ensure_ascii=False, indent=2, default=str)


@mcp.tool()
def creature_weakness(element: str) -> str:
    """Find creatures weak to a specific damage element (mod > 100%).

    Args:
        element: Damage element (physical, earth, fire, death, energy, holy, ice)
    """
    valid_elements = ["physical", "earth", "fire", "death", "energy", "holy", "ice"]
    element = element.lower().strip()

    if element not in valid_elements:
        return f"Invalid element '{element}'. Valid: {', '.join(valid_elements)}"

    col = f"{element}_mod"
    rows = _query(
        f"SELECT name, hp, exp, {col} as weakness_percent, creature_class "
        f"FROM creatures WHERE {col} IS NOT NULL AND {col} > 100 "
        f"ORDER BY {col} DESC, exp DESC LIMIT 20",
    )

    if not rows:
        return f"No creatures found with weakness to {element}."

    return f"Creatures weak to {element} (mod > 100%):\n\n" + _format(rows)


@mcp.tool()
def items_for_vocation(vocation: str, body_position: str = "") -> str:
    """Find equipment suitable for a specific vocation.

    Args:
        vocation: Vocation name (e.g. "knight", "sorcerer", "paladin", "druid")
        body_position: Optional body slot filter (e.g. "helmet", "armor", "legs", "shield")
    """
    conditions = [
        "(voc_required ILIKE %s OR voc_required IS NULL OR voc_required = '')"
    ]
    params = [f"%{vocation}%"]

    if body_position:
        conditions.append("body_position ILIKE %s")
        params.append(f"%{body_position}%")

    where = " AND ".join(conditions)

    rows = _query(
        f"SELECT name, item_class, body_position, armor, attack, defense, "
        f"level_required, resist, skillboost, "
        f"npc_value, imbuement_slots, classification "
        f"FROM items WHERE {where} "
        f"AND (armor IS NOT NULL OR attack IS NOT NULL OR defense IS NOT NULL) "
        f"ORDER BY COALESCE(classification, 0) DESC, "
        f"COALESCE(armor, 0) + COALESCE(attack, 0) + COALESCE(defense, 0) DESC "
        f"LIMIT 20",
        params,
    )

    if not rows:
        return f"No equipment found for vocation '{vocation}'."
    return _format(rows)


@mcp.tool()
def compare_creatures(name1: str, name2: str) -> str:
    """Compare two creatures side by side — stats and elemental weaknesses.

    Args:
        name1: First creature name
        name2: Second creature name
    """
    rows = _query(
        "SELECT name, hp, exp, speed, defense, mitigation, charm_points, "
        "physical_mod, earth_mod, fire_mod, death_mod, energy_mod, holy_mod, ice_mod, "
        "immunities, creature_class "
        "FROM creatures WHERE name ILIKE %s OR name ILIKE %s ORDER BY name LIMIT 2",
        (f"%{name1}%", f"%{name2}%"),
    )
    return _format(rows)


# ─── MAP & POSITION TOOLS ─────────────────────────────────────────

@mcp.tool()
def get_map_url(x: int, y: int, z: int, zoom: int = 3) -> str:
    """Generate a TibiaWiki map URL for given coordinates.

    Args:
        x: Map X coordinate (e.g. 33070 for Ankrahmun)
        y: Map Y coordinate (e.g. 32882)
        z: Floor (0-15, 7=ground level)
        zoom: Zoom level (1-5, default 3)
    """
    url = f"https://www.tibiawiki.com.br/wiki/Mapper?coords={x},{y},{z},{zoom}"
    return json.dumps({
        "url": url,
        "coordinates": {"x": x, "y": y, "z": z},
        "floor": "underground" if z < 7 else ("ground" if z == 7 else "above ground"),
    }, indent=2)


@mcp.tool()
def search_by_position(x: int, y: int, z: int, radius: int = 50) -> str:
    """Find all entities near a map position within a given radius.

    Args:
        x: Map X coordinate
        y: Map Y coordinate
        z: Floor (0-15)
        radius: Search radius in sqm (default 50, max 500)
    """
    radius = min(radius, 500)

    rows = _query(
        "SELECT entity_name, source_table, x, y, z, context, "
        "GREATEST(ABS(x - %s), ABS(y - %s)) AS distance "
        "FROM positions "
        "WHERE z = %s AND x BETWEEN %s AND %s AND y BETWEEN %s AND %s "
        "ORDER BY distance ASC LIMIT 30",
        (x, y, z, x - radius, x + radius, y - radius, y + radius),
        limit=30,
    )

    if not rows:
        return f"No entities found near ({x}, {y}, {z}) within radius {radius}."

    for row in rows:
        row["map_url"] = f"https://www.tibiawiki.com.br/wiki/Mapper?coords={row['x']},{row['y']},{row['z']},3"

    return json.dumps({
        "center": {"x": x, "y": y, "z": z},
        "radius": radius,
        "results": rows,
        "center_map_url": f"https://www.tibiawiki.com.br/wiki/Mapper?coords={x},{y},{z},3",
    }, ensure_ascii=False, indent=2, default=str)


@mcp.tool()
def nearby_entities(entity_name: str, radius: int = 100) -> str:
    """Find entities near a named entity on the map.

    Args:
        entity_name: Name of entity to search around (e.g. "Rashid", "Coastwood 1")
        radius: Search radius in sqm (default 100, max 500)
    """
    positions = _query(
        "SELECT DISTINCT entity_name, source_table, x, y, z "
        "FROM positions WHERE entity_name ILIKE %s LIMIT 5",
        (f"%{entity_name}%",),
        limit=5,
    )

    if not positions:
        return f"No map position found for '{entity_name}'."

    radius = min(radius, 500)
    all_results = []

    for pos in positions:
        x, y, z = pos["x"], pos["y"], pos["z"]

        nearby = _query(
            "SELECT entity_name, source_table, x, y, z, "
            "GREATEST(ABS(x - %s), ABS(y - %s)) AS distance "
            "FROM positions "
            "WHERE z = %s AND x BETWEEN %s AND %s AND y BETWEEN %s AND %s "
            "AND NOT (entity_name = %s AND x = %s AND y = %s) "
            "ORDER BY distance ASC LIMIT 20",
            (x, y, z, x - radius, x + radius, y - radius, y + radius,
             pos["entity_name"], x, y),
            limit=20,
        )

        all_results.append({
            "origin": {
                "entity": pos["entity_name"],
                "type": pos["source_table"],
                "position": {"x": x, "y": y, "z": z},
                "map_url": f"https://www.tibiawiki.com.br/wiki/Mapper?coords={x},{y},{z},3",
            },
            "nearby": nearby,
        })

    return json.dumps(all_results, ensure_ascii=False, indent=2, default=str)


# ─── SEMANTIC SEARCH ───────────────────────────────────────────────

@mcp.tool()
def semantic_search(question: str, entity_type: str = "", limit: int = 5) -> str:
    """Search by meaning using AI embeddings. Use for natural language questions.

    Unlike keyword search, this understands semantics:
    - "creatures that heal themselves" -> finds self-healing creatures
    - "what happened to the elves?" -> finds relevant lore books
    - "good items for a mage at level 100" -> finds relevant equipment

    Falls back to keyword search if vector index is unavailable.

    Args:
        question: Natural language question or description
        entity_type: Filter to specific table (optional)
        limit: Max results (default 5)
    """
    try:
        from src.indexer import query_index
        results = query_index(question, entity_type=entity_type, limit=limit)
        if results is not None:
            return json.dumps({
                "method": "semantic (vector similarity)",
                "question": question,
                "results": results,
            }, ensure_ascii=False, indent=2, default=str)
    except Exception as e:
        logger.debug("Semantic search unavailable: %s", e)

    # Fallback to keyword search
    fallback = search(question, entity_type=entity_type, limit=limit)
    return f"(Semantic search unavailable, using keyword fallback)\n\n{fallback}"


# ─── RANKING TOOLS ─────────────────────────────────────────────────

# Compact columns for views (used by rank_entities)
VIEW_COMPACT_COLUMNS = {
    "creature_drops": ["creature_name", "item_name", "npc_value", "rarity"],
    "npc_trades": ["npc_name", "item_name", "npc_value", "npc_sells", "npc_buys", "city"],
    "hunt_creatures": ["hunt_name", "creature_name", "creature_hp", "creature_exp"],
    "quest_bosses": ["quest_name", "creature_name"],
}

NUMERIC_TYPES = {"integer", "bigint", "smallint", "numeric", "real", "double precision"}


def _is_numeric_column(table, column):
    """Check if a column exists in the table and has a numeric type."""
    rows = _query(
        "SELECT data_type FROM information_schema.columns "
        "WHERE table_name = %s AND column_name = %s",
        (table, column), limit=1,
    )
    if not rows:
        # Also check materialized view columns via pg_attribute
        rows = _query(
            "SELECT format_type(a.atttypid, a.atttypmod) as data_type "
            "FROM pg_attribute a JOIN pg_class c ON a.attrelid = c.oid "
            "WHERE c.relname = %s AND a.attname = %s AND a.attnum > 0",
            (table, column), limit=1,
        )
    if not rows:
        return False
    return rows[0]["data_type"].lower() in NUMERIC_TYPES


@mcp.tool()
def rank_entities(
    entity_type: str,
    sort_by: str,
    limit: int = 20,
    order: str = "desc",
    min_value: int = None,
    max_value: int = None,
    filter_column: str = "",
    filter_value: str = "",
) -> str:
    """Rank entities by a numeric column. Best for "most expensive", "strongest", "highest exp", etc.

    Examples:
      rank_entities("items", "npc_value") -> most expensive items
      rank_entities("creatures", "exp") -> highest exp creatures
      rank_entities("creatures", "hp") -> tankiest creatures
      rank_entities("items", "armor", filter_column="body_position", filter_value="armor") -> best body armors
      rank_entities("items", "attack", filter_column="item_class", filter_value="Espadas") -> best swords
      rank_entities("creature_drops", "npc_value") -> most valuable loot drops

    Note: This wiki is in Portuguese. Filter values use PT names (e.g. "Espadas" not "Swords",
    "Machados" not "Axes", "Armas" for weapons). Use search() first if unsure about category names.

    Args:
        entity_type: Table or view name (creatures, items, spells, hunts, creature_drops, etc.)
        sort_by: Numeric column to rank by (npc_value, exp, hp, armor, attack, defense, mana, etc.)
        limit: Number of results (default 20, max 50)
        order: "desc" (highest first, default) or "asc" (lowest first)
        min_value: Optional minimum value filter on sort_by column
        max_value: Optional maximum value filter on sort_by column
        filter_column: Optional column to filter on (e.g. "item_class", "creature_class", "body_position")
        filter_value: Value to match for filter_column (case-insensitive partial match)
    """
    # Validate entity_type
    valid_tables = ALL_ENTITY_TABLES + VIEW_TABLES
    if entity_type not in valid_tables:
        return f"Unknown entity_type '{entity_type}'. Valid: {', '.join(valid_tables)}"

    # Validate sort_by is numeric
    if not _is_numeric_column(entity_type, sort_by):
        return (f"Column '{sort_by}' is not a valid numeric column in '{entity_type}'. "
                f"Use describe_tables('{entity_type}') to see available columns.")

    # Validate filter_column if provided
    if filter_column:
        if not _has_column(entity_type, filter_column):
            return f"Column '{filter_column}' does not exist in '{entity_type}'."

    # Determine SELECT columns
    compact = VIEW_COMPACT_COLUMNS.get(entity_type) or COMPACT_COLUMNS.get(entity_type, ["name"])
    select_cols = list(compact)
    if sort_by not in select_cols:
        select_cols.append(sort_by)
    valid_cols = [c for c in select_cols if _has_column(entity_type, c)]
    if not valid_cols:
        valid_cols = ["name", sort_by] if _has_column(entity_type, "name") else [sort_by]

    # Build query with parameterized values
    limit = min(max(1, limit), 50)
    order_dir = "ASC" if order.lower() == "asc" else "DESC"

    # Column and table names are validated above, safe to interpolate
    where_clauses = [f"{sort_by} IS NOT NULL"]
    params = []

    if min_value is not None:
        where_clauses.append(f"{sort_by} >= %s")
        params.append(min_value)
    if max_value is not None:
        where_clauses.append(f"{sort_by} <= %s")
        params.append(max_value)
    if filter_column and filter_value:
        where_clauses.append(f"{filter_column} ILIKE %s")
        params.append(f"%{filter_value}%")

    where_sql = " AND ".join(where_clauses)
    sql = (f"SELECT {', '.join(valid_cols)} FROM {entity_type} "
           f"WHERE {where_sql} ORDER BY {sort_by} {order_dir} LIMIT {limit}")

    try:
        rows = _query(sql, tuple(params), limit=limit)
        return _format(rows)
    except Exception as e:
        return f"Query error: {e}"


# ─── UTILITY TOOLS ─────────────────────────────────────────────────

@mcp.tool()
def query_database(sql_query: str) -> str:
    """Execute a read-only SQL SELECT on the TibiaWiki database.

    TABLES AND KEY COLUMNS:

    items (5000+ rows):
      name TEXT, npc_value INTEGER (gold price NPCs pay — USE THIS for price queries),
      value TEXT (raw wiki text, NOT a number — do NOT use for price!),
      sell_to TEXT (NPC names who buy it — NOT a price!),
      buy_from TEXT (NPC names who sell it — NOT a price!),
      item_class TEXT, primary_type TEXT,
      body_position TEXT (helmet/armor/legs/boots/shield/weapon/ring/amulet/ammo),
      armor INTEGER, attack INTEGER, defense INTEGER, classification INTEGER (tier 0-4),
      level_required INTEGER, resist TEXT, skillboost TEXT,
      damage TEXT, damage_type TEXT, element_attack TEXT, augments TEXT,
      mana INTEGER, range INTEGER, charges INTEGER, enchantable BOOLEAN,
      imbuement_slots INTEGER, weight NUMERIC, voc_required TEXT,
      tags TEXT[], summary TEXT

    creatures (2000+ rows):
      name TEXT, hp INTEGER, exp INTEGER, creature_class TEXT, primary_type TEXT,
      speed INTEGER, armor INTEGER, physical_mod INTEGER, fire_mod INTEGER,
      ice_mod INTEGER, earth_mod INTEGER, energy_mod INTEGER, holy_mod INTEGER,
      death_mod INTEGER (damage modifiers: 100=normal, >100=weak, 0=immune),
      tags TEXT[], summary TEXT

    spells: name, words, mana INTEGER, mag_level INTEGER, vocations TEXT, magic_type TEXT
    npcs: name, job, city, subarea, buys TEXT (item names), sells TEXT (item names)
    hunts: name, level INTEGER, exp_rating INTEGER (1-5), loot_rating INTEGER (1-5), vocation, city
    quests: name, level INTEGER, reward TEXT, location TEXT, premium BOOLEAN
    positions: page_id, source_table, entity_name, x INTEGER, y INTEGER, z INTEGER, context

    VIEWS (materialized):
      creature_drops (16000+ rows): creature_name, item_name, npc_value INTEGER, rarity TEXT
        (rarity values: common, uncommon, semi_rare, rare, very_rare)
      npc_trades (~43 rows — INCOMPLETE, prefer items.npc_value for prices):
        npc_name, item_name, npc_value INTEGER, npc_sells BOOLEAN, npc_buys BOOLEAN, city
      hunt_creatures: hunt_name, creature_name, creature_hp, creature_exp
      quest_bosses: quest_name, creature_name

    Other tables: achievements, mounts, outfits, imbuements, books, buildings,
    worlds, runes, world_quests, world_changes, familiars, tasks, updates, fansites.
    Most have: name, page_id, tags[], summary, notes.

    EXAMPLE QUERIES:
      Most expensive items: SELECT name, npc_value FROM items WHERE npc_value IS NOT NULL ORDER BY npc_value DESC LIMIT 20
      Strongest creatures: SELECT name, hp, exp FROM creatures ORDER BY exp DESC LIMIT 20
      Best loot drops: SELECT creature_name, item_name, npc_value, rarity FROM creature_drops WHERE npc_value > 1000 ORDER BY npc_value DESC LIMIT 20
      Items by type: SELECT name, armor, npc_value FROM items WHERE body_position = 'armor' AND armor IS NOT NULL ORDER BY armor DESC LIMIT 20
      Creatures weak to fire: SELECT name, hp, exp, fire_mod FROM creatures WHERE fire_mod > 100 ORDER BY fire_mod DESC LIMIT 20

    WARNINGS:
      - items.value is TEXT (raw wiki), NOT a price. Use items.npc_value (INTEGER).
      - items.sell_to / buy_from contain NPC names, NOT prices.
      - npc_trades has only ~43 rows (very incomplete). Query items.npc_value directly.
      - Creature _mod columns: 100=neutral, >100=weak, <100=resistant, 0=immune.

    Args:
        sql_query: A SELECT SQL query (read-only, max 30 results)
    """
    cleaned = sql_query.strip().upper()
    if not cleaned.startswith("SELECT"):
        return "Error: Only SELECT queries are allowed."

    for keyword in ("INSERT", "UPDATE", "DELETE", "DROP", "ALTER", "CREATE", "TRUNCATE"):
        if keyword in cleaned:
            return f"Error: {keyword} is not allowed. Only SELECT queries."

    try:
        rows = _query(sql_query, limit=30)
        return _format(rows)
    except Exception as e:
        return f"Query error: {e}"


if __name__ == "__main__":
    mcp.run(transport="sse")
