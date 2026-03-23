"""Algorithmic tag and summary generation for entity tables.

Generates searchable tags and compact one-line summaries from parsed fields,
enabling tag-based filtering and compact search results for AI agents.
"""

import logging

logger = logging.getLogger(__name__)


def generate_tags(table, record):
    """Generate a list of descriptive tags from parsed entity fields."""
    tags = []

    if table == "creatures":
        if record.get("is_boss"):
            tags.append("boss")
        hp = record.get("hp")
        exp = record.get("exp")
        if hp and hp > 10000:
            tags.append("high_hp")
        elif hp and hp < 100:
            tags.append("low_hp")
        if exp and exp > 5000:
            tags.append("high_exp")
        if record.get("charm_points") and record["charm_points"] >= 50:
            tags.append("high_charm")
        for elem in ("fire", "ice", "earth", "energy", "holy", "death", "physical"):
            mod = record.get(f"{elem}_mod")
            if mod is not None:
                if mod > 100:
                    tags.append(f"weak_to_{elem}")
                elif mod == 0:
                    tags.append(f"immune_to_{elem}")
        if record.get("illusionable"):
            tags.append("illusionable")
        if record.get("convinceable"):
            tags.append("convinceable")
        if record.get("pushable"):
            tags.append("pushable")
        if record.get("loot_very_rare"):
            tags.append("has_rare_loot")
        if record.get("creature_class"):
            tags.append(record["creature_class"].lower().replace(" ", "_"))
        if record.get("primary_type"):
            tags.append(record["primary_type"].lower().replace(" ", "_"))

    elif table == "items":
        if record.get("classification") and record["classification"] >= 3:
            tags.append("high_tier")
        if record.get("imbuement_slots") and record["imbuement_slots"] > 0:
            tags.append("imbueable")
        if record.get("armor"):
            tags.append("equipment")
        if record.get("attack"):
            tags.append("weapon")
        if record.get("defense") and not record.get("attack"):
            tags.append("shield")
        if record.get("body_position"):
            tags.append(record["body_position"].lower().replace(" ", "_"))
        if record.get("npc_value") and record["npc_value"] > 10000:
            tags.append("valuable")
        if record.get("item_class"):
            tags.append(record["item_class"].lower().replace(" ", "_"))
        if record.get("level_required") and record["level_required"] >= 200:
            tags.append("high_level_req")
        if record.get("enchantable"):
            tags.append("enchantable")
        if record.get("resist"):
            tags.append("has_resistance")
        if record.get("skillboost"):
            tags.append("has_skillboost")
        if record.get("augments"):
            tags.append("has_augments")
        if record.get("element_attack"):
            tags.append("elemental_weapon")

    elif table == "spells":
        if record.get("subclass"):
            tags.append(record["subclass"].lower().replace(" ", "_"))
        if record.get("magic_type"):
            tags.append(record["magic_type"].lower().replace(" ", "_"))
        if record.get("premium"):
            tags.append("premium")
        if record.get("vocations"):
            for v in ("knight", "sorcerer", "druid", "paladin"):
                if v in str(record["vocations"]).lower():
                    tags.append(v)

    elif table == "npcs":
        if record.get("job"):
            tags.append(record["job"].lower().replace(" ", "_"))
        if record.get("city"):
            tags.append(record["city"].lower().replace(" ", "_").replace("'", ""))
        if record.get("buys"):
            tags.append("buys_items")
        if record.get("sells"):
            tags.append("sells_items")

    elif table == "quests":
        if record.get("premium"):
            tags.append("premium")
        level = record.get("level") or record.get("level_req")
        if level and level >= 200:
            tags.append("high_level")
        elif level and level <= 30:
            tags.append("low_level")
        if record.get("bosses"):
            tags.append("has_bosses")

    elif table == "hunts":
        if record.get("exp_rating"):
            try:
                stars = int(record["exp_rating"])
                if stars >= 4:
                    tags.append("great_exp")
            except (ValueError, TypeError):
                pass
        if record.get("loot_rating"):
            try:
                stars = int(record["loot_rating"])
                if stars >= 4:
                    tags.append("great_loot")
            except (ValueError, TypeError):
                pass
        if record.get("vocation"):
            for v in ("knight", "sorcerer", "druid", "paladin"):
                if v in str(record["vocation"]).lower():
                    tags.append(v)
        if record.get("city"):
            tags.append(record["city"].lower().replace(" ", "_").replace("'", ""))

    elif table == "runes":
        if record.get("damage_type"):
            tags.append(record["damage_type"].lower())
        if record.get("premium"):
            tags.append("premium")
        if record.get("subclass"):
            tags.append(record["subclass"].lower().replace(" ", "_"))

    elif table == "books":
        if record.get("translated"):
            tags.append("translated")
        if record.get("book_type"):
            tags.append(record["book_type"].lower().replace(" ", "_"))

    elif table == "buildings":
        if record.get("building_type"):
            tags.append(record["building_type"].lower().replace(" ", "_"))
        if record.get("payrent"):
            tags.append(record["payrent"].lower().replace(" ", "_").replace("'", ""))
        beds = record.get("beds")
        if beds and beds >= 4:
            tags.append("large_house")

    elif table == "worlds":
        if record.get("world_type"):
            tags.append(record["world_type"].lower().replace(" ", "_"))
        if record.get("battleye"):
            tags.append(f"battleye_{record['battleye'].lower()}")
        if record.get("location"):
            tags.append(record["location"].lower().replace(" ", "_"))

    elif table == "world_quests":
        if record.get("frequency"):
            tags.append(record["frequency"].lower())
        if record.get("premium"):
            tags.append("premium")

    elif table == "world_changes":
        if record.get("frequency"):
            tags.append(record["frequency"].lower())

    elif table == "familiars":
        if record.get("vocation"):
            tags.append(record["vocation"].lower())

    elif table == "achievements":
        if record.get("grade"):
            try:
                grade = int(record["grade"])
                if grade >= 3:
                    tags.append("high_grade")
            except (ValueError, TypeError):
                pass
        if record.get("secret"):
            tags.append("secret")
        if record.get("premium"):
            tags.append("premium")

    elif table == "mounts":
        if record.get("premium"):
            tags.append("premium")
        if record.get("store_mount"):
            tags.append("store")
        if record.get("quest_mount"):
            tags.append("quest")
        if record.get("event_mount"):
            tags.append("event")
        if record.get("tame_mount"):
            tags.append("tameable")

    # Filter empty/None tags
    return [t for t in tags if t]


def generate_summary(table, record):
    """Generate a compact one-line summary from parsed entity fields."""
    name = record.get("name", "?")

    if table == "creatures":
        parts = [f"HP:{record.get('hp', '?')}", f"EXP:{record.get('exp', '?')}"]
        if record.get("creature_class"):
            parts.append(record["creature_class"])
        if record.get("is_boss"):
            parts.append("BOSS")
        if record.get("speed"):
            parts.append(f"Spd:{record['speed']}")
        return " | ".join(parts)

    elif table == "items":
        parts = []
        if record.get("item_class"):
            parts.append(record["item_class"])
        if record.get("armor"):
            parts.append(f"Arm:{record['armor']}")
        if record.get("attack"):
            parts.append(f"Atk:{record['attack']}")
        if record.get("defense"):
            parts.append(f"Def:{record['defense']}")
        if record.get("level_required"):
            parts.append(f"Lvl:{record['level_required']}")
        if record.get("npc_value"):
            parts.append(f"NPC:{record['npc_value']}gp")
        if record.get("classification"):
            parts.append(f"Tier:{record['classification']}")
        if record.get("resist"):
            parts.append(f"Res:{record['resist'][:30]}")
        if record.get("skillboost"):
            parts.append(f"Skill:{record['skillboost'][:30]}")
        return " | ".join(parts) if parts else record.get("item_class", "")

    elif table == "spells":
        parts = []
        if record.get("words"):
            parts.append(record["words"])
        if record.get("mana"):
            parts.append(f"Mana:{record['mana']}")
        if record.get("subclass"):
            parts.append(record["subclass"])
        if record.get("vocations"):
            parts.append(record["vocations"])
        return " | ".join(parts) if parts else ""

    elif table == "npcs":
        parts = []
        if record.get("job"):
            parts.append(record["job"])
        if record.get("city"):
            parts.append(record["city"])
        return " | ".join(parts) if parts else ""

    elif table == "quests":
        parts = []
        if record.get("level"):
            parts.append(f"Lvl:{record['level']}")
        if record.get("reward"):
            parts.append(f"Reward:{record['reward'][:60]}")
        if record.get("location"):
            parts.append(record["location"][:40])
        return " | ".join(parts) if parts else ""

    elif table == "hunts":
        parts = []
        if record.get("city"):
            parts.append(record["city"])
        if record.get("level"):
            parts.append(f"Lvl:{record['level']}")
        if record.get("exp_rating"):
            parts.append(f"Exp:{record['exp_rating']}*")
        if record.get("loot_rating"):
            parts.append(f"Loot:{record['loot_rating']}*")
        if record.get("vocation"):
            parts.append(record["vocation"])
        return " | ".join(parts) if parts else ""

    elif table == "runes":
        parts = []
        if record.get("damage_type"):
            parts.append(record["damage_type"])
        if record.get("words"):
            parts.append(record["words"])
        if record.get("level_required"):
            parts.append(f"Lvl:{record['level_required']}")
        if record.get("npc_price"):
            parts.append(f"{record['npc_price']}gp")
        return " | ".join(parts) if parts else ""

    elif table == "books":
        parts = []
        if record.get("author"):
            parts.append(f"by {record['author']}")
        if record.get("location"):
            parts.append(record["location"][:40])
        if record.get("blurb"):
            parts.append(record["blurb"][:60])
        return " | ".join(parts) if parts else ""

    elif table == "buildings":
        parts = []
        if record.get("building_type"):
            parts.append(record["building_type"])
        if record.get("size"):
            parts.append(f"Size:{record['size']}sqm")
        if record.get("beds"):
            parts.append(f"Beds:{record['beds']}")
        if record.get("rent"):
            parts.append(f"Rent:{record['rent']}gp")
        if record.get("payrent"):
            parts.append(record["payrent"])
        return " | ".join(parts) if parts else ""

    elif table == "worlds":
        parts = []
        if record.get("world_type"):
            parts.append(record["world_type"])
        if record.get("location"):
            parts.append(record["location"])
        if record.get("battleye"):
            parts.append(f"BE:{record['battleye']}")
        return " | ".join(parts) if parts else ""

    elif table == "achievements":
        parts = []
        if record.get("grade"):
            parts.append(f"Grade:{record['grade']}")
        if record.get("points"):
            parts.append(f"{record['points']}pts")
        if record.get("description"):
            parts.append(record["description"][:60])
        return " | ".join(parts) if parts else ""

    elif table == "mounts":
        parts = []
        if record.get("speed"):
            parts.append(f"Spd:{record['speed']}")
        if record.get("method"):
            parts.append(record["method"][:50])
        return " | ".join(parts) if parts else ""

    elif table == "familiars":
        parts = []
        if record.get("vocation"):
            parts.append(record["vocation"])
        if record.get("hp"):
            parts.append(f"HP:{record['hp']}")
        return " | ".join(parts) if parts else ""

    elif table == "world_quests":
        parts = []
        if record.get("frequency"):
            parts.append(record["frequency"])
        if record.get("level"):
            parts.append(f"Lvl:{record['level']}")
        if record.get("reward"):
            parts.append(record["reward"][:50])
        return " | ".join(parts) if parts else ""

    elif table == "world_changes":
        parts = []
        if record.get("frequency"):
            parts.append(record["frequency"])
        if record.get("reward"):
            parts.append(record["reward"][:50])
        return " | ".join(parts) if parts else ""

    elif table == "tasks":
        parts = []
        if record.get("level"):
            parts.append(f"Lvl:{record['level']}")
        if record.get("reward"):
            parts.append(record["reward"][:50])
        if record.get("location"):
            parts.append(record["location"][:30])
        return " | ".join(parts) if parts else ""

    elif table == "updates":
        parts = []
        if record.get("update_version"):
            parts.append(f"v{record['update_version']}")
        if record.get("update_season"):
            parts.append(str(record["update_season"]))
        return " | ".join(parts) if parts else ""

    elif table == "fansites":
        parts = []
        if record.get("fansite_type"):
            parts.append(record["fansite_type"])
        if record.get("language"):
            parts.append(record["language"])
        return " | ".join(parts) if parts else ""

    return ""
