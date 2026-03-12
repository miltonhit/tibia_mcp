import os
import re
import logging

from src.config import MIGRATIONS_DIR
from src.db.connection import get_connection

logger = logging.getLogger(__name__)


def run_migrations():
    """Execute all pending SQL migrations in order."""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            # Find all migration files sorted by version number
            migration_files = sorted(
                f for f in os.listdir(MIGRATIONS_DIR)
                if re.match(r"^\d{3}_.*\.sql$", f)
            )

            if not migration_files:
                logger.info("No migration files found")
                return

            # First migration (001) creates schema_migrations table itself
            # Execute it first unconditionally
            first_file = migration_files[0]
            first_path = os.path.join(MIGRATIONS_DIR, first_file)
            with open(first_path) as f:
                sql = f.read()
            cur.execute(sql)
            conn.commit()

            # Record first migration if not already recorded
            cur.execute(
                "INSERT INTO schema_migrations (version, filename) VALUES (%s, %s) "
                "ON CONFLICT (version) DO NOTHING",
                (1, first_file),
            )
            conn.commit()

            # Get already-applied migrations
            cur.execute("SELECT version FROM schema_migrations ORDER BY version")
            applied = {row["version"] for row in cur.fetchall()}

            # Apply remaining migrations
            for filename in migration_files[1:]:
                version = int(filename.split("_")[0])
                if version in applied:
                    continue

                filepath = os.path.join(MIGRATIONS_DIR, filename)
                logger.info("Applying migration %s", filename)

                with open(filepath) as f:
                    sql = f.read()

                cur.execute(sql)
                cur.execute(
                    "INSERT INTO schema_migrations (version, filename) VALUES (%s, %s)",
                    (version, filename),
                )
                conn.commit()
                logger.info("Applied migration %s", filename)

        logger.info("All migrations applied successfully")
    finally:
        conn.close()
