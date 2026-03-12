import os

from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://tibiawiki:tibiawiki@localhost:5432/tibiawiki")
WIKI_API_URL = os.getenv("WIKI_API_URL", "https://www.tibiawiki.com.br/api.php")
RATE_LIMIT_SECONDS = float(os.getenv("RATE_LIMIT_SECONDS", "1"))
BATCH_SIZE = int(os.getenv("BATCH_SIZE", "50"))

MIGRATIONS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "migrations")

# Infobox templates to search for (template name -> target table)
INFOBOX_TEMPLATES = {
    "Infobox_Criatura": "creatures",
    "Infobox_Item": "items",
    "Infobox_Spell": "spells",
    "Infobox_NPC": "npcs",
    "Infobox_Quest": "quests",
    "Infobox_Achievement": "achievements",
    "Infobox_Mount": "mounts",
    "Infobox_Outfit": "outfits",
    "Infobox_Imbuement": "imbuements",
    "Infobox_Hunts": "hunts",
    "Infobox_Book": "books",
    "Infobox_Building": "buildings",
    "Infobox_World": "worlds",
    "Infobox_Runas": "runes",
    "Infobox_World_Quest": "world_quests",
    "Infobox_World_Change": "world_changes",
    "Infobox Familiar": "familiars",
    "Infobox_Tasks": "tasks",
    "Infobox_Updates": "updates",
    "Infobox_Fansite": "fansites",
}
