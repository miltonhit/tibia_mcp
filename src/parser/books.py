from src.parser.wikitext import extract_infobox, parse_boolean, clean_wikilinks

TEMPLATE = "Infobox_Book"
TABLE = "books"

COLUMNS = [
    "page_id", "name", "title", "flavortext", "location", "author",
    "blurb", "book_type", "translated", "prev_book", "next_book",
    "related_pages", "text", "implemented", "notes",
]

FIELD_MAP = {
    "name": "name",
    "title": "title",
    "flavortext": "flavortext",
    "location": "location",
    "author": "author",
    "blurb": "blurb",
    "type": "book_type",
    "traduzido": "translated",
    "prevbook": "prev_book",
    "nextbook": "next_book",
    "relatedpages": "related_pages",
    "text": "text",
    "implemented": "implemented",
    "notas": "notes",
    "notes": "notes",
}

BOOL_FIELDS = {"translated"}
CLEAN_FIELDS = {"location", "blurb", "related_pages", "notes"}


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

    # Use title as name fallback
    if "name" not in record or not record["name"]:
        record["name"] = record.get("title")
    if not record.get("name"):
        return None

    return record
