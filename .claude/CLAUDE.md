# TibiaWiki Downloader — AI Context

## O que é este projeto

Sistema de extração, normalização e indexação de dados do **TibiaWiki** (wiki do MMORPG Tibia, em `tibiawiki.com.br`) via MediaWiki API. Os dados são armazenados em PostgreSQL e expostos via um servidor **MCP (Model Context Protocol)** para consumo por agentes de IA.

## Stack

| Camada | Tecnologia |
|--------|-----------|
| Linguagem | Python 3.12 |
| Banco de dados | PostgreSQL 16 |
| Driver DB | psycopg2-binary |
| HTTP client | requests (rate limiting + retry automático) |
| MCP server | FastMCP |
| Config | python-dotenv |
| Containerização | Docker + Docker Compose |
| Testes | pytest |
| Opcional | pgvector + llama-index (busca semântica) |

## Estrutura de pastas

```
src/
  main.py           # Orquestrador principal (executa as 6 fases em sequência)
  config.py         # Leitura de variáveis de ambiente
  mcp_server.py     # Servidor MCP com 17 ferramentas para agentes de IA
  tagger.py         # Geração de tags e resumos por entidade
  indexer.py        # Indexação semântica (opcional, via LlamaIndex)

  api/
    client.py       # WikiClient: HTTP com rate limiting e exponential backoff
    paginator.py    # Iteradores de páginas da API MediaWiki
    downloader.py   # Generator para baixar conteúdo das páginas

  parser/
    wikitext.py     # Parser base: extrai infoboxes de wikitext com regex
    creatures.py    # Infobox_Criatura
    items.py        # Infobox_Item
    spells.py       # Infobox_Spell
    npcs.py         # Infobox_NPC
    quests.py       # Infobox_Quest
    achievements.py # Infobox_Achievement
    mounts.py       # Infobox_Mount
    outfits.py      # Infobox_Outfit
    imbuements.py   # Infobox_Imbuement
    hunts.py        # Infobox_Hunts
    books.py        # Infobox_Book
    buildings.py    # Infobox_Building
    worlds.py       # Infobox_World
    runes.py        # Infobox_Runas
    world_quests.py # Infobox_World_Quest
    world_changes.py# Infobox_World_Change
    familiars.py    # Infobox Familiar
    tasks.py        # Infobox_Tasks
    updates.py      # Infobox_Updates
    fansites.py     # Infobox_Fansite

  db/
    connection.py   # get_connection() — singleton de conexão ao PostgreSQL
    migrator.py     # run_migrations() — aplica SQLs em migrations/ em ordem
    inserter.py     # upsert_raw_pages, upsert_parsed_records

migrations/         # 27 arquivos SQL numerados (001–027)
tests/              # pytest + fixtures de páginas wiki de exemplo
```

## Fluxo de execução (src/main.py)

O `main.py` executa **6 fases sequenciais**:

1. **Migrations** — aplica arquivos SQL de `migrations/` na tabela `schema_migrations`
2. **Download** — enumera e baixa wikitext de todas as páginas via API (batch de 50)
3. **Parse & Import** — para cada tipo de infobox, extrai campos e faz upsert nas tabelas normalizadas
4. **Extract Positions** — extrai coordenadas de mapa `{{mapa|X,Y,Z}}` para a tabela `positions`
5. **Generate Tags & Summaries** — gera tags e resumos textuais por entidade (ex: "boss", "immune_fire")
6. **Refresh Materialized Views** — atualiza views cruzadas (`creature_drops`, `npc_trades`, etc.)

## Variáveis de ambiente

Definidas no `.env` (copiar de `.env.example`):

| Variável | Padrão | Descrição |
|----------|--------|-----------|
| `DATABASE_URL` | `postgresql://tibiawiki:tibiawiki@localhost:5432/tibiawiki` | Conexão ao PostgreSQL |
| `WIKI_API_URL` | `https://www.tibiawiki.com.br/api.php` | Endpoint da API MediaWiki |
| `RATE_LIMIT_SECONDS` | `1` | Delay entre requisições à API (segundos) |
| `BATCH_SIZE` | `50` | Páginas por requisição (máx. 50) |
| `MIGRATIONS_DIR` | (auto) | Caminho para os arquivos SQL de migration |

## Servidor MCP (src/mcp_server.py)

Expõe **17 ferramentas** para agentes de IA consultarem o banco via linguagem natural ou filtros estruturados. Segue o padrão `discover → filter → detail`:

- `search_*` — busca textual por nome/tag
- `get_*` — detalhes de uma entidade específica
- `list_*` — listagens com filtros (ex: criaturas de uma área, drops de um item)
- `find_*` — queries cruzadas (ex: NPCs que vendem X, quests que requerem Y)

## Padrões e convenções

- **Parsers**: cada arquivo em `parser/` implementa uma função `parse_<tipo>(raw_wikitext) -> dict`. Usa `wikitext.extract_infobox()` + helpers de conversão de tipos.
- **Upserts**: todos os inserts usam `INSERT ... ON CONFLICT DO UPDATE` para idempotência.
- **Rate limiting**: o `WikiClient` respeita `RATE_LIMIT_SECONDS` e faz retry com backoff exponencial em falhas HTTP.
- **Migrations**: sempre adicionar novas migrations como arquivos numerados sequencialmente — nunca editar migrations existentes.
- **Testes**: fixtures em `tests/fixtures/` são amostras reais de wikitext para testar parsers.

## Como rodar localmente

```bash
cp .env.example .env
pip install -r requirements.txt
python -m src.main        # executa todas as fases
python -m src.mcp_server  # sobe o servidor MCP em :8000
```

Via Docker:

```bash
docker-compose up
```
