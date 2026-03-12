import psycopg2
from psycopg2.extras import RealDictCursor

from src.config import DATABASE_URL


def get_connection():
    """Create a new database connection."""
    return psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)
