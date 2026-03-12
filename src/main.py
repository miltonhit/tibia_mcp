"""TibiaWiki Downloader - Main orchestrator.

Downloads all content from TibiaWiki via MediaWiki API,
parses infobox templates, and imports into PostgreSQL.
"""

import logging
import sys

from src.api.client import WikiClient
from src.api.paginator import iter_all_pages
from src.api.downloader import download_page_contents
from src.db.connection import get_connection
from src.db.migrator import run_migrations
from src.db.inserter import upsert_raw_pages, upsert_parsed_records
from src.parser import (
    creatures, items, spells, npcs, quests, achievements, mounts, outfits,
    imbuements, hunts, books, buildings, worlds, runes, world_quests,
    world_changes, familiars, tasks, updates, fansites,
)
from src.parser.wikitext import extract_map_coords
from src.tagger import generate_tags, generate_summary

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    stream=sys.stdout,
)
logger = logging.getLogger(__name__)

# All parsers mapped by their template pattern in wikitext
PARSERS = [
    ("Infobox_Criatura", creatures),
    ("Infobox_Item", items),
    ("Infobox_Spell", spells),
    ("Infobox_NPC", npcs),
    ("Infobox_Quest", quests),
    ("Infobox_Achievement", achievements),
    ("Infobox_Mount", mounts),
    ("Infobox_Outfit", outfits),
    ("Infobox_Imbuement", imbuements),
    ("Infobox_Hunts", hunts),
    ("Infobox_Book", books),
    ("Infobox_Building", buildings),
    ("Infobox_World", worlds),
    ("Infobox_Runas", runes),
    ("Infobox_World_Quest", world_quests),
    ("Infobox_World_Change", world_changes),
    ("Infobox Familiar", familiars),
    ("Infobox_Tasks", tasks),
    ("Infobox_Updates", updates),
    ("Infobox_Fansite", fansites),
]


def phase_download(client):
    """Phase 1: Download all pages from wiki into raw_pages."""
    logger.info("=== PHASE 1: Downloading all pages ===")

    # Enumerate all pages in main namespace
    logger.info("Enumerating all pages in namespace 0...")
    all_pages = list(iter_all_pages(client))
    logger.info("Found %d pages total", len(all_pages))

    if not all_pages:
        logger.warning("No pages found! Check API connectivity.")
        return

    # Check which pages we already have
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT page_id FROM raw_pages")
            existing_ids = {row["page_id"] for row in cur.fetchall()}
    finally:
        conn.close()

    # Filter to only new pages
    new_pages = [p for p in all_pages if p["page_id"] not in existing_ids]
    logger.info("%d new pages to download (%d already in database)",
                len(new_pages), len(existing_ids))

    if not new_pages:
        logger.info("All pages already downloaded, skipping phase 1")
        return

    # Download content in batches
    titles = [p["title"] for p in new_pages]
    batch = []
    conn = get_connection()
    try:
        for page_data in download_page_contents(client, titles):
            batch.append(page_data)

            if len(batch) >= 100:
                upsert_raw_pages(conn, batch)
                batch = []

        # Insert remaining
        if batch:
            upsert_raw_pages(conn, batch)
    finally:
        conn.close()

    logger.info("Phase 1 complete: downloaded %d pages", len(new_pages))


def phase_parse_and_import():
    """Phase 2 & 3: Parse infoboxes and import into typed tables."""
    logger.info("=== PHASE 2: Parsing and importing ===")

    conn = get_connection()
    try:
        for template_name, parser_module in PARSERS:
            table = parser_module.TABLE
            columns = parser_module.COLUMNS

            # Find pages with this template (normalize underscore/space)
            search_pattern1 = f"%{{{{{template_name}%"
            search_pattern2 = f"%{{{{{template_name.replace('_', ' ')}%"

            with conn.cursor() as cur:
                cur.execute(
                    "SELECT page_id, content FROM raw_pages "
                    "WHERE NOT is_redirect AND (content LIKE %s OR content LIKE %s)",
                    (search_pattern1, search_pattern2),
                )
                pages = cur.fetchall()

            logger.info("Found %d pages with %s", len(pages), template_name)

            records = []
            errors = 0
            for page in pages:
                try:
                    record = parser_module.parse(page["page_id"], page["content"])
                    if record:
                        records.append(record)
                except Exception as e:
                    errors += 1
                    logger.warning("Parse error for page_id=%d: %s", page["page_id"], e)

            if records:
                upsert_parsed_records(conn, table, records, columns)

            logger.info("Parsed %s: %d records, %d errors", table, len(records), errors)

    finally:
        conn.close()

    logger.info("Phase 2 complete")


def phase_extract_positions():
    """Phase 3: Extract map coordinates from all parsed content into positions table."""
    logger.info("=== PHASE 3: Extracting map positions ===")

    conn = get_connection()
    try:
        # For each parser, scan its text fields for {{mapa|X,Y,Z:zoom|text}} patterns
        table_text_fields = {
            "npcs": ["location", "notes"],
            "buildings": ["location", "notes"],
            "hunts": ["location", "map_coords", "info", "notes"],
            "quests": ["location", "legend", "spoiler", "notes"],
            "creatures": ["location_raid", "notes"],
            "world_quests": ["location", "legend", "notes"],
            "world_changes": ["location", "legend", "notes"],
            "tasks": ["location", "notes"],
            "books": ["location", "notes"],
            "runes": ["notes"],
        }

        total_positions = 0

        for table, fields in table_text_fields.items():
            cols = ", ".join(["page_id", "name"] + fields)
            with conn.cursor() as cur:
                try:
                    cur.execute(f"SELECT {cols} FROM {table}")
                    rows = cur.fetchall()
                except Exception:
                    conn.rollback()
                    continue

            positions = []
            for row in rows:
                page_id = row["page_id"]
                entity_name = row["name"]
                seen = set()
                for field in fields:
                    text = row.get(field)
                    if not text:
                        continue
                    # Also scan raw_pages content for this page_id
                    coords = extract_map_coords(text)
                    for x, y, z in coords:
                        if (x, y, z) not in seen:
                            seen.add((x, y, z))
                            context_snippet = field
                            positions.append((page_id, table, entity_name, x, y, z, context_snippet))

                # Also check raw content for coords not in parsed fields
                with conn.cursor() as cur:
                    cur.execute("SELECT content FROM raw_pages WHERE page_id = %s", (page_id,))
                    raw_row = cur.fetchone()
                if raw_row and raw_row["content"]:
                    raw_coords = extract_map_coords(raw_row["content"])
                    for x, y, z in raw_coords:
                        if (x, y, z) not in seen:
                            seen.add((x, y, z))
                            positions.append((page_id, table, entity_name, x, y, z, "raw_content"))

            if positions:
                with conn.cursor() as cur:
                    from psycopg2.extras import execute_values
                    execute_values(
                        cur,
                        "INSERT INTO positions (page_id, source_table, entity_name, x, y, z, context) "
                        "VALUES %s ON CONFLICT (page_id, x, y, z) DO UPDATE SET "
                        "source_table = EXCLUDED.source_table, "
                        "entity_name = EXCLUDED.entity_name, "
                        "context = EXCLUDED.context",
                        positions,
                    )
                conn.commit()
                total_positions += len(positions)
                logger.info("Extracted %d positions from %s", len(positions), table)

        logger.info("Phase 3 complete: %d total positions extracted", total_positions)

    finally:
        conn.close()


def phase_generate_tags():
    """Phase 4: Generate tags and summaries for all parsed entities."""
    logger.info("=== PHASE 4: Generating tags and summaries ===")

    conn = get_connection()
    try:
        for _, parser_module in PARSERS:
            table = parser_module.TABLE

            # Check if tags column exists
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT 1 FROM information_schema.columns "
                    "WHERE table_name = %s AND column_name = 'tags'",
                    (table,),
                )
                if not cur.fetchone():
                    continue

            with conn.cursor() as cur:
                cur.execute(f"SELECT * FROM {table}")
                rows = cur.fetchall()

            updated = 0
            for row in rows:
                record = dict(row)
                tags = generate_tags(table, record)
                summary = generate_summary(table, record)

                with conn.cursor() as cur:
                    cur.execute(
                        f"UPDATE {table} SET tags = %s, summary = %s WHERE page_id = %s",
                        (tags, summary, record["page_id"]),
                    )
                updated += 1

            conn.commit()
            logger.info("Tagged %s: %d records", table, updated)

    finally:
        conn.close()

    logger.info("Phase 4 complete")


MATERIALIZED_VIEWS = ["creature_drops", "npc_trades", "hunt_creatures", "quest_bosses"]


def phase_refresh_views():
    """Phase 5: Refresh materialized views for cross-entity relationships."""
    logger.info("=== PHASE 5: Refreshing materialized views ===")

    conn = get_connection()
    try:
        with conn.cursor() as cur:
            for view in MATERIALIZED_VIEWS:
                try:
                    cur.execute(f"REFRESH MATERIALIZED VIEW {view}")
                    logger.info("Refreshed view: %s", view)
                except Exception as e:
                    logger.warning("Could not refresh %s: %s", view, e)
                    conn.rollback()
        conn.commit()
    finally:
        conn.close()

    logger.info("Phase 5 complete")


def phase_build_embeddings():
    """Phase 6: Build semantic search index with LlamaIndex (optional)."""
    logger.info("=== PHASE 6: Building semantic embeddings ===")
    try:
        from src.indexer import build_index
        from src.config import DATABASE_URL
        build_index(DATABASE_URL)
        logger.info("Semantic index built successfully")
    except ImportError:
        logger.info("LlamaIndex not installed, skipping semantic indexing. "
                     "Install with: pip install llama-index llama-index-vector-stores-postgres "
                     "llama-index-embeddings-huggingface sentence-transformers")
    except Exception as e:
        logger.warning("Could not build semantic index: %s", e)

    logger.info("Phase 6 complete")


def main():
    logger.info("Starting TibiaWiki Downloader")

    # Phase 0: Run migrations
    logger.info("=== PHASE 0: Running migrations ===")
    run_migrations()

    # Phase 1: Download
    client = WikiClient()
    phase_download(client)

    # Phase 2: Parse and import
    phase_parse_and_import()

    # Phase 3: Extract positions from parsed content
    phase_extract_positions()

    # Phase 4: Generate tags and summaries
    phase_generate_tags()

    # Phase 5: Refresh materialized views (for cross-entity queries)
    phase_refresh_views()

    # Phase 6: Build semantic embeddings (optional)
    phase_build_embeddings()

    # Summary
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT count(*) as cnt FROM raw_pages")
            total_pages = cur.fetchone()["cnt"]
            cur.execute("SELECT count(*) as cnt FROM raw_pages WHERE NOT is_redirect")
            non_redirect = cur.fetchone()["cnt"]
            logger.info("=== SUMMARY ===")
            logger.info("Total pages: %d (%d non-redirect)", total_pages, non_redirect)

            for _, parser_module in PARSERS:
                table = parser_module.TABLE
                cur.execute(f"SELECT count(*) as cnt FROM {table}")
                count = cur.fetchone()["cnt"]
                logger.info("  %s: %d records", table, count)

            cur.execute("SELECT count(*) as cnt FROM positions")
            pos_count = cur.fetchone()["cnt"]
            logger.info("  positions: %d records", pos_count)
    finally:
        conn.close()

    logger.info("Done!")


if __name__ == "__main__":
    main()
