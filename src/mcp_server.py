"""MCP Server for TibiaWiki database.

Exposes the PostgreSQL database as tools for AI chat integration via SSE.
Supports querying creatures, items, spells, NPCs, quests, and more,
with intelligent cross-entity search and relationship analysis.
"""

import json
import logging

from mcp.server.fastmcp import FastMCP
import psycopg2
from psycopg2.extras import RealDictCursor

from src.config import DATABASE_URL

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

mcp = FastMCP("TibiaWiki", instructions="""
You have access to a comprehensive TibiaWiki database with information about
the MMORPG Tibia. This covers ALL content from the wiki including:

ENTITIES: creatures, items, spells, NPCs, quests, achievements, mounts,
outfits, imbuements, hunting places, books/lore, buildings/houses, game worlds,
runes, world quests, world changes, familiars, tasks, updates, fansites.

MAP & POSITIONS: Every entity with coordinates has them stored in a positions
table. You can search by coordinates, find nearby entities, calculate distances.

SMART TOOLS (use these first):
- smart_search: Global keyword search across ALL 20 tables. Use when unsure which entity type to search.
- creature_full_info: Complete creature profile with loot, hunts, and sell locations.
- where_to_get_item: Find all sources for an item (creature drops + NPC shops).
- where_to_sell_item: Find NPCs that buy a specific item, with city and price.
- recommend_hunt: Get hunt recommendations for a level/vocation combo.
- profit_analysis: Estimate gold/kill for a creature based on NPC loot prices.
- creature_weakness: Find creatures vulnerable to a specific damage element.
- items_for_vocation: Find equipment for a specific vocation.

MAP & POSITION TOOLS:
- get_map_url: Generate TibiaWiki map URL for coordinates.
- search_by_position: Find entities near a map position (x, y, z).
- nearby_entities: Find what's close to a named entity on the map.
- positions_in_area: Find all entities within a rectangular map area.

NEW ENTITY SEARCH TOOLS:
- search_book: Search books/lore by name or content.
- search_building: Search houses/buildings by name, street, or city.
- search_world: Search game worlds/servers.
- search_rune: Search runes by name or damage type.
- search_world_quest: Search world quests/events.
- search_world_change: Search world changes.
- search_familiar: Search familiars by name or vocation.
- search_task: Search tasks.
- search_update: Search game updates by version or content.

BASIC SEARCH TOOLS:
- search_creature, search_item, search_spell, search_npc, search_quest
- search_achievement, search_mount, search_hunt
- compare_creatures

ADVANCED:
- query_database: Raw SQL SELECT for custom queries.
- get_database_stats: Row counts for all tables.

Data from https://www.tibiawiki.com.br/
""")


# ─── Database helpers ──────────────────────────────────────────────

def _get_conn():
    return psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)


def _query(sql, params=None, limit=20):
    """Execute a query and return results as list of dicts."""
    conn = _get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(sql, params or ())
            rows = cur.fetchmany(limit)
            return [dict(r) for r in rows]
    finally:
        conn.close()


def _format(rows):
    """Format query results as readable text."""
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


# ─── SMART TOOLS ───────────────────────────────────────────────────

@mcp.tool()
def smart_search(query: str) -> str:
    """Global intelligent search across ALL TibiaWiki tables.

    Searches creatures, items, spells, NPCs, quests, achievements, hunts,
    books, buildings, worlds, runes, world_quests, world_changes, familiars,
    tasks, updates, fansites using full-text search with relevance ranking.
    Use this when you don't know which entity type to look for.

    Args:
        query: Keywords to search for (e.g. "fire dragon", "ice protection", "thais quest")
    """
    results = {}

    fts_tables = [
        ("creatures", "name", ["hp", "exp", "creature_class", "primary_type"]),
        ("items", "name", ["item_class", "primary_type", "npc_value"]),
        ("spells", "name", ["words", "subclass", "mana", "magic_type"]),
        ("npcs", "name", ["job", "city"]),
        ("quests", "name", ["level", "reward", "location"]),
        ("achievements", "name", ["grade", "points", "description"]),
        ("hunts", "name", ["city", "level", "exp_rating", "loot_rating"]),
        ("books", "name", ["author", "blurb", "location"]),
        ("buildings", "name", ["building_type", "street", "payrent"]),
        ("worlds", "name", ["world_type", "location", "battleye"]),
        ("runes", "name", ["subclass", "damage_type", "words"]),
        ("world_quests", "name", ["quest_type", "frequency", "reward"]),
        ("world_changes", "name", ["change_type", "frequency", "reward"]),
        ("familiars", "name", ["vocation", "hp"]),
        ("tasks", "name", ["reward", "location"]),
        ("updates", "name", ["update_version"]),
        ("fansites", "name", ["fansite_type", "language"]),
    ]

    for table, name_col, extra_cols in fts_tables:
        if not _has_table(table):
            continue

        cols = ", ".join([name_col] + [c for c in extra_cols if _has_column(table, c)])

        if _has_column(table, "search_vector"):
            rows = _query(
                f"SELECT {cols}, "
                f"ts_rank(search_vector, plainto_tsquery('simple', %s)) AS relevance "
                f"FROM {table} "
                f"WHERE search_vector @@ plainto_tsquery('simple', %s) "
                f"ORDER BY relevance DESC LIMIT 5",
                (query, query), limit=5
            )
        else:
            rows = _query(
                f"SELECT {cols} FROM {table} "
                f"WHERE {name_col} ILIKE %s ORDER BY {name_col} LIMIT 5",
                (f"%{query}%",), limit=5
            )

        if rows:
            results[table] = rows

    if not results:
        return f"No results found for '{query}'. Try different keywords or use a specific search tool."

    output = []
    for table, rows in results.items():
        output.append(f"=== {table.upper()} ({len(rows)} matches) ===")
        output.append(json.dumps(rows, ensure_ascii=False, indent=2, default=str))
    return "\n\n".join(output)


@mcp.tool()
def creature_full_info(name: str) -> str:
    """Get complete information about a creature including stats, loot, hunts, and where to sell drops.

    This combines creature stats + loot analysis + hunt locations + NPC sell prices
    into a single comprehensive response.

    Args:
        name: Creature name (e.g. "Dragon", "Demon", "Hydra")
    """
    creatures = _query(
        "SELECT * FROM creatures WHERE name ILIKE %s ORDER BY "
        "CASE WHEN name ILIKE %s THEN 0 ELSE 1 END, name LIMIT 1",
        (f"%{name}%", name),
    )
    if not creatures:
        return f"Creature '{name}' not found."

    creature = creatures[0]
    result = {"creature": creature}

    creature_name = creature["name"]

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
        result["loot_with_prices"] = loot

    if _has_table("hunt_creatures"):
        hunts = _query(
            "SELECT hunt_name, city, hunt_level, exp_rating, loot_rating "
            "FROM hunt_creatures WHERE creature_name = %s ORDER BY hunt_level",
            (creature_name,), limit=20
        )
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
    """Find all ways to obtain an item: creature drops and NPC shops.

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
    npc_value = items[0]["npc_value"]

    result = {"item": real_name, "npc_value": npc_value}

    if _has_table("npc_trades"):
        buyers = _query(
            "SELECT npc_name, city, npc_value FROM npc_trades "
            "WHERE item_name = %s AND npc_buys = true ORDER BY city",
            (real_name,), limit=20
        )
        result["buy_npcs"] = buyers
    else:
        result["sell_to_text"] = items[0].get("sell_to", "Unknown")

    return json.dumps(result, ensure_ascii=False, indent=2, default=str)


@mcp.tool()
def recommend_hunt(level: int, vocation: str = "") -> str:
    """Recommend hunting places for a given level and vocation.

    Returns hunts sorted by exp/loot rating with creature details.

    Args:
        level: Character level (e.g. 80, 150, 300)
        vocation: Vocation name (optional, e.g. "knight", "sorcerer", "paladin", "druid")
    """
    conditions = ["level <= %s", "level >= %s"]
    params = [level + 50, max(1, level - 30)]

    if vocation:
        conditions.append("(vocation ILIKE %s OR vocation ILIKE '%all%' OR vocation IS NULL)")
        params.append(f"%{vocation}%")

    where = " AND ".join(conditions)

    hunts = _query(
        f"SELECT name, city, location, level, vocation, difficulty, "
        f"exp_rating, loot_rating, rare_items, info "
        f"FROM hunts WHERE {where} "
        f"ORDER BY exp_rating DESC NULLS LAST, loot_rating DESC NULLS LAST LIMIT 15",
        params,
    )

    if not hunts:
        return f"No hunts found for level {level}. Try adjusting the level range."

    if _has_table("hunt_creatures"):
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

    Analyzes all loot drops and their NPC sell values to estimate income.

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

    result = {
        "creature": real_name,
        "hp": creature["hp"],
        "exp": creature["exp"],
    }

    if not _has_table("creature_drops"):
        return json.dumps({"error": "creature_drops view not available. Run importer first."}, default=str)

    loot = _query(
        "SELECT item_name, rarity, npc_value "
        "FROM creature_drops WHERE creature_name = %s AND npc_value IS NOT NULL AND npc_value > 0 "
        "ORDER BY npc_value DESC",
        (real_name,), limit=50
    )

    rarity_rates = {
        "common": 0.25,
        "uncommon": 0.10,
        "semi_rare": 0.05,
        "rare": 0.02,
        "very_rare": 0.005,
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
    """Find creatures that are weak to a specific damage element.

    A creature is weak when its element_mod > 100 (takes extra damage).

    Args:
        element: Damage element (physical, earth, fire, death, energy, holy, ice)
    """
    valid_elements = ["physical", "earth", "fire", "death", "energy", "holy", "ice"]
    element = element.lower().strip()

    if element not in valid_elements:
        return f"Invalid element '{element}'. Valid: {', '.join(valid_elements)}"

    col = f"{element}_mod"
    rows = _query(
        f"SELECT name, hp, exp, {col} as weakness_percent, creature_class, primary_type "
        f"FROM creatures WHERE {col} IS NOT NULL AND {col} > 100 "
        f"ORDER BY {col} DESC, exp DESC LIMIT 20",
    )

    if not rows:
        return f"No creatures found with weakness to {element}."

    return f"Creatures weak to {element} (mod > 100% = takes extra damage):\n\n" + _format(rows)


@mcp.tool()
def items_for_vocation(vocation: str, body_position: str = "") -> str:
    """Find equipment suitable for a specific vocation.

    Args:
        vocation: Vocation name (e.g. "knight", "sorcerer", "paladin", "druid")
        body_position: Optional body slot filter (e.g. "helmet", "armor", "legs", "shield", "weapon")
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
        f"SELECT name, item_class, primary_type, body_position, "
        f"armor, attack, defense, weight, npc_value, voc_required, "
        f"imbuement_slots, classification "
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


# ─── MAP & POSITION TOOLS ─────────────────────────────────────────

@mcp.tool()
def get_map_url(x: int, y: int, z: int, zoom: int = 3) -> str:
    """Generate a TibiaWiki map URL for given coordinates.

    Returns a clickable URL that opens the TibiaWiki interactive map
    centered on the specified position.

    Args:
        x: Map X coordinate (e.g. 33070 for Ankrahmun)
        y: Map Y coordinate (e.g. 32882)
        z: Map Z coordinate / floor (0-15, where 7 is ground level)
        zoom: Map zoom level (1-5, default 3)
    """
    url = f"https://www.tibiawiki.com.br/wiki/Mapper?coords={x},{y},{z},{zoom}"
    return json.dumps({
        "url": url,
        "coordinates": {"x": x, "y": y, "z": z},
        "floor": "underground" if z < 7 else ("ground" if z == 7 else "above ground"),
    }, indent=2)


@mcp.tool()
def search_by_position(x: int, y: int, z: int, radius: int = 50) -> str:
    """Find all entities near a specific map position within a given radius.

    Searches the positions table for anything close to (x, y, z).
    Uses Chebyshev distance (max of dx, dy) on the same floor.

    Args:
        x: Map X coordinate
        y: Map Y coordinate
        z: Map Z coordinate / floor (0-15)
        radius: Search radius in sqm (default 50, max 500)
    """
    radius = min(radius, 500)

    rows = _query(
        "SELECT entity_name, source_table, x, y, z, context, "
        "ABS(x - %s) + ABS(y - %s) AS manhattan_distance, "
        "GREATEST(ABS(x - %s), ABS(y - %s)) AS chebyshev_distance "
        "FROM positions "
        "WHERE z = %s AND x BETWEEN %s AND %s AND y BETWEEN %s AND %s "
        "ORDER BY chebyshev_distance ASC LIMIT 30",
        (x, y, x, y, z, x - radius, x + radius, y - radius, y + radius),
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

    First looks up the entity's position, then finds everything nearby.

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


@mcp.tool()
def positions_in_area(x_min: int, y_min: int, x_max: int, y_max: int, z: int = 7, source_table: str = "") -> str:
    """Find all entities within a rectangular map area.

    Useful for finding everything on a specific map region or city.

    Args:
        x_min: Minimum X coordinate
        y_min: Minimum Y coordinate
        x_max: Maximum X coordinate
        y_max: Maximum Y coordinate
        z: Floor level (default 7 = ground)
        source_table: Filter by entity type (e.g. "npcs", "buildings"). Empty = all types.
    """
    conditions = ["z = %s", "x BETWEEN %s AND %s", "y BETWEEN %s AND %s"]
    params = [z, x_min, x_max, y_min, y_max]

    if source_table:
        conditions.append("source_table = %s")
        params.append(source_table)

    where = " AND ".join(conditions)

    rows = _query(
        f"SELECT entity_name, source_table, x, y, z "
        f"FROM positions WHERE {where} "
        f"ORDER BY source_table, entity_name LIMIT 50",
        params,
        limit=50,
    )

    if not rows:
        return f"No entities found in area ({x_min},{y_min})-({x_max},{y_max}) floor {z}."

    return _format(rows)


# ─── BASIC SEARCH TOOLS ───────────────────────────────────────────

@mcp.tool()
def search_creature(name: str) -> str:
    """Search for a creature by name (partial match).

    Args:
        name: Creature name to search for (e.g. "Dragon", "Demon")

    Returns information like HP, EXP, loot, abilities, immunities, etc.
    """
    rows = _query(
        "SELECT name, hp, exp, speed, charm_points, defense, mitigation, "
        "creature_class, primary_type, immunities, behavior, "
        "physical_mod, earth_mod, fire_mod, death_mod, energy_mod, holy_mod, ice_mod, "
        "loot_common, loot_uncommon, loot_semi_rare, loot_rare, loot_very_rare, "
        "sounds, notes "
        "FROM creatures WHERE name ILIKE %s ORDER BY name LIMIT 10",
        (f"%{name}%",),
    )
    return _format(rows)


@mcp.tool()
def search_item(name: str) -> str:
    """Search for an item by name (partial match).

    Args:
        name: Item name to search for (e.g. "Magic Plate", "Wand")

    Returns information like armor, attack, defense, weight, value, where to buy/sell, etc.
    """
    rows = _query(
        "SELECT name, item_class, primary_type, armor, attack, defense, weight, "
        "value, npc_value, voc_required, imbuement_slots, classification, "
        "dropped_by, buy_from, sell_to, notes "
        "FROM items WHERE name ILIKE %s ORDER BY name LIMIT 10",
        (f"%{name}%",),
    )
    return _format(rows)


@mcp.tool()
def search_spell(name: str) -> str:
    """Search for a spell by name or words (partial match).

    Args:
        name: Spell name or incantation words (e.g. "exura", "fireball")
    """
    rows = _query(
        "SELECT name, words, subclass, mana, mag_level, exp_level, vocations, "
        "premium, base_power, magic_type, effect, spell_cost, notes "
        "FROM spells WHERE name ILIKE %s OR words ILIKE %s ORDER BY name LIMIT 10",
        (f"%{name}%", f"%{name}%"),
    )
    return _format(rows)


@mcp.tool()
def search_npc(name: str) -> str:
    """Search for an NPC by name or city (partial match).

    Args:
        name: NPC name or city name (e.g. "Rashid", "Thais")
    """
    rows = _query(
        "SELECT name, job, city, subarea, location, buys, sells, notes "
        "FROM npcs WHERE name ILIKE %s OR city ILIKE %s ORDER BY name LIMIT 10",
        (f"%{name}%", f"%{name}%"),
    )
    return _format(rows)


@mcp.tool()
def search_quest(name: str) -> str:
    """Search for a quest by name (partial match).

    Args:
        name: Quest name (e.g. "Annihilator", "Inquisition")
    """
    rows = _query(
        "SELECT name, reward, location, level, level_req, duration, team, "
        "difficulty, premium, dangers, bosses, legend, notes "
        "FROM quests WHERE name ILIKE %s ORDER BY name LIMIT 10",
        (f"%{name}%",),
    )
    return _format(rows)


@mcp.tool()
def search_achievement(name: str) -> str:
    """Search for an achievement by name (partial match).

    Args:
        name: Achievement name (e.g. "Backpack Tourist")
    """
    rows = _query(
        "SELECT name, grade, points, secret, premium, description, notes "
        "FROM achievements WHERE name ILIKE %s ORDER BY name LIMIT 10",
        (f"%{name}%",),
    )
    return _format(rows)


@mcp.tool()
def search_mount(name: str) -> str:
    """Search for a mount by name (partial match).

    Args:
        name: Mount name (e.g. "Blazebringer", "Widow Queen")
    """
    rows = _query(
        "SELECT name, speed, premium, method, attrib, "
        "quest_mount, store_mount, tame_mount, event_mount, notes "
        "FROM mounts WHERE name ILIKE %s ORDER BY name LIMIT 10",
        (f"%{name}%",),
    )
    return _format(rows)


@mcp.tool()
def search_hunt(name: str = "", city: str = "", min_level: int = 0) -> str:
    """Search for hunting places by name, city, or minimum level.

    Args:
        name: Hunt name (partial match, optional)
        city: City name (partial match, optional)
        min_level: Minimum recommended level (optional)
    """
    conditions = []
    params = []

    if name:
        conditions.append("name ILIKE %s")
        params.append(f"%{name}%")
    if city:
        conditions.append("city ILIKE %s")
        params.append(f"%{city}%")
    if min_level > 0:
        conditions.append("level >= %s")
        params.append(min_level)

    where = " AND ".join(conditions) if conditions else "TRUE"

    rows = _query(
        f"SELECT name, city, location, level, vocation, difficulty, "
        f"exp_rating, loot_rating, rare_items, info "
        f"FROM hunts WHERE {where} ORDER BY level, name LIMIT 15",
        params,
    )
    return _format(rows)


# ─── NEW ENTITY SEARCH TOOLS ──────────────────────────────────────

@mcp.tool()
def search_book(name: str) -> str:
    """Search for books/lore texts by name, title, or content.

    Books contain in-game lore, stories, and knowledge from the Tibia world.

    Args:
        name: Book name or keyword to search for (e.g. "Elven Names", "dragon", "banor")
    """
    if not _has_table("books"):
        return "Books table not available. Run the importer first."

    rows = _query(
        "SELECT name, title, author, blurb, location, book_type, text "
        "FROM books WHERE name ILIKE %s OR title ILIKE %s OR blurb ILIKE %s "
        "OR text ILIKE %s ORDER BY name LIMIT 10",
        (f"%{name}%", f"%{name}%", f"%{name}%", f"%{name}%"),
    )
    return _format(rows)


@mcp.tool()
def search_building(name: str = "", street: str = "", city: str = "") -> str:
    """Search for houses and buildings by name, street, or city.

    Returns house info including size, beds, rent, location with map coordinates.

    Args:
        name: Building name (partial match, optional)
        street: Street name (partial match, optional)
        city: City where rent is paid (partial match, optional, e.g. "Thais", "Venore")
    """
    if not _has_table("buildings"):
        return "Buildings table not available. Run the importer first."

    conditions = []
    params = []

    if name:
        conditions.append("name ILIKE %s")
        params.append(f"%{name}%")
    if street:
        conditions.append("street ILIKE %s")
        params.append(f"%{street}%")
    if city:
        conditions.append("payrent ILIKE %s")
        params.append(f"%{city}%")

    where = " AND ".join(conditions) if conditions else "TRUE"

    rows = _query(
        f"SELECT name, building_type, street, location, size, beds, rent, "
        f"payrent, floors, rooms, furnishings "
        f"FROM buildings WHERE {where} ORDER BY name LIMIT 15",
        params,
    )
    return _format(rows)


@mcp.tool()
def search_world(name: str) -> str:
    """Search for Tibia game worlds/servers by name or location.

    Returns server type (PvP mode), location, BattlEye status, etc.

    Args:
        name: World name or location (e.g. "Antica", "Brazil", "Optional PvP")
    """
    if not _has_table("worlds"):
        return "Worlds table not available. Run the importer first."

    rows = _query(
        "SELECT name, world_type, online_since, location, transfer, battleye "
        "FROM worlds WHERE name ILIKE %s OR world_type ILIKE %s OR location ILIKE %s "
        "ORDER BY name LIMIT 20",
        (f"%{name}%", f"%{name}%", f"%{name}%"),
    )
    return _format(rows)


@mcp.tool()
def search_rune(name: str) -> str:
    """Search for runes by name or damage type.

    Returns rune info including damage type, mana to make, level required, buy price.

    Args:
        name: Rune name or damage type (e.g. "Sudden Death", "fire", "ice")
    """
    if not _has_table("runes"):
        return "Runes table not available. Run the importer first."

    rows = _query(
        "SELECT name, subclass, damage_type, words, make_mana, weight, "
        "ml_required, level_required, make_qty, make_voc, premium, "
        "npc_price, store_value, effect "
        "FROM runes WHERE name ILIKE %s OR damage_type ILIKE %s OR words ILIKE %s "
        "ORDER BY name LIMIT 10",
        (f"%{name}%", f"%{name}%", f"%{name}%"),
    )
    return _format(rows)


@mcp.tool()
def search_world_quest(name: str) -> str:
    """Search for world quests and events (e.g. Rise of Devovorga, Lightbearer).

    World quests are server-wide events that happen periodically.

    Args:
        name: World quest name (e.g. "Devovorga", "Lightbearer", "Bewitched")
    """
    if not _has_table("world_quests"):
        return "World quests table not available. Run the importer first."

    rows = _query(
        "SELECT name, quest_type, start_date, end_date, frequency, reward, "
        "location, level, premium, dangers, bosses, legend "
        "FROM world_quests WHERE name ILIKE %s ORDER BY name LIMIT 10",
        (f"%{name}%",),
    )
    return _format(rows)


@mcp.tool()
def search_world_change(name: str) -> str:
    """Search for world changes (dynamic events that alter the game world).

    Args:
        name: World change name (e.g. "Thornback", "Hive", "Feverish")
    """
    if not _has_table("world_changes"):
        return "World changes table not available. Run the importer first."

    rows = _query(
        "SELECT name, change_type, frequency, reward, location, level, "
        "premium, dangers, bosses, legend "
        "FROM world_changes WHERE name ILIKE %s ORDER BY name LIMIT 10",
        (f"%{name}%",),
    )
    return _format(rows)


@mcp.tool()
def search_familiar(name: str = "", vocation: str = "") -> str:
    """Search for familiars (summonable companion creatures).

    Each vocation has a unique familiar: Skullfrost (Knight), Emberwing (Sorcerer),
    Grovebeast (Druid), Thundergiant (Paladin).

    Args:
        name: Familiar name (partial match, optional)
        vocation: Vocation filter (optional, e.g. "knight", "druid")
    """
    if not _has_table("familiars"):
        return "Familiars table not available. Run the importer first."

    conditions = []
    params = []

    if name:
        conditions.append("name ILIKE %s")
        params.append(f"%{name}%")
    if vocation:
        conditions.append("vocation ILIKE %s")
        params.append(f"%{vocation}%")

    where = " AND ".join(conditions) if conditions else "TRUE"

    rows = _query(
        f"SELECT name, hp, summon_cost, vocation, behavior, obtain, notes "
        f"FROM familiars WHERE {where} ORDER BY name LIMIT 10",
        params,
    )
    return _format(rows)


@mcp.tool()
def search_task(name: str) -> str:
    """Search for tasks (repeatable hunting assignments from NPCs like Grizzly Adams).

    Args:
        name: Task name (e.g. "Curos", "Lazaran", "Rottin Wood")
    """
    if not _has_table("tasks"):
        return "Tasks table not available. Run the importer first."

    rows = _query(
        "SELECT name, premium, reward, location, time, level, dangers "
        "FROM tasks WHERE name ILIKE %s ORDER BY name LIMIT 10",
        (f"%{name}%",),
    )
    return _format(rows)


@mcp.tool()
def search_update(name: str) -> str:
    """Search for Tibia game updates by version number or content.

    Args:
        name: Update version or keyword (e.g. "8.6", "12.0", "summer")
    """
    if not _has_table("updates"):
        return "Updates table not available. Run the importer first."

    rows = _query(
        "SELECT name, update_version, update_previous, update_next, update_season "
        "FROM updates WHERE name ILIKE %s OR update_version ILIKE %s "
        "ORDER BY update_version LIMIT 10",
        (f"%{name}%", f"%{name}%"),
    )
    return _format(rows)


# ─── UTILITY TOOLS ─────────────────────────────────────────────────

@mcp.tool()
def compare_creatures(name1: str, name2: str) -> str:
    """Compare two creatures side by side.

    Args:
        name1: First creature name (exact or partial)
        name2: Second creature name (exact or partial)
    """
    rows = _query(
        "SELECT name, hp, exp, speed, defense, mitigation, charm_points, "
        "physical_mod, earth_mod, fire_mod, death_mod, energy_mod, holy_mod, ice_mod, "
        "immunities, loot_rare, loot_very_rare "
        "FROM creatures WHERE name ILIKE %s OR name ILIKE %s ORDER BY name LIMIT 2",
        (f"%{name1}%", f"%{name2}%"),
    )
    return _format(rows)


@mcp.tool()
def query_database(sql_query: str) -> str:
    """Execute a read-only SQL query on the TibiaWiki database.

    Available tables: raw_pages, creatures, items, spells, npcs, quests,
    achievements, mounts, outfits, imbuements, hunts, books, buildings,
    worlds, runes, world_quests, world_changes, familiars, tasks, updates,
    fansites, positions.

    Materialized views: creature_drops, npc_trades, hunt_creatures, quest_bosses.

    The positions table has columns: id, page_id, source_table, entity_name, x, y, z, context.
    Use it for spatial queries (find entities near coordinates, calculate distances, etc).

    Args:
        sql_query: A SELECT SQL query (read-only, max 20 results)
    """
    cleaned = sql_query.strip().upper()
    if not cleaned.startswith("SELECT"):
        return "Error: Only SELECT queries are allowed."

    for keyword in ("INSERT", "UPDATE", "DELETE", "DROP", "ALTER", "CREATE", "TRUNCATE"):
        if keyword in cleaned:
            return f"Error: {keyword} is not allowed. Only SELECT queries."

    try:
        rows = _query(sql_query, limit=20)
        return _format(rows)
    except Exception as e:
        return f"Query error: {e}"


@mcp.tool()
def get_database_stats() -> str:
    """Get statistics about the TibiaWiki database.

    Shows the number of records in each table and materialized view.
    """
    tables = [
        "raw_pages", "creatures", "items", "spells", "npcs", "quests",
        "achievements", "mounts", "outfits", "imbuements", "hunts",
        "books", "buildings", "worlds", "runes", "world_quests",
        "world_changes", "familiars", "tasks", "updates", "fansites",
        "positions",
    ]
    views = ["creature_drops", "npc_trades", "hunt_creatures", "quest_bosses"]

    stats = {}
    conn = _get_conn()
    try:
        with conn.cursor() as cur:
            for table in tables + views:
                try:
                    cur.execute(f"SELECT count(*) as cnt FROM {table}")
                    stats[table] = cur.fetchone()["cnt"]
                except Exception:
                    stats[table] = "not available"
                    conn.rollback()
    finally:
        conn.close()

    return json.dumps(stats, indent=2)


if __name__ == "__main__":
    mcp.run(transport="sse")
