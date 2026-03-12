from src.parser.wikitext import extract_infobox, parse_boolean, parse_int, clean_wikilinks

TEMPLATE = "Infobox_Hunts"
TABLE = "hunts"

COLUMNS = [
    "page_id", "name", "city", "location", "map_coords", "premium",
    "difficulty", "vocation", "level", "loot_rating", "exp_rating",
    "rare_items", "implemented", "info", "notes",
]

FIELD_MAP = {
    "name": "name",
    "city": "city",
    "location": "location",
    "mapcoords": "map_coords",
    "premium": "premium",
    "difficulty": "difficulty",
    "voc": "vocation",
    "lvl": "level",
    "lootrating": "loot_rating",
    "exprating": "exp_rating",
    "rareitems": "rare_items",
    "implemented": "implemented",
    "info": "info",
    "notas": "notes",
    "notes": "notes",
}

BOOL_FIELDS = {"premium"}
INT_FIELDS = {"difficulty", "level", "loot_rating", "exp_rating"}
CLEAN_FIELDS = {"rare_items", "info", "notes"}


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
