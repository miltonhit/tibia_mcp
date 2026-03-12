"""MCP Server for TibiaWiki database.

Exposes the PostgreSQL database as tools for AI chat integration.
Supports querying creatures, items, spells, NPCs, quests, and more.
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

Use the search tools to find specific entries, or the SQL tool for advanced queries.
Data comes from https://www.tibiawiki.com.br/
""")


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


def _format_results(rows):
    """Format query results as readable text."""
    if not rows:
        return "No results found."
    return json.dumps(rows, ensure_ascii=False, indent=2, default=str)


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
    return _format_results(rows)


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
    return _format_results(rows)


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
    return _format_results(rows)


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
    return _format_results(rows)


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
    return _format_results(rows)


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
    return _format_results(rows)


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
    return _format_results(rows)


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
    return _format_results(rows)


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
    return _format_results(rows)


@mcp.tool()
def query_database(sql_query: str) -> str:
    """Execute a read-only SQL query on the TibiaWiki database.

    Available tables: raw_pages, creatures, items, spells, npcs, quests,
    achievements, mounts, outfits, imbuements, hunts.

    Args:
        sql_query: A SELECT SQL query (read-only, max 20 results)
    """
    # Basic safety check - only allow SELECT
    cleaned = sql_query.strip().upper()
    if not cleaned.startswith("SELECT"):
        return "Error: Only SELECT queries are allowed."

    for keyword in ("INSERT", "UPDATE", "DELETE", "DROP", "ALTER", "CREATE", "TRUNCATE"):
        if keyword in cleaned:
            return f"Error: {keyword} is not allowed. Only SELECT queries."

    try:
        rows = _query(sql_query, limit=20)
        return _format_results(rows)
    except Exception as e:
        return f"Query error: {e}"


@mcp.tool()
def get_database_stats() -> str:
    """Get statistics about the TibiaWiki database.

    Shows the number of records in each table.
    """
    tables = ["raw_pages", "creatures", "items", "spells", "npcs", "quests",
              "achievements", "mounts", "outfits", "imbuements", "hunts"]
    stats = {}
    conn = _get_conn()
    try:
        with conn.cursor() as cur:
            for table in tables:
                try:
                    cur.execute(f"SELECT count(*) as cnt FROM {table}")
                    stats[table] = cur.fetchone()["cnt"]
                except Exception:
                    stats[table] = "table not found"
    finally:
        conn.close()

    return json.dumps(stats, indent=2)


if __name__ == "__main__":
    mcp.run()
