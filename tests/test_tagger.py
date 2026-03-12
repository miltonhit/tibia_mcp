"""Tests for the tagger module — tag and summary generation."""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from src.tagger import generate_tags, generate_summary


# === Creature tags ===

def test_creature_tags_boss():
    record = {"name": "Orshabaal", "hp": 30000, "exp": 15000, "is_boss": True,
              "fire_mod": 0, "ice_mod": 110, "creature_class": "Demons"}
    tags = generate_tags("creatures", record)
    assert "boss" in tags
    assert "high_hp" in tags
    assert "high_exp" in tags
    assert "immune_to_fire" in tags
    assert "weak_to_ice" in tags
    assert "demons" in tags


def test_creature_tags_low_hp():
    record = {"name": "Rat", "hp": 20, "exp": 5, "pushable": True, "illusionable": True}
    tags = generate_tags("creatures", record)
    assert "low_hp" in tags
    assert "pushable" in tags
    assert "illusionable" in tags
    assert "boss" not in tags


def test_creature_tags_rare_loot():
    record = {"name": "Dragon", "hp": 1000, "exp": 700,
              "loot_very_rare": "Dragon Scale Mail", "primary_type": "Dragoes"}
    tags = generate_tags("creatures", record)
    assert "has_rare_loot" in tags
    assert "dragoes" in tags


# === Item tags ===

def test_item_tags_weapon():
    record = {"name": "Magic Longsword", "attack": 50, "classification": 4,
              "imbuement_slots": 2, "npc_value": 15000, "item_class": "Swords"}
    tags = generate_tags("items", record)
    assert "weapon" in tags
    assert "high_tier" in tags
    assert "imbueable" in tags
    assert "valuable" in tags
    assert "swords" in tags


def test_item_tags_shield():
    record = {"name": "Mastermind Shield", "defense": 37, "item_class": "Shields",
              "body_position": "Shield"}
    tags = generate_tags("items", record)
    assert "shield" in tags
    assert "shields" in tags


def test_item_tags_equipment():
    record = {"name": "Magic Plate Armor", "armor": 17, "classification": 4,
              "body_position": "Body", "imbuement_slots": 3}
    tags = generate_tags("items", record)
    assert "equipment" in tags
    assert "high_tier" in tags
    assert "imbueable" in tags
    assert "body" in tags


# === Spell tags ===

def test_spell_tags():
    record = {"name": "Exura Gran", "subclass": "Healing", "magic_type": "Instant",
              "premium": True, "vocations": "Druids and Knights"}
    tags = generate_tags("spells", record)
    assert "healing" in tags
    assert "instant" in tags
    assert "premium" in tags
    assert "druid" in tags
    assert "knight" in tags


# === NPC tags ===

def test_npc_tags():
    record = {"name": "Rashid", "job": "Trader", "city": "Ab'Dendriel",
              "buys": "Magic Plate Armor, Golden Armor", "sells": None}
    tags = generate_tags("npcs", record)
    assert "trader" in tags
    assert "abdendriel" in tags
    assert "buys_items" in tags
    assert "sells_items" not in tags


# === Hunt tags ===

def test_hunt_tags():
    record = {"name": "Roshamuul", "city": "Roshamuul", "level": 250,
              "exp_rating": "5", "loot_rating": "4",
              "vocation": "Knights and Paladins"}
    tags = generate_tags("hunts", record)
    assert "great_exp" in tags
    assert "great_loot" in tags
    assert "knight" in tags
    assert "paladin" in tags


# === Quest tags ===

def test_quest_tags():
    record = {"name": "The Annihilator", "level": 100, "premium": True,
              "bosses": "Demon, Dragon Lord"}
    tags = generate_tags("quests", record)
    assert "premium" in tags
    assert "has_bosses" in tags


def test_quest_tags_premium():
    record = {"name": "Test Quest", "level": 250, "premium": True, "bosses": None}
    tags = generate_tags("quests", record)
    assert "premium" in tags
    assert "high_level" in tags


# === Mount tags ===

def test_mount_tags():
    record = {"name": "Blazebringer", "premium": True, "event_mount": True,
              "store_mount": False, "tame_mount": False}
    tags = generate_tags("mounts", record)
    assert "premium" in tags
    assert "event" in tags
    assert "store" not in tags


# === Summary tests ===

def test_creature_summary():
    record = {"name": "Dragon", "hp": 1000, "exp": 700, "speed": 210,
              "creature_class": "Dragoes", "is_boss": False}
    summary = generate_summary("creatures", record)
    assert "HP:1000" in summary
    assert "EXP:700" in summary
    assert "Dragoes" in summary


def test_creature_summary_boss():
    record = {"name": "Orshabaal", "hp": 30000, "exp": 15000,
              "creature_class": "Demons", "is_boss": True, "speed": 400}
    summary = generate_summary("creatures", record)
    assert "BOSS" in summary
    assert "HP:30000" in summary


def test_item_summary():
    record = {"name": "Magic Plate Armor", "item_class": "Armors",
              "armor": 17, "npc_value": 6400, "classification": 4}
    summary = generate_summary("items", record)
    assert "Arm:17" in summary
    assert "NPC:6400gp" in summary
    assert "Tier:4" in summary


def test_hunt_summary():
    record = {"name": "Roshamuul", "city": "Roshamuul", "level": 250,
              "exp_rating": "5", "loot_rating": "4", "vocation": "All"}
    summary = generate_summary("hunts", record)
    assert "Roshamuul" in summary
    assert "Lvl:250" in summary
    assert "Exp:5*" in summary


def test_npc_summary():
    record = {"name": "Rashid", "job": "Trader", "city": "Various"}
    summary = generate_summary("npcs", record)
    assert "Trader" in summary
    assert "Various" in summary


def test_empty_tags():
    tags = generate_tags("creatures", {})
    assert tags == []


def test_empty_summary():
    summary = generate_summary("unknown_table", {"name": "Test"})
    assert summary == ""


if __name__ == "__main__":
    test_functions = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    passed = 0
    failed = 0
    for test_fn in test_functions:
        try:
            test_fn()
            print(f"  PASS: {test_fn.__name__}")
            passed += 1
        except Exception as e:
            print(f"  FAIL: {test_fn.__name__}: {e}")
            failed += 1

    print(f"\n{passed} passed, {failed} failed")
    sys.exit(1 if failed else 0)
