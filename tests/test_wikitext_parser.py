"""Tests for the wikitext parser and type-specific parsers."""

import os
import sys

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from src.parser.wikitext import extract_infobox, clean_wikilinks, parse_boolean, parse_int, parse_float
from src.parser import creatures, items, mounts

FIXTURES_DIR = os.path.join(os.path.dirname(__file__), "fixtures")


def read_fixture(name):
    with open(os.path.join(FIXTURES_DIR, name)) as f:
        return f.read()


# === Core parser tests ===

def test_extract_infobox_creature():
    content = read_fixture("dragon.txt")
    result = extract_infobox(content, "Infobox_Criatura")
    assert result is not None
    assert result["name"] == "Dragon"
    assert result["hp"] == "1000"
    assert result["exp"] == "700"
    assert result["speed"] == "210"
    assert result["firemod"] == "0%"
    assert result["icemod"] == "110%"
    assert "Gold Coin" in result["lootcomum"]


def test_extract_infobox_item():
    content = read_fixture("magic_plate_armor.txt")
    result = extract_infobox(content, "Infobox_Item")
    assert result is not None
    assert result["name"] == "Magic Plate Armor"
    assert result["armor"] == "17"
    assert result["weight"] == "85.00"
    assert result["npcvalue"] == "6400"
    assert result["imbuementslots"] == "3"


def test_extract_infobox_mount():
    content = read_fixture("blazebringer.txt")
    result = extract_infobox(content, "Infobox_Mount")
    assert result is not None
    assert result["name"] == "Blazebringer"
    assert result["speed"] == "10"
    assert result["eventmount"] == "sim"
    assert result["premium"] == "sim"


def test_extract_infobox_not_found():
    result = extract_infobox("Just some text", "Infobox_Criatura")
    assert result is None


def test_extract_infobox_none_content():
    result = extract_infobox(None, "Infobox_Criatura")
    assert result is None


def test_extract_infobox_space_variant():
    content = read_fixture("dragon.txt").replace("Infobox_Criatura", "Infobox Criatura")
    result = extract_infobox(content, "Infobox_Criatura")
    assert result is not None
    assert result["name"] == "Dragon"


# === Helper function tests ===

def test_clean_wikilinks():
    assert clean_wikilinks("[[Dragon Lord]]") == "Dragon Lord"
    assert clean_wikilinks("[[Santa Claus|Papai Noel]]") == "Papai Noel"
    assert clean_wikilinks("[[Gold Coin]]s") == "Gold Coins"
    assert clean_wikilinks("text <noinclude>hidden</noinclude> more") == "text  more"
    assert clean_wikilinks("") == ""
    assert clean_wikilinks(None) is None


def test_parse_boolean():
    assert parse_boolean("sim") is True
    assert parse_boolean("Sim") is True
    assert parse_boolean("yes") is True
    assert parse_boolean("não") is False
    assert parse_boolean("no") is False
    assert parse_boolean("") is None
    assert parse_boolean(None) is None
    assert parse_boolean("  ") is None


def test_parse_int():
    assert parse_int("1000") == 1000
    assert parse_int("100%") == 100
    assert parse_int("") is None
    assert parse_int(None) is None
    assert parse_int("--") is None
    assert parse_int("6400") == 6400


def test_parse_float():
    assert parse_float("85.00") == 85.0
    assert parse_float("1.04") == 1.04
    assert parse_float("") is None
    assert parse_float(None) is None


# === Type-specific parser tests ===

def test_creature_parser():
    content = read_fixture("dragon.txt")
    result = creatures.parse(12345, content)
    assert result is not None
    assert result["page_id"] == 12345
    assert result["name"] == "Dragon"
    assert result["hp"] == 1000
    assert result["exp"] == 700
    assert result["speed"] == 210
    assert result["fire_mod"] == 0
    assert result["ice_mod"] == 110
    assert result["illusionable"] is True
    assert result["pushable"] is False
    assert result["mitigation"] == 1.04
    assert "Gold Coin" in result["loot_common"]


def test_item_parser():
    content = read_fixture("magic_plate_armor.txt")
    result = items.parse(67890, content)
    assert result is not None
    assert result["page_id"] == 67890
    assert result["name"] == "Magic Plate Armor"
    assert result["armor"] == 17
    assert result["npc_value"] == 6400
    assert result["weight"] == 85.0
    assert result["imbuement_slots"] == 3
    assert result["classification"] == 4


def test_mount_parser():
    content = read_fixture("blazebringer.txt")
    result = mounts.parse(11111, content)
    assert result is not None
    assert result["page_id"] == 11111
    assert result["name"] == "Blazebringer"
    assert result["speed"] == 10
    assert result["event_mount"] is True
    assert result["premium"] is True


def test_creature_parser_no_infobox():
    result = creatures.parse(99999, "Just some random text without infobox")
    assert result is None


if __name__ == "__main__":
    # Run all test functions
    test_functions = [v for k, v in globals().items() if k.startswith("test_")]
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
