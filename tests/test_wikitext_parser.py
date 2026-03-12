"""Tests for the wikitext parser and type-specific parsers."""

import os
import sys

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from src.parser.wikitext import extract_infobox, clean_wikilinks, parse_boolean, parse_int, parse_float, extract_map_coords
from src.parser import creatures, items, mounts, books, buildings, worlds, runes, world_quests, familiars

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


# === extract_map_coords tests ===

def test_extract_map_coords_basic():
    text = "localizado em ({{mapa|32644,31601,6:5|aqui}})."
    coords = extract_map_coords(text)
    assert coords == [(32644, 31601, 6)]


def test_extract_map_coords_multiple():
    text = "({{mapa|33070,32882,6:2|aqui}}) e ({{mapa|33235,32485,7:2|aqui}})"
    coords = extract_map_coords(text)
    assert len(coords) == 2
    assert coords[0] == (33070, 32882, 6)
    assert coords[1] == (33235, 32485, 7)


def test_extract_map_coords_none():
    assert extract_map_coords(None) == []
    assert extract_map_coords("") == []
    assert extract_map_coords("no coordinates here") == []


def test_extract_map_coords_no_zoom():
    text = "{{mapa|32000,31000,7|aqui}}"
    coords = extract_map_coords(text)
    assert coords == [(32000, 31000, 7)]


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


# === New parser tests ===

def test_book_parser():
    content = read_fixture("elven_names_book.txt")
    result = books.parse(20001, content)
    assert result is not None
    assert result["page_id"] == 20001
    assert result["name"] == "Elven Names"
    assert result["translated"] is True
    assert "Ab'Dendriel" in result["location"]
    assert "Elven names are chosen" in result["text"]
    assert result["blurb"] == "Arquivo de como os elfos ganham seus nomes."


def test_building_parser():
    content = read_fixture("coastwood1.txt")
    result = buildings.parse(20002, content)
    assert result is not None
    assert result["page_id"] == 20002
    assert result["name"] == "Coastwood 1"
    assert result["building_type"] == "Casa"
    assert result["street"] == "Coastwood"
    assert result["size"] == 16
    assert result["beds"] == 2
    assert result["rent"] == 50000
    assert result["payrent"] == "Ab'Dendriel"
    assert result["openwindows"] == 4
    assert result["floors"] == 1
    assert result["rooms"] == 1


def test_world_parser():
    content = read_fixture("antica.txt")
    result = worlds.parse(20003, content)
    assert result is not None
    assert result["page_id"] == 20003
    assert result["name"] == "Antica"
    assert result["world_type"] == "Open PvP"
    assert result["location"] == "Reino Unido"
    assert result["transfer"] is True
    assert result["battleye"] == "yellow"


def test_rune_parser():
    content = read_fixture("sudden_death_rune.txt")
    result = runes.parse(20004, content)
    assert result is not None
    assert result["page_id"] == 20004
    assert result["name"] == "Sudden Death Rune"
    assert result["damage_type"] == "Death"
    assert result["words"] == "adori gran mort"
    assert result["make_mana"] == 985
    assert result["weight"] == 0.70
    assert result["ml_required"] == 15
    assert result["level_required"] == 45
    assert result["soul"] == 5
    assert result["make_qty"] == 3
    assert result["premium"] is False
    assert result["npc_price"] == 162
    assert result["store_value"] == 28


def test_world_quest_parser():
    content = read_fixture("devovorga.txt")
    result = world_quests.parse(20005, content)
    assert result is not None
    assert result["page_id"] == 20005
    assert result["name"] == "Rise of Devovorga"
    assert result["quest_type"] == "quest"
    assert result["start_date"] == "01 de Setembro"
    assert result["end_date"] == "07 de Setembro"
    assert result["frequency"] == "Anual"
    assert result["level"] == 20
    assert result["premium"] is True
    assert "Devovorga" in result["bosses"]


def test_familiar_parser():
    content = read_fixture("skullfrost.txt")
    result = familiars.parse(20006, content)
    assert result is not None
    assert result["page_id"] == 20006
    assert result["name"] == "Skullfrost"
    assert result["hp"] == 10000
    assert result["summon_cost"] == 1000
    assert result["vocation"] == "knight"
    assert result["illusionable"] is False
    assert result["pushable"] is True
    assert result["push_objects"] is False
    assert "cavaleiros" in result["notes"]


def test_building_with_coords():
    """Test that building location field preserves mapa template for coord extraction."""
    content = read_fixture("coastwood1.txt")
    raw = extract_infobox(content, "Infobox_Building")
    assert raw is not None
    # The raw location should contain the mapa template
    assert "mapa" in raw["location"]
    coords = extract_map_coords(raw["location"])
    assert coords == [(32644, 31601, 6)]


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
