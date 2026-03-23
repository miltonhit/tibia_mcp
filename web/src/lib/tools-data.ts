export type ToolCategory =
  | "discovery"
  | "search"
  | "creatures"
  | "items"
  | "hunting"
  | "map"
  | "advanced";

export interface Tool {
  name: string;
  description: string;
  category: ToolCategory;
  example?: string;
  emoji: string;
}

export const categories: Record<
  ToolCategory,
  { label: string; color: string }
> = {
  discovery: { label: "Discovery", color: "text-tibia-blue" },
  search: { label: "Search", color: "text-tibia-green" },
  creatures: { label: "Creatures", color: "text-tibia-red-glow" },
  items: { label: "Items", color: "text-tibia-gold-light" },
  hunting: { label: "Hunting", color: "text-tibia-green" },
  map: { label: "Map", color: "text-tibia-blue" },
  advanced: { label: "Advanced", color: "text-tibia-text-dim" },
};

export const tools: Tool[] = [
  {
    name: "describe_tables",
    description: "View database schema, row counts, and column details",
    category: "discovery",
    example: 'describe_tables("creatures")',
    emoji: "\uD83D\uDCCA",
  },
  {
    name: "list_entities",
    description: "Browse entities by type with pagination and sorting",
    category: "discovery",
    example: 'list_entities("items", limit=25)',
    emoji: "\uD83D\uDCCB",
  },
  {
    name: "search",
    description: "Full-text search across all entity types",
    category: "search",
    example: 'search("demon helmet")',
    emoji: "\uD83D\uDD0D",
  },
  {
    name: "search_by_tags",
    description: 'Filter entities by auto-generated tags like "boss" or "immune_fire"',
    category: "search",
    example: 'search_by_tags("creatures", ["boss", "high_exp"])',
    emoji: "\uD83C\uDFF7\uFE0F",
  },
  {
    name: "semantic_search",
    description: "Natural language AI-powered search via embeddings",
    category: "search",
    example: 'semantic_search("creatures that heal themselves")',
    emoji: "\uD83E\uDDE0",
  },
  {
    name: "creature_full_info",
    description: "Complete creature profile: stats, loot, hunts, quest appearances",
    category: "creatures",
    example: 'creature_full_info("Demon")',
    emoji: "\uD83D\uDC32",
  },
  {
    name: "creature_weakness",
    description: "Find creatures weak to a specific damage element",
    category: "creatures",
    example: 'creature_weakness("fire")',
    emoji: "\uD83D\uDD25",
  },
  {
    name: "compare_creatures",
    description: "Side-by-side stat and weakness comparison",
    category: "creatures",
    example: 'compare_creatures("Dragon Lord", "Frost Dragon")',
    emoji: "\u2694\uFE0F",
  },
  {
    name: "where_to_get_item",
    description: "All ways to obtain an item: drops, shops, quest rewards",
    category: "items",
    example: 'where_to_get_item("Falcon Longsword")',
    emoji: "\uD83D\uDCE6",
  },
  {
    name: "where_to_sell_item",
    description: "Find NPCs that buy a specific item and their prices",
    category: "items",
    example: 'where_to_sell_item("Demon Helmet")',
    emoji: "\uD83D\uDCB0",
  },
  {
    name: "items_for_vocation",
    description: "Equipment suitable for your class and body slot",
    category: "items",
    example: 'items_for_vocation("knight", "armor")',
    emoji: "\uD83D\uDEE1\uFE0F",
  },
  {
    name: "recommend_hunt",
    description: "Best hunting places by level and vocation",
    category: "hunting",
    example: 'recommend_hunt(250, "paladin")',
    emoji: "\uD83C\uDFAF",
  },
  {
    name: "profit_analysis",
    description: "Estimated gold per kill with detailed loot breakdown",
    category: "hunting",
    example: 'profit_analysis("Hydra")',
    emoji: "\uD83D\uDCB2",
  },
  {
    name: "get_map_url",
    description: "Generate TibiaWiki interactive map URLs",
    category: "map",
    example: "get_map_url(32369, 32241, 7)",
    emoji: "\uD83D\uDDFA\uFE0F",
  },
  {
    name: "search_by_position",
    description: "Find entities near specific map coordinates",
    category: "map",
    example: "search_by_position(32369, 32241, 7, radius=100)",
    emoji: "\uD83D\uDCCD",
  },
  {
    name: "nearby_entities",
    description: 'Entities near a named location — e.g. "near Rashid"',
    category: "map",
    example: 'nearby_entities("Rashid", radius=50)',
    emoji: "\uD83D\uDCCE",
  },
  {
    name: "rank_entities",
    description: "Top items by price, strongest creatures, best armor",
    category: "advanced",
    example: 'rank_entities("items", "npc_value")',
    emoji: "\uD83C\uDFC6",
  },
  {
    name: "query_database",
    description: "Custom read-only SQL SELECT queries",
    category: "advanced",
    example: "query_database(\"SELECT name, exp FROM creatures WHERE exp > 10000\")",
    emoji: "\uD83D\uDDC3\uFE0F",
  },
  {
    name: "get_entity",
    description: "Full details for any single entity by type and name",
    category: "advanced",
    example: 'get_entity("quests", "The Annihilator")',
    emoji: "\uD83D\uDD0E",
  },
];
