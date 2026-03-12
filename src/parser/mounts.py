from src.parser.wikitext import extract_infobox, parse_boolean, parse_int, clean_wikilinks

TEMPLATE = "Infobox_Mount"
TABLE = "mounts"

COLUMNS = [
    "page_id", "name", "speed", "premium", "implemented",
    "arena_mount", "champ_mount", "color_mount", "event_mount",
    "offer_mount", "quest_mount", "raid_mount", "rent_mount",
    "store_mount", "tame_mount", "wchange_mount",
    "attrib", "method", "notes",
]

FIELD_MAP = {
    "name": "name",
    "speed": "speed",
    "premium": "premium",
    "implemented": "implemented",
    "arenamount": "arena_mount",
    "champmount": "champ_mount",
    "colormount": "color_mount",
    "eventmount": "event_mount",
    "offermount": "offer_mount",
    "questmount": "quest_mount",
    "raidmount": "raid_mount",
    "rentmount": "rent_mount",
    "storemount": "store_mount",
    "tamemount": "tame_mount",
    "wchangemount": "wchange_mount",
    "attrib": "attrib",
    "method": "method",
    "notas": "notes",
    "notes": "notes",
}

BOOL_FIELDS = {"premium", "arena_mount", "champ_mount", "color_mount", "event_mount",
               "offer_mount", "quest_mount", "raid_mount", "rent_mount",
               "store_mount", "tame_mount", "wchange_mount"}
INT_FIELDS = {"speed"}
CLEAN_FIELDS = {"attrib", "method", "notes"}


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
