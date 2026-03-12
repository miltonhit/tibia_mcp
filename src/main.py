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
from src.parser import creatures, items, spells, npcs, quests, achievements, mounts, outfits, imbuements, hunts

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


MATERIALIZED_VIEWS = ["creature_drops", "npc_trades", "hunt_creatures", "quest_bosses"]


def phase_refresh_views():
    """Phase 4: Refresh materialized views for cross-entity relationships."""
    logger.info("=== PHASE 4: Refreshing materialized views ===")

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

    logger.info("Phase 4 complete")


def main():
    logger.info("Starting TibiaWiki Downloader")

    # Phase 0: Run migrations
    logger.info("=== PHASE 0: Running migrations ===")
    run_migrations()

    # Phase 1: Download
    client = WikiClient()
    phase_download(client)

    # Phase 2+3: Parse and import
    phase_parse_and_import()

    # Phase 4: Refresh materialized views (for cross-entity queries)
    phase_refresh_views()

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
    finally:
        conn.close()

    logger.info("Done!")


if __name__ == "__main__":
    main()
