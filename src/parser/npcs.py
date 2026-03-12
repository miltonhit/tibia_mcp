from src.parser.wikitext import extract_infobox, parse_boolean, clean_wikilinks

TEMPLATE = "Infobox_NPC"
TABLE = "npcs"

COLUMNS = [
    "page_id", "name", "job", "job2", "npc_class", "npc_sprite",
    "city", "subarea", "location", "implemented", "buysell",
    "buys", "sells", "notes",
]

FIELD_MAP = {
    "name": "name",
    "job": "job",
    "job2": "job2",
    "npcclass": "npc_class",
    "npcsprite": "npc_sprite",
    "city": "city",
    "subarea": "subarea",
    "location": "location",
    "implemented": "implemented",
    "buysell": "buysell",
    "buys": "buys",
    "sells": "sells",
    "notas": "notes",
    "notes": "notes",
}

BOOL_FIELDS = {"buysell"}
CLEAN_FIELDS = {"buys", "sells", "notes", "location"}


def parse(page_id, content):
    raw = extract_infobox(content, TEMPLATE)
    if not raw:
        return None

    record = {"page_id": page_id}

    for wiki_key, col in FIELD_MAP.items():
        value = raw.get(wiki_key)
        if value is None:
            continue

        if col in BOOL_FIELDS:
            record[col] = parse_boolean(value)
        elif col in CLEAN_FIELDS:
            record[col] = clean_wikilinks(value) if value else None
        else:
            record[col] = value.strip() if value else None

    if "name" not in record or not record["name"]:
        return None

    return record
