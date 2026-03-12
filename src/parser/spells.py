from src.parser.wikitext import extract_infobox, parse_boolean, parse_int, clean_wikilinks

TEMPLATE = "Infobox_Spell"
TABLE = "spells"

COLUMNS = [
    "page_id", "name", "subclass", "cooldown_group", "cooldown_own",
    "words", "premium", "mana", "mag_level", "exp_level", "vocations",
    "learn_druid", "learn_paladin", "learn_sorcerer", "learn_knight",
    "spell_cost", "base_power", "scale_with", "spell_range",
    "magic_type", "aim_at_target", "effect", "implemented", "notes",
]

FIELD_MAP = {
    "name": "name",
    "subclass": "subclass",
    "cooldowngroup": "cooldown_group",
    "cooldownown": "cooldown_own",
    "words": "words",
    "premium": "premium",
    "mana": "mana",
    "maglvl": "mag_level",
    "explvl": "exp_level",
    "voc": "vocations",
    "learndruid": "learn_druid",
    "learnpaladin": "learn_paladin",
    "learnsorcerer": "learn_sorcerer",
    "learnknight": "learn_knight",
    "spellcost": "spell_cost",
    "basepower": "base_power",
    "scalewith": "scale_with",
    "range": "spell_range",
    "magictype": "magic_type",
    "aimattarget": "aim_at_target",
    "effect": "effect",
    "implemented": "implemented",
    "notas": "notes",
    "notes": "notes",
}

BOOL_FIELDS = {"premium"}
INT_FIELDS = {"cooldown_group", "cooldown_own", "mana", "mag_level", "exp_level", "base_power"}
CLEAN_FIELDS = {"effect", "notes"}


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
