from src.parser.wikitext import extract_infobox, parse_boolean, clean_wikilinks

TEMPLATE = "Infobox_World"
TABLE = "worlds"

COLUMNS = [
    "page_id", "name", "world_type", "online_since", "free_since",
    "offline", "location", "transfer", "battleye", "implemented", "notes",
]

FIELD_MAP = {
    "name": "name",
    "type": "world_type",
    "online": "online_since",
    "freesince": "free_since",
    "offline": "offline",
    "location": "location",
    "transfer": "transfer",
    "battleye": "battleye",
    "implemented": "implemented",
    "notas": "notes",
    "notes": "notes",
}

BOOL_FIELDS = {"transfer"}
CLEAN_FIELDS = {"notes"}


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
