from src.parser.wikitext import extract_infobox, parse_boolean, clean_wikilinks

TEMPLATE = "Infobox_Updates"
TABLE = "updates"

COLUMNS = [
    "page_id", "name", "update_version", "update_previous", "update_next",
    "update_season", "update_new", "update_changed", "update_fixed",
    "implemented", "notes",
]

FIELD_MAP = {
    "name": "name",
    "updateversion": "update_version",
    "updateprevious": "update_previous",
    "updatenext": "update_next",
    "updateseason": "update_season",
    "updatenew": "update_new",
    "updatechanged": "update_changed",
    "updatefixed": "update_fixed",
    "implemented": "implemented",
    "notas": "notes",
    "notes": "notes",
}

BOOL_FIELDS = {"update_season"}
CLEAN_FIELDS = {"update_new", "update_changed", "update_fixed", "notes"}


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

    # Use update_version as name fallback
    if "name" not in record or not record["name"]:
        record["name"] = record.get("update_version")
    if not record.get("name"):
        return None

    return record
