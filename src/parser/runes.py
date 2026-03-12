from src.parser.wikitext import extract_infobox, parse_boolean, parse_int, parse_float, clean_wikilinks

TEMPLATE = "Infobox_Runas"
TABLE = "runes"

COLUMNS = [
    "page_id", "name", "subclass", "damage_type", "words", "make_mana",
    "weight", "ml_required", "level_required", "soul", "make_qty",
    "make_voc", "premium", "make_level", "dropped_by", "dropped_raid_by",
    "learn_from", "buy_from", "learn_cost", "npc_price", "store_value",
    "effect", "history", "implemented", "notes",
]

FIELD_MAP = {
    "name": "name",
    "subclass": "subclass",
    "damagetype": "damage_type",
    "words": "words",
    "makemana": "make_mana",
    "weight": "weight",
    "mlrequired": "ml_required",
    "levelrequired": "level_required",
    "soul": "soul",
    "makeqty": "make_qty",
    "makevoc": "make_voc",
    "premium": "premium",
    "makelvl": "make_level",
    "droppedby": "dropped_by",
    "droppedraidby": "dropped_raid_by",
    "learnfrom": "learn_from",
    "buyfrom": "buy_from",
    "learncost": "learn_cost",
    "npcprice": "npc_price",
    "storevalue": "store_value",
    "effect": "effect",
    "history": "history",
    "implemented": "implemented",
    "notas": "notes",
    "notes": "notes",
}

BOOL_FIELDS = {"premium"}
INT_FIELDS = {"make_mana", "ml_required", "level_required", "soul", "make_qty",
              "make_level", "npc_price", "store_value"}
FLOAT_FIELDS = {"weight"}
CLEAN_FIELDS = {"dropped_by", "dropped_raid_by", "learn_from", "buy_from",
                "make_voc", "effect", "history", "notes"}


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
        elif col in FLOAT_FIELDS:
            record[col] = parse_float(value)
        elif col in CLEAN_FIELDS:
            record[col] = clean_wikilinks(value) if value else None
        else:
            record[col] = value.strip() if value else None

    if "name" not in record or not record["name"]:
        return None

    return record
