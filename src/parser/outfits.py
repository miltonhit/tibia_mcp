from src.parser.wikitext import extract_infobox, parse_boolean, clean_wikilinks

TEMPLATE = "Infobox_Outfit"
TABLE = "outfits"

COLUMNS = [
    "page_id", "name", "outfit_type", "premium", "outfit_access",
    "addon1_access", "addon2_access", "value", "achievement",
    "implemented", "notes",
]

FIELD_MAP = {
    "name": "name",
    "type": "outfit_type",
    "premium": "premium",
    "access": "outfit_access",
    "addon1": "addon1_access",
    "addon2": "addon2_access",
    "value": "value",
    "achievement": "achievement",
    "implemented": "implemented",
    "notas": "notes",
    "notes": "notes",
}

BOOL_FIELDS = {"premium"}
CLEAN_FIELDS = {"outfit_access", "addon1_access", "addon2_access", "notes"}


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
