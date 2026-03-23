"""Semantic indexing with LlamaIndex + pgvector.

Builds vector embeddings from entity data for semantic search.
Uses local sentence-transformers model (no API key required).

This module is OPTIONAL - if llama-index or sentence-transformers
are not installed, the system works normally with keyword/FTS search.
"""

import logging
import os

logger = logging.getLogger(__name__)

# Entity tables and their text-building fields
ENTITY_TABLES = [
    "creatures", "items", "spells", "npcs", "quests", "achievements",
    "mounts", "hunts", "books", "buildings", "worlds", "runes",
    "world_quests", "world_changes", "familiars", "tasks", "updates", "fansites",
]

EMBED_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
EMBED_DIM = 384


def build_searchable_text(table, row):
    """Build a rich text representation of an entity for embedding."""
    name = row.get("name", "")

    if table == "creatures":
        parts = [f"{name} is a creature"]
        if row.get("creature_class"):
            parts[0] = f"{name} is a {row['creature_class']} creature"
        if row.get("hp"):
            parts.append(f"with {row['hp']} HP")
        if row.get("exp"):
            parts.append(f"and {row['exp']} experience")
        weaknesses = []
        for elem in ("fire", "ice", "earth", "energy", "holy", "death", "physical"):
            mod = row.get(f"{elem}_mod")
            if mod and mod > 100:
                weaknesses.append(elem)
        if weaknesses:
            parts.append(f"Weak to: {', '.join(weaknesses)}")
        immunities = []
        for elem in ("fire", "ice", "earth", "energy", "holy", "death", "physical"):
            mod = row.get(f"{elem}_mod")
            if mod is not None and mod == 0:
                immunities.append(elem)
        if immunities:
            parts.append(f"Immune to: {', '.join(immunities)}")
        for loot_type in ("loot_common", "loot_uncommon", "loot_rare", "loot_very_rare"):
            if row.get(loot_type):
                parts.append(f"Loot ({loot_type.replace('loot_', '')}): {row[loot_type][:200]}")
        if row.get("behavior"):
            parts.append(f"Behavior: {row['behavior']}")
        if row.get("notes"):
            parts.append(row["notes"][:300])
        return ". ".join(parts)

    elif table == "items":
        parts = [name]
        if row.get("item_class"):
            parts.append(f"Type: {row['item_class']}")
        if row.get("body_position"):
            parts.append(f"Slot: {row['body_position']}")
        if row.get("armor"):
            parts.append(f"Armor: {row['armor']}")
        if row.get("attack"):
            parts.append(f"Attack: {row['attack']}")
        if row.get("defense"):
            parts.append(f"Defense: {row['defense']}")
        if row.get("level_required"):
            parts.append(f"Level required: {row['level_required']}")
        if row.get("resist"):
            parts.append(f"Resistance: {row['resist']}")
        if row.get("skillboost"):
            parts.append(f"Skill boost: {row['skillboost']}")
        if row.get("element_attack"):
            parts.append(f"Element: {row['element_attack']}")
        if row.get("damage") and row.get("damage_type"):
            parts.append(f"Damage: {row['damage']} {row['damage_type']}")
        if row.get("augments"):
            parts.append(f"Augments: {row['augments']}")
        if row.get("npc_value"):
            parts.append(f"NPC value: {row['npc_value']} gold")
        if row.get("notes"):
            parts.append(row["notes"][:300])
        return ". ".join(parts)

    elif table == "spells":
        parts = [f"{name} spell"]
        if row.get("words"):
            parts.append(f"Words: {row['words']}")
        if row.get("subclass"):
            parts.append(f"Type: {row['subclass']}")
        if row.get("mana"):
            parts.append(f"Mana: {row['mana']}")
        if row.get("vocations"):
            parts.append(f"For: {row['vocations']}")
        if row.get("notes"):
            parts.append(row["notes"][:200])
        return ". ".join(parts)

    elif table == "npcs":
        parts = [f"{name} NPC"]
        if row.get("job"):
            parts.append(f"Job: {row['job']}")
        if row.get("city"):
            parts.append(f"City: {row['city']}")
        if row.get("buys"):
            parts.append(f"Buys: {row['buys'][:200]}")
        if row.get("sells"):
            parts.append(f"Sells: {row['sells'][:200]}")
        if row.get("notes"):
            parts.append(row["notes"][:200])
        return ". ".join(parts)

    elif table == "quests":
        parts = [f"{name} quest"]
        if row.get("level"):
            parts.append(f"Level: {row['level']}")
        if row.get("reward"):
            parts.append(f"Reward: {row['reward']}")
        if row.get("legend"):
            parts.append(row["legend"][:300])
        if row.get("notes"):
            parts.append(row["notes"][:200])
        return ". ".join(parts)

    elif table == "books":
        parts = [f"Book: {name}"]
        if row.get("blurb"):
            parts.append(row["blurb"])
        if row.get("text"):
            parts.append(row["text"][:500])
        return ". ".join(parts)

    elif table == "hunts":
        parts = [f"Hunting place: {name}"]
        if row.get("city"):
            parts.append(f"City: {row['city']}")
        if row.get("level"):
            parts.append(f"Level: {row['level']}")
        if row.get("vocation"):
            parts.append(f"Vocation: {row['vocation']}")
        if row.get("info"):
            parts.append(row["info"][:300])
        if row.get("notes"):
            parts.append(row["notes"][:200])
        return ". ".join(parts)

    # Generic fallback
    parts = [f"{name}"]
    if row.get("notes"):
        parts.append(row["notes"][:300])
    if row.get("description"):
        parts.append(row["description"][:300])
    return ". ".join(parts)


def build_index(database_url=None):
    """Build or update the vector index from all entity tables.

    Requires: llama-index, llama-index-vector-stores-postgres,
              llama-index-embeddings-huggingface, pgvector
    """
    try:
        from llama_index.core import Document, VectorStoreIndex, StorageContext
        from llama_index.vector_stores.postgres import PGVectorStore
        from llama_index.embeddings.huggingface import HuggingFaceEmbedding
    except ImportError:
        logger.warning(
            "LlamaIndex not installed. Install with: "
            "pip install llama-index llama-index-vector-stores-postgres "
            "llama-index-embeddings-huggingface sentence-transformers"
        )
        raise

    import psycopg2
    from psycopg2.extras import RealDictCursor
    from urllib.parse import urlparse

    if database_url is None:
        database_url = os.getenv(
            "DATABASE_URL",
            "postgresql://tibiawiki:tibiawiki@localhost:5432/tibiawiki",
        )

    parsed = urlparse(database_url)

    embed_model = HuggingFaceEmbedding(model_name=EMBED_MODEL_NAME)

    vector_store = PGVectorStore.from_params(
        host=parsed.hostname or "localhost",
        port=str(parsed.port or 5432),
        database=parsed.path.lstrip("/") if parsed.path else "tibiawiki",
        user=parsed.username or "tibiawiki",
        password=parsed.password or "tibiawiki",
        table_name="entity_embeddings",
        embed_dim=EMBED_DIM,
    )

    # Fetch all entities and convert to Documents
    conn = psycopg2.connect(database_url, cursor_factory=RealDictCursor)
    documents = []

    try:
        with conn.cursor() as cur:
            for table in ENTITY_TABLES:
                try:
                    cur.execute(f"SELECT * FROM {table}")
                    rows = cur.fetchall()
                except Exception:
                    conn.rollback()
                    logger.warning("Could not read table %s, skipping", table)
                    continue

                for row in rows:
                    row_dict = dict(row)
                    text = build_searchable_text(table, row_dict)
                    if not text or len(text.strip()) < 10:
                        continue

                    doc = Document(
                        text=text,
                        metadata={
                            "source_table": table,
                            "entity_name": row_dict.get("name", ""),
                            "page_id": row_dict.get("page_id", 0),
                        },
                    )
                    documents.append(doc)

                logger.info("Prepared %d documents from %s", len(rows), table)
    finally:
        conn.close()

    logger.info("Building vector index from %d documents...", len(documents))

    storage_context = StorageContext.from_defaults(vector_store=vector_store)
    index = VectorStoreIndex.from_documents(
        documents,
        storage_context=storage_context,
        embed_model=embed_model,
        show_progress=True,
    )

    logger.info("Vector index built successfully with %d documents", len(documents))
    return index


def query_index(question, database_url=None, entity_type="", limit=5):
    """Query the vector index with a natural language question.

    Returns list of dicts with entity_name, source_table, score, text.
    """
    try:
        from llama_index.core import VectorStoreIndex
        from llama_index.vector_stores.postgres import PGVectorStore
        from llama_index.embeddings.huggingface import HuggingFaceEmbedding
    except ImportError:
        return None  # Graceful degradation

    from urllib.parse import urlparse

    if database_url is None:
        database_url = os.getenv(
            "DATABASE_URL",
            "postgresql://tibiawiki:tibiawiki@localhost:5432/tibiawiki",
        )

    parsed = urlparse(database_url)

    embed_model = HuggingFaceEmbedding(model_name=EMBED_MODEL_NAME)

    vector_store = PGVectorStore.from_params(
        host=parsed.hostname or "localhost",
        port=str(parsed.port or 5432),
        database=parsed.path.lstrip("/") if parsed.path else "tibiawiki",
        user=parsed.username or "tibiawiki",
        password=parsed.password or "tibiawiki",
        table_name="entity_embeddings",
        embed_dim=EMBED_DIM,
    )

    index = VectorStoreIndex.from_vector_store(
        vector_store, embed_model=embed_model
    )

    retriever = index.as_retriever(similarity_top_k=limit)

    nodes = retriever.retrieve(question)

    results = []
    for node in nodes:
        meta = node.metadata or {}
        if entity_type and meta.get("source_table") != entity_type:
            continue
        results.append({
            "entity_name": meta.get("entity_name", ""),
            "source_table": meta.get("source_table", ""),
            "page_id": meta.get("page_id", 0),
            "score": round(node.score, 4) if node.score else 0,
            "text_snippet": node.text[:200] if node.text else "",
        })

    return results
