from src.parser.wikitext import extract_infobox, parse_boolean, parse_int, clean_wikilinks

TEMPLATE = "Infobox_World_Quest"
TABLE = "world_quests"

COLUMNS = [
    "page_id", "name", "quest_type", "start_date", "end_date",
    "frequency", "reward", "location", "level", "premium",
    "dangers", "mini_quests", "bosses", "legend", "implemented", "notes",
]

FIELD_MAP = {
    "name": "name",
    "type": "quest_type",
    "start": "start_date",
    "end": "end_date",
    "freq": "frequency",
    "reward": "reward",
    "location": "location",
    "lvl": "level",
    "premium": "premium",
    "dangers": "dangers",
    "mini": "mini_quests",
    "bosses": "bosses",
    "legend": "legend",
    "implemented": "implemented",
    "notas": "notes",
    "notes": "notes",
}

BOOL_FIELDS = {"premium"}
INT_FIELDS = {"level"}
CLEAN_FIELDS = {"reward", "location", "dangers", "mini_quests", "bosses", "legend", "notes"}


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
