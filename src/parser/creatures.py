from src.parser.wikitext import extract_infobox, parse_boolean, parse_int, parse_float, clean_wikilinks

TEMPLATE = "Infobox_Criatura"
TABLE = "creatures"

COLUMNS = [
    "page_id", "name", "hp", "exp", "boss", "is_boss", "boss_type",
    "boss_cooldown", "boss_timeout", "summon_cost", "convince_cost",
    "illusionable", "creature_class", "primary_type", "secondary_type",
    "pushable", "push_objects", "speed", "charm_points", "defense",
    "mitigation", "occurrence", "difficulty", "max_damage",
    "hab_physical", "hab_earth", "hab_fire", "hab_death", "hab_energy",
    "hab_holy", "hab_ice", "hab_lifedrain", "hab_manadrain", "hab_drowning",
    "hab_healing", "hab_invisible", "hab_speed", "hab_debuff", "hab_summon",
    "hab_drunk", "hab_paralyze", "hab_antitrap",
    "physical_mod", "earth_mod", "fire_mod", "death_mod", "energy_mod",
    "holy_mod", "ice_mod", "heal_mod",
    "reflects", "immunities", "ignores_fields",
    "implemented", "removed", "respawn_blocked", "behavior", "sounds",
    "location_raid",
    "loot_common", "loot_uncommon", "loot_semi_rare", "loot_rare",
    "loot_very_rare", "loot_event", "loot_raid",
    "notes", "history",
]

# Map wiki field names to our column names
FIELD_MAP = {
    "name": "name",
    "hp": "hp",
    "exp": "exp",
    "boss": "boss",
    "isboss": "is_boss",
    "bosstype": "boss_type",
    "bosscooldown": "boss_cooldown",
    "bosstimeout": "boss_timeout",
    "summon": "summon_cost",
    "convince": "convince_cost",
    "illusionable": "illusionable",
    "creatureclass": "creature_class",
    "primarytype": "primary_type",
    "secondarytype": "secondary_type",
    "pushable": "pushable",
    "pushobjects": "push_objects",
    "speed": "speed",
    "charmpoints": "charm_points",
    "defense": "defense",
    "mitigation": "mitigation",
    "occurrence": "occurrence",
    "difficulty": "difficulty",
    "maxdmg": "max_damage",
    "hab_fisico": "hab_physical",
    "hab_terra": "hab_earth",
    "hab_fogo": "hab_fire",
    "hab_morte": "hab_death",
    "hab_energia": "hab_energy",
    "hab_sagrado": "hab_holy",
    "hab_gelo": "hab_ice",
    "hab_drenavida": "hab_lifedrain",
    "hab_drenamana": "hab_manadrain",
    "hab_afogamento": "hab_drowning",
    "hab_cura": "hab_healing",
    "hab_invisibilidade": "hab_invisible",
    "hab_velocidade": "hab_speed",
    "hab_debuff": "hab_debuff",
    "hab_invocação": "hab_summon",
    "hab_invocacao": "hab_summon",
    "hab_embriaguez": "hab_drunk",
    "hab_paralisia": "hab_paralyze",
    "hab_antiarmadilha": "hab_antitrap",
    "physicalmod": "physical_mod",
    "earthmod": "earth_mod",
    "firemod": "fire_mod",
    "deathmod": "death_mod",
    "energymod": "energy_mod",
    "holymod": "holy_mod",
    "icemod": "ice_mod",
    "healmod": "heal_mod",
    "reflects": "reflects",
    "immunities": "immunities",
    "ignoresfields": "ignores_fields",
    "implemented": "implemented",
    "removed": "removed",
    "respawnblocked": "respawn_blocked",
    "behavior": "behavior",
    "sounds": "sounds",
    "localizacaoraid": "location_raid",
    "lootcomum": "loot_common",
    "lootincomum": "loot_uncommon",
    "lootsemiraro": "loot_semi_rare",
    "lootraro": "loot_rare",
    "lootmuitotraro": "loot_very_rare",
    "lootevento": "loot_event",
    "lootraid": "loot_raid",
    "notas": "notes",
    "historico": "history",
    "notes": "notes",
    "history": "history",
}

BOOL_FIELDS = {"is_boss", "illusionable", "pushable", "push_objects", "respawn_blocked"}
INT_FIELDS = {"hp", "exp", "summon_cost", "convince_cost", "speed", "charm_points",
              "defense", "max_damage", "physical_mod", "earth_mod", "fire_mod",
              "death_mod", "energy_mod", "holy_mod", "ice_mod", "heal_mod"}
FLOAT_FIELDS = {"mitigation"}
CLEAN_FIELDS = {"loot_common", "loot_uncommon", "loot_semi_rare", "loot_rare",
                "loot_very_rare", "loot_event", "loot_raid", "immunities",
                "reflects", "ignores_fields", "sounds", "notes", "history"}


def parse(page_id, content):
    """Parse creature data from wikitext.

    Returns:
        dict with creature fields or None
    """
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

    # Ensure name is set
    if "name" not in record or not record["name"]:
        return None

    return record
