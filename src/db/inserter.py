import logging

from psycopg2.extras import execute_values

logger = logging.getLogger(__name__)


def upsert_raw_pages(conn, pages):
    """Batch upsert pages into raw_pages table."""
    if not pages:
        return

    sql = """
        INSERT INTO raw_pages (page_id, title, namespace, content, is_redirect)
        VALUES %s
        ON CONFLICT (page_id) DO UPDATE SET
            title = EXCLUDED.title,
            content = EXCLUDED.content,
            is_redirect = EXCLUDED.is_redirect,
            downloaded_at = NOW()
    """

    values = [
        (p["page_id"], p["title"], p.get("namespace", 0), p["content"], p["is_redirect"])
        for p in pages
    ]

    with conn.cursor() as cur:
        execute_values(cur, sql, values)
    conn.commit()


def upsert_parsed_records(conn, table_name, records, columns):
    """Batch upsert parsed records into a typed table.

    Args:
        conn: Database connection
        table_name: Target table name
        records: List of dicts with parsed data
        columns: List of column names (first must be page_id)
    """
    if not records:
        return

    cols_str = ", ".join(columns)
    update_cols = [c for c in columns if c != "page_id"]
    update_str = ", ".join(f"{c} = EXCLUDED.{c}" for c in update_cols)

    sql = f"""
        INSERT INTO {table_name} ({cols_str})
        VALUES %s
        ON CONFLICT (page_id) DO UPDATE SET {update_str}
    """

    values = [
        tuple(record.get(col) for col in columns)
        for record in records
    ]

    with conn.cursor() as cur:
        execute_values(cur, sql, values)
    conn.commit()
    logger.info("Upserted %d records into %s", len(records), table_name)
