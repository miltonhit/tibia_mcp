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
the MMORPG Tibia. You can search for creatures, items, spells, NPCs, quests,
achievements, mounts, outfits, imbuements, and hunting places.

SMART TOOLS (use these first):
- smart_search: Global keyword search across ALL tables. Use when unsure which entity type to search.
- creature_full_info: Complete creature profile with loot, hunts, and sell locations.
- where_to_get_item: Find all sources for an item (creature drops + NPC shops).
- where_to_sell_item: Find NPCs that buy a specific item, with city and price.
- recommend_hunt: Get hunt recommendations for a level/vocation combo.
- profit_analysis: Estimate gold/kill for a creature based on NPC loot prices.
- creature_weakness: Find creatures vulnerable to a specific damage element.
- items_for_vocation: Find equipment for a specific vocation.

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

    Searches creatures, items, spells, NPCs, quests, achievements, and hunts
    using full-text search with relevance ranking. Use this when you don't know
    which entity type to look for.

    Args:
        query: Keywords to search for (e.g. "fire dragon", "ice protection", "thais quest")
    """
    results = {}

    # Full-text search tables with search_vector column
    fts_tables = [
        ("creatures", "name", ["hp", "exp", "creature_class", "primary_type"]),
        ("items", "name", ["item_class", "primary_type", "npc_value"]),
        ("spells", "name", ["words", "subclass", "mana", "magic_type"]),
        ("npcs", "name", ["job", "city"]),
        ("quests", "name", ["level", "reward", "location"]),
        ("achievements", "name", ["grade", "points", "description"]),
        ("hunts", "name", ["city", "level", "exp_rating", "loot_rating"]),
    ]

    for table, name_col, extra_cols in fts_tables:
        cols = ", ".join([name_col] + extra_cols)

        if _has_column(table, "search_vector"):
            # Use full-text search with ranking
            rows = _query(
                f"SELECT {cols}, "
                f"ts_rank(search_vector, plainto_tsquery('simple', %s)) AS relevance "
                f"FROM {table} "
                f"WHERE search_vector @@ plainto_tsquery('simple', %s) "
                f"ORDER BY relevance DESC LIMIT 5",
                (query, query), limit=5
            )
        else:
            # Fallback: ILIKE on name
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
    # Get creature base info
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

    # Get loot with NPC sell prices (from materialized view)
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

    # Get hunts where this creature appears
    if _has_table("hunt_creatures"):
        hunts = _query(
            "SELECT hunt_name, city, hunt_level, exp_rating, loot_rating "
            "FROM hunt_creatures WHERE creature_name = %s ORDER BY hunt_level",
            (creature_name,), limit=20
        )
        result["hunting_places"] = hunts

    # Get quests where this is a boss
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
    # Find the item first
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

    # Creatures that drop it (from materialized view)
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

    # NPCs that sell it
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
        # Fallback: search in items.sell_to
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

    # Enrich with creature details if view exists
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
    # Find creature
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

    # Estimate based on rarity tiers (rough drop rate estimates)
    rarity_rates = {
        "common": 0.25,      # ~25% chance
        "uncommon": 0.10,    # ~10%
        "semi_rare": 0.05,   # ~5%
        "rare": 0.02,        # ~2%
        "very_rare": 0.005,  # ~0.5%
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
    achievements, mounts, outfits, imbuements, hunts.

    Materialized views: creature_drops, npc_trades, hunt_creatures, quest_bosses.

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
