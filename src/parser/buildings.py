from src.parser.wikitext import extract_infobox, parse_int, clean_wikilinks

TEMPLATE = "Infobox_Building"
TABLE = "buildings"

COLUMNS = [
    "page_id", "name", "building_type", "location", "street", "size",
    "beds", "rent", "payrent", "openwindows", "floors", "rooms",
    "furnishings", "implemented", "notes",
]

FIELD_MAP = {
    "name": "name",
    "type": "building_type",
    "location": "location",
    "street": "street",
    "size": "size",
    "beds": "beds",
    "rent": "rent",
    "payrent": "payrent",
    "openwindows": "openwindows",
    "floors": "floors",
    "rooms": "rooms",
    "furnishings": "furnishings",
    "implemented": "implemented",
    "notas": "notes",
    "notes": "notes",
}

INT_FIELDS = {"size", "beds", "rent", "openwindows", "floors", "rooms"}
CLEAN_FIELDS = {"location", "furnishings", "notes"}


def parse(page_id, content):
    raw = extract_infobox(content, TEMPLATE)
    if not raw:
        return None

    record = {"page_id": page_id}

    for wiki_key, col in FIELD_MAP.items():
        value = raw.get(wiki_key)
        if value is None:
            continue

        if col in INT_FIELDS:
            record[col] = parse_int(value)
        elif col in CLEAN_FIELDS:
            record[col] = clean_wikilinks(value) if value else None
        else:
            record[col] = value.strip() if value else None

    if "name" not in record or not record["name"]:
        return None

    return record
