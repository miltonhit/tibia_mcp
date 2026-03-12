from src.parser.wikitext import extract_infobox, parse_int, clean_wikilinks

TEMPLATE = "Infobox_Imbuement"
TABLE = "imbuements"

COLUMNS = [
    "page_id", "name", "modifier", "applicable_to", "duration",
    "imbuement_class", "effect_basic", "effect_intricate", "effect_powerful",
    "item_basic", "item_basic_qty", "item_intricate", "item_intricate_qty",
    "item_powerful", "item_powerful_qty", "implemented", "notes",
]

FIELD_MAP = {
    "name": "name",
    "modifier": "modifier",
    "applicableto": "applicable_to",
    "duration": "duration",
    "class": "imbuement_class",
    "effectbasic": "effect_basic",
    "effectintricate": "effect_intricate",
    "effectpowerful": "effect_powerful",
    "itembasic": "item_basic",
    "itembasicqty": "item_basic_qty",
    "itemintricate": "item_intricate",
    "itemintricateqty": "item_intricate_qty",
    "itempowerful": "item_powerful",
    "itempowerfulqty": "item_powerful_qty",
    "implemented": "implemented",
    "notas": "notes",
    "notes": "notes",
}

INT_FIELDS = {"item_basic_qty", "item_intricate_qty", "item_powerful_qty"}
CLEAN_FIELDS = {"applicable_to", "item_basic", "item_intricate", "item_powerful", "notes"}


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
