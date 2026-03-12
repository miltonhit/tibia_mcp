from src.parser.wikitext import extract_infobox, parse_boolean, parse_int, clean_wikilinks

TEMPLATE = "Infobox Familiar"
TABLE = "familiars"

COLUMNS = [
    "page_id", "name", "hp", "summon_cost", "vocation", "illusionable",
    "pushable", "push_objects", "behavior", "obtain",
    "implemented", "notes", "history",
]

FIELD_MAP = {
    "name": "name",
    "hp": "hp",
    "summon": "summon_cost",
    "vocation": "vocation",
    "illusionable": "illusionable",
    "pushable": "pushable",
    "pushobjects": "push_objects",
    "behavior": "behavior",
    "obtain": "obtain",
    "implemented": "implemented",
    "notas": "notes",
    "notes": "notes",
    "history": "history",
}

BOOL_FIELDS = {"illusionable", "pushable", "push_objects"}
INT_FIELDS = {"hp", "summon_cost"}
CLEAN_FIELDS = {"behavior", "obtain", "notes", "history"}


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
