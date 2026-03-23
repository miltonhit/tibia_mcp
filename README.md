# Tibia MCP Server

A tool that downloads, parses, and indexes all content from [TibiaWiki](https://www.tibiawiki.com.br) — the wiki for the MMORPG Tibia — and serves it via an **MCP (Model Context Protocol)** server for AI agents.

## Quick Start

The fastest way to get everything running is with [Claude Code](https://docs.anthropic.com/en/docs/claude-code) (Anthropic's official CLI). This project includes a custom **skill** `/start` that automates the entire setup:

1. Open a terminal at the project root
2. Start Claude Code: `claude`
3. Run the skill:

```
/start
```

The skill will automatically:
1. Check all prerequisites (Docker, Docker Compose, free ports, etc.)
2. Create the persistent data directory for PostgreSQL
3. Start the database, run the crawler, and launch the MCP server
4. Display the ready-to-use MCP URL

> **MCP URL:** `http://localhost:8000/sse`

### Prerequisites

- [Claude Code](https://docs.anthropic.com/en/docs/claude-code) installed (`npm install -g @anthropic-ai/claude-code`)
- [Docker](https://docs.docker.com/get-docker/) and Docker Compose V2
- Ports **5432** (PostgreSQL) and **8000** (MCP) available

### Persistent Data

PostgreSQL data is stored in `./data/postgres/` on the host machine. This means restarting containers **does not lose data** — the crawler doesn't need to re-download everything.

### Useful Commands

```bash
# Watch logs in real-time
docker compose logs -f

# Check service status
docker compose ps

# Stop everything (data preserved)
docker compose down

# Full reset (deletes data)
docker compose down -v && rm -rf ./data/postgres && docker compose up --build -d
```

### MCP Configuration for Claude Desktop

Add to your MCP configuration file:

```json
{
  "mcpServers": {
    "tibiawiki": {
      "url": "http://localhost:8000/sse"
    }
  }
}
```

Works with **Claude Desktop**, **Claude Code**, **Cursor**, **Windsurf**, and any MCP-compatible client.

---

## What It Does

1. **Downloads** all TibiaWiki pages via the MediaWiki API (raw wikitext)
2. **Parses** structured infoboxes from 20 entity types (creatures, items, spells, NPCs, quests, etc.)
3. **Stores** normalized data in PostgreSQL
4. **Extracts** map coordinates and generates tags/summaries per entity
5. **Serves** the data via MCP with 19 tools optimized for AI agent queries

## Stack

- **Python 3.12**
- **PostgreSQL 16** — relational storage with materialized views
- **FastMCP** — MCP server for AI agent integration
- **Docker + Docker Compose** — containerized environment
- **psycopg2**, **requests**, **python-dotenv**
- **pgvector + llama-index** _(optional)_ — semantic search via embeddings

## Project Structure

```
src/
  main.py           # Orchestrator (runs all 6 phases)
  mcp_server.py     # MCP server with 19 tools
  tagger.py         # Tag and summary generation
  api/              # HTTP client with rate limiting and retry
  parser/           # Parsers by infobox type (20 types)
  db/               # Connection, migrations, and upserts

migrations/         # 28 numbered SQL files
tests/              # pytest + wikitext fixtures
web/                # Next.js landing page
```

## How It Works

`src/main.py` runs 6 sequential phases:

```
Phase 0 → Migrations          Apply SQL migrations to the database
Phase 1 → Download            Download wikitext from all pages (batches of 50)
Phase 2 → Parse & Import      Extract infoboxes and upsert into normalized tables
Phase 3 → Positions           Extract {{mapa|X,Y,Z}} coordinates to the positions table
Phase 4 → Tags & Summaries    Generate tags (e.g. "boss", "immune_fire") and text summaries
Phase 5 → Materialized Views  Refresh creature_drops, npc_trades, quest_bosses, etc.
```

## Supported Entities

| Entity | Table | Infobox |
|--------|-------|---------|
| Creatures | `creatures` | `Infobox_Criatura` |
| Items | `items` | `Infobox_Item` |
| Spells | `spells` | `Infobox_Spell` |
| NPCs | `npcs` | `Infobox_NPC` |
| Quests | `quests` | `Infobox_Quest` |
| Achievements | `achievements` | `Infobox_Achievement` |
| Mounts | `mounts` | `Infobox_Mount` |
| Outfits | `outfits` | `Infobox_Outfit` |
| Imbuements | `imbuements` | `Infobox_Imbuement` |
| Hunts | `hunts` | `Infobox_Hunts` |
| Books | `books` | `Infobox_Book` |
| Buildings | `buildings` | `Infobox_Building` |
| Worlds | `worlds` | `Infobox_World` |
| Runes | `runes` | `Infobox_Runas` |
| World Quests | `world_quests` | `Infobox_World_Quest` |
| World Changes | `world_changes` | `Infobox_World_Change` |
| Familiars | `familiars` | `Infobox Familiar` |
| Tasks | `tasks` | `Infobox_Tasks` |
| Updates | `updates` | `Infobox_Updates` |
| Fansites | `fansites` | `Infobox_Fansite` |

## MCP Server

`src/mcp_server.py` exposes 19 tools for AI agents to query the database. The suggested usage pattern is:

```
discover → filter → detail
```

### Tools

| Category | Tool | Description |
|----------|------|-------------|
| Discovery | `describe_tables` | Database schema, row counts, and column details |
| Discovery | `list_entities` | Browse entities by type with pagination |
| Search | `search` | Full-text search across all entity types |
| Search | `search_by_tags` | Filter by auto-generated tags |
| Search | `semantic_search` | Natural language AI-powered search |
| Creatures | `creature_full_info` | Complete profile: stats, loot, hunts, quests |
| Creatures | `creature_weakness` | Find creatures weak to a specific element |
| Creatures | `compare_creatures` | Side-by-side stat comparison |
| Items | `where_to_get_item` | Drops, NPC shops, and quest rewards |
| Items | `where_to_sell_item` | NPCs that buy the item and their prices |
| Items | `items_for_vocation` | Equipment for a class and body slot |
| Hunting | `recommend_hunt` | Best hunts by level and vocation |
| Hunting | `profit_analysis` | Estimated gold per kill |
| Map | `get_map_url` | Generate TibiaWiki map URLs |
| Map | `search_by_position` | Find entities near coordinates |
| Map | `nearby_entities` | Entities near a named location |
| Advanced | `rank_entities` | Top items by price, strongest creatures, etc. |
| Advanced | `query_database` | Custom read-only SQL queries |
| Advanced | `get_entity` | Full details for any single entity |

### Usage Examples

Real questions an AI agent can answer using this MCP:

**Equipment recommendation by vocation and level**

> "What's the recommended set for a Knight level 400?"

The agent uses `items_for_vocation("knight")` filtering by each slot (`helmet`, `armor`, `legs`, `boots`, `shield`, `ring`) and cross-references with level to build the best combination:

| Slot | Item | Armor/Def | Resistances | Skill Boost |
|------|------|-----------|-------------|-------------|
| Helmet | Spiritthorn Helmet | 12 arm | Physical +6%, Energy +10% | Sword/Club/Axe +3 |
| Armor | Spiritthorn Armor | 20 arm | Physical +13% | Sword/Club/Axe +4 |
| Legs | Falcon Greaves | 10 arm | Physical +7%, Ice +7% | Melee +3 |
| Boots | Pair of Soulwalkers | 4 arm | Physical +7%, Fire +5% | Melee +1, Speed +15 |
| Shield | Soulbastion | 42 def | Physical +10%, Death +10% | — |
| Ring | Charged Spiritthorn Ring | 2 arm | Physical +8%, All Elements +4% | Melee +3 |

**Complete quest guide**

> "How do I complete the Desert Quest?"

The agent uses `search("desert quest", entity_type="quests")` followed by `get_entity("quests", "The Desert Dungeon Quest")` to return the full spoiler: preparation, required items, step-by-step path, sacrifice room positioning, and rewards.

**NPC locations**

> "Where are the guards for the Inquisition Quest?"

The agent fetches each NPC with `get_entity("npcs", "Walter, The Guard")` etc., returning exact coordinates and TibiaWiki map links:

| NPC | Coordinates | Link |
|-----|-------------|------|
| Henricus | 32316, 32268, z8 | [map](https://www.tibiawiki.com.br/wiki/Mapper?coords=32316,32268,8,3) |
| Walter, The Guard | 32341, 32278, z7 | [map](https://www.tibiawiki.com.br/wiki/Mapper?coords=32341,32278,7,3) |
| Tim, The Guard | 32424, 32226, z6 | [map](https://www.tibiawiki.com.br/wiki/Mapper?coords=32424,32226,6,3) |

**More examples**

- "Creatures weak to fire?" → `creature_weakness("fire")`
- "Where does Falcon Longsword drop?" → `where_to_get_item("Falcon Longsword")`
- "Best hunts for Paladin level 250?" → `recommend_hunt(250, "paladin")`
- "Most expensive items?" → `rank_entities("items", "npc_value")`
- "Dragon Lord vs Frost Dragon?" → `compare_creatures("Dragon Lord", "Frost Dragon")`
- "Where to sell Demon Helmet?" → `where_to_sell_item("Demon Helmet")`
- "Profit per kill at Hydra?" → `profit_analysis("Hydra")`

## Local Setup (without Docker)

```bash
# 1. Copy and edit the configuration file
cp .env.example .env

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the downloader
python -m src.main

# 4. Start the MCP server
python -m src.mcp_server
```

## Tests

```bash
pytest tests/
```

Fixtures in `tests/fixtures/` contain real wikitext samples for testing parsers.

## Semantic Search (optional)

To enable semantic search with embeddings:

1. Install the optional dependencies in `requirements.txt` (uncomment the `llama-index` lines)
2. Make sure the `pgvector` extension is enabled in PostgreSQL (migration `027_enable_pgvector.sql`)
3. Run `python -m src.indexer` after the download
