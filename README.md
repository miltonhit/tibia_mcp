# TibiaWiki Downloader

Ferramenta para baixar, parsear e indexar todo o conteúdo do [TibiaWiki](https://www.tibiawiki.com.br) — a wiki do MMORPG Tibia — e disponibilizá-lo via um servidor **MCP (Model Context Protocol)** para agentes de IA.

## Quick Start

A maneira mais rápida de subir tudo é usando o **Claude Code** com a skill `/start`:

```
/start
```

Isso irá automaticamente:
1. Verificar todos os pré-requisitos (Docker, portas livres, etc.)
2. Criar o diretório de dados persistentes para o PostgreSQL
3. Subir o banco, executar o crawler e iniciar o servidor MCP
4. Exibir a URL do MCP pronta para uso

> **MCP URL:** `http://localhost:8000/sse`

### Pré-requisitos

- [Docker](https://docs.docker.com/get-docker/) e Docker Compose V2
- Portas **5432** (PostgreSQL) e **8000** (MCP) livres

### Dados persistentes

Os dados do PostgreSQL ficam armazenados em `./data/postgres/` na máquina hospedeira. Isso significa que reiniciar os containers **não perde dados** — o crawler não precisa re-baixar tudo.

### Comandos úteis

```bash
# Ver logs em tempo real
docker compose logs -f

# Ver status dos serviços
docker compose ps

# Parar tudo (dados preservados)
docker compose down

# Reiniciar tudo do zero (apaga dados)
docker compose down -v && rm -rf ./data/postgres && docker compose up --build -d
```

### Configuração MCP para Claude Desktop

Adicione ao seu arquivo de configuração MCP:

```json
{
  "mcpServers": {
    "tibiawiki": {
      "url": "http://localhost:8000/sse"
    }
  }
}
```

---

## O que faz

1. **Baixa** todas as páginas do TibiaWiki via MediaWiki API (wikitext bruto)
2. **Parseia** infoboxes estruturadas de 20 tipos de entidades (criaturas, itens, spells, NPCs, quests, etc.)
3. **Armazena** os dados normalizados em PostgreSQL
4. **Extrai** coordenadas de mapa e gera tags/resumos por entidade
5. **Serve** os dados via MCP com 17 ferramentas otimizadas para consulta por agentes de IA

## Stack

- **Python 3.12**
- **PostgreSQL 16** — armazenamento relacional com views materializadas
- **FastMCP** — servidor MCP para integração com agentes de IA
- **Docker + Docker Compose** — ambiente containerizado
- **psycopg2**, **requests**, **python-dotenv**
- **pgvector + llama-index** _(opcional)_ — busca semântica por embeddings

## Estrutura do projeto

```
src/
  main.py           # Orquestrador (executa as 6 fases)
  mcp_server.py     # Servidor MCP com 17 ferramentas
  tagger.py         # Geração de tags e resumos
  api/              # Cliente HTTP com rate limiting e retry
  parser/           # Parsers por tipo de infobox (20 tipos)
  db/               # Conexão, migrations e upserts

migrations/         # 27 arquivos SQL numerados
tests/              # pytest + fixtures de wikitext
```

## Como funciona

O `src/main.py` executa 6 fases sequenciais:

```
Fase 0 → Migrations       Aplica os SQLs de migrations/ no banco
Fase 1 → Download         Baixa wikitext de todas as páginas (batch de 50)
Fase 2 → Parse & Import   Extrai infoboxes e faz upsert nas tabelas normalizadas
Fase 3 → Positions        Extrai coordenadas {{mapa|X,Y,Z}} para a tabela positions
Fase 4 → Tags & Summaries Gera tags (ex: "boss", "immune_fire") e resumos textuais
Fase 5 → Materialized Views Atualiza creature_drops, npc_trades, quest_bosses, etc.
```

## Entidades suportadas

| Entidade | Tabela | Infobox |
|----------|--------|---------|
| Criaturas | `creatures` | `Infobox_Criatura` |
| Itens | `items` | `Infobox_Item` |
| Spells | `spells` | `Infobox_Spell` |
| NPCs | `npcs` | `Infobox_NPC` |
| Quests | `quests` | `Infobox_Quest` |
| Conquistas | `achievements` | `Infobox_Achievement` |
| Montarias | `mounts` | `Infobox_Mount` |
| Outfits | `outfits` | `Infobox_Outfit` |
| Imbuimentos | `imbuements` | `Infobox_Imbuement` |
| Hunts | `hunts` | `Infobox_Hunts` |
| Livros | `books` | `Infobox_Book` |
| Construções | `buildings` | `Infobox_Building` |
| Mundos | `worlds` | `Infobox_World` |
| Runas | `runes` | `Infobox_Runas` |
| World Quests | `world_quests` | `Infobox_World_Quest` |
| World Changes | `world_changes` | `Infobox_World_Change` |
| Familiares | `familiars` | `Infobox Familiar` |
| Tarefas | `tasks` | `Infobox_Tasks` |
| Updates | `updates` | `Infobox_Updates` |
| Fansites | `fansites` | `Infobox_Fansite` |

## Servidor MCP

O `src/mcp_server.py` expõe 17 ferramentas para agentes de IA consultarem o banco. O padrão de uso sugerido é:

```
discover → filter → detail
```

Exemplos de ferramentas disponíveis:
- `search_creatures` — busca criaturas por nome ou tag
- `get_creature` — detalhes completos de uma criatura
- `list_creature_drops` — itens dropados por uma criatura
- `find_npcs_selling` — NPCs que vendem determinado item
- `search_quests` — busca quests por nome ou área

## Setup local (sem Docker)

```bash
# 1. Copie e edite o arquivo de configuração
cp .env.example .env

# 2. Instale as dependências
pip install -r requirements.txt

# 3. Execute o downloader
python -m src.main

# 4. Suba o servidor MCP
python -m src.mcp_server
```

## Testes

```bash
pytest tests/
```

Os fixtures em `tests/fixtures/` contêm amostras reais de wikitext para testar os parsers.

## Busca semântica (opcional)

Para habilitar busca semântica com embeddings:

1. Instale as dependências opcionais no `requirements.txt` (descomente as linhas de `llama-index`)
2. Certifique-se que a extensão `pgvector` está habilitada no PostgreSQL (migration `027_enable_pgvector.sql`)
3. Execute `python -m src.indexer` após o download
