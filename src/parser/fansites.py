from src.parser.wikitext import extract_infobox, clean_wikilinks

TEMPLATE = "Infobox_Fansite"
TABLE = "fansites"

COLUMNS = [
    "page_id", "name", "fansite_type", "status", "language",
    "content", "contact", "website", "implemented", "notes",
]

FIELD_MAP = {
    "name": "name",
    "type": "fansite_type",
    "status": "status",
    "language": "language",
    "content": "content",
    "contact": "contact",
    "website": "website",
    "implemented": "implemented",
    "notas": "notes",
    "notes": "notes",
}

CLEAN_FIELDS = {"content", "notes"}


def parse(page_id, content):
    raw = extract_infobox(content, TEMPLATE)
    if not raw:
        return None

    record = {"page_id": page_id}

    for wiki_key, col in FIELD_MAP.items():
        value = raw.get(wiki_key)
        if value is None:
            continue

        if col in CLEAN_FIELDS:
            record[col] = clean_wikilinks(value) if value else None
        else:
            record[col] = value.strip() if value else None

    if "name" not in record or not record["name"]:
        return None

    return record
