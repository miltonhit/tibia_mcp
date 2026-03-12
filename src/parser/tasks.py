from src.parser.wikitext import extract_infobox, parse_boolean, parse_int, clean_wikilinks

TEMPLATE = "Infobox_Tasks"
TABLE = "tasks"

COLUMNS = [
    "page_id", "name", "premium", "reward", "location", "time",
    "level", "dangers", "implemented", "notes",
]

FIELD_MAP = {
    "name": "name",
    "premium": "premium",
    "reward": "reward",
    "location": "location",
    "time": "time",
    "lvl": "level",
    "dangers": "dangers",
    "implemented": "implemented",
    "notas": "notes",
    "notes": "notes",
}

BOOL_FIELDS = {"premium"}
INT_FIELDS = {"level"}
CLEAN_FIELDS = {"reward", "location", "dangers", "notes"}


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
        elif col in INT_FIELDS:
            record[col] = parse_int(value)
        elif col in CLEAN_FIELDS:
            record[col] = clean_wikilinks(value) if value else None
        else:
            record[col] = value.strip() if value else None

    if "name" not in record or not record["name"]:
        return None

    return record
