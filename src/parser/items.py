from src.parser.wikitext import extract_infobox, parse_boolean, parse_int, parse_float, clean_wikilinks

TEMPLATE = "Infobox_Item"
TABLE = "items"

COLUMNS = [
    "page_id", "name", "voc_required", "item_class", "primary_type",
    "secondary_type", "stackable", "imbuement_slots", "classification",
    "max_tier", "armor", "attack", "attack_mod", "hit_percent",
    "defense", "defense_mod", "hands", "body_position", "weight",
    "value", "npc_value", "npc_value_currency",
    "dropped_by", "buy_from", "sell_to", "implemented", "notes",
]

FIELD_MAP = {
    "name": "name",
    "vocrequired": "voc_required",
    "itemclass": "item_class",
    "primarytype": "primary_type",
    "secondarytype": "secondary_type",
    "stackable": "stackable",
    "imbuementslots": "imbuement_slots",
    "classification": "classification",
    "maxtier": "max_tier",
    "armor": "armor",
    "attack": "attack",
    "attackmod": "attack_mod",
    "hitpercent": "hit_percent",
    "defense": "defense",
    "defensemod": "defense_mod",
    "hands": "hands",
    "bodyposition": "body_position",
    "weight": "weight",
    "value": "value",
    "npcvalue": "npc_value",
    "npcvaluecurrency": "npc_value_currency",
    "droppedby": "dropped_by",
    "buyfrom": "buy_from",
    "sellto": "sell_to",
    "implemented": "implemented",
    "notas": "notes",
    "notes": "notes",
}

BOOL_FIELDS = {"stackable"}
INT_FIELDS = {"imbuement_slots", "classification", "max_tier", "armor", "attack",
              "hit_percent", "defense", "npc_value"}
FLOAT_FIELDS = {"weight"}
CLEAN_FIELDS = {"dropped_by", "buy_from", "sell_to", "notes"}


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
