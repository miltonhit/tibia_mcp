export interface Example {
  question: string;
  toolCall: string;
  response: string;
}

export const examples: Example[] = [
  {
    question: "Best hunts for Paladin level 250?",
    toolCall: 'recommend_hunt(250, "paladin")',
    response: `Hunting Place         | Exp Rating | Loot Rating
----------------------|------------|------------
Asura Palace          | ★★★★★      | ★★★★☆
Cobras                | ★★★★☆      | ★★★★★
Summer Elves          | ★★★★☆      | ★★★★☆
Issavi Surface        | ★★★★☆      | ★★★☆☆
Werelions             | ★★★☆☆      | ★★★★★`,
  },
  {
    question: "Where does Falcon Longsword drop?",
    toolCall: 'where_to_get_item("Falcon Longsword")',
    response: `Source                | Type       | Rarity
----------------------|------------|--------
Grand Master Oberon   | Drop       | Semi-rare
Falcon Knight         | Drop       | Rare

NPC Price: 130,000 gp`,
  },
  {
    question: "Creatures weak to fire?",
    toolCall: 'creature_weakness("fire")',
    response: `Creature              | Fire Mod | HP      | Exp
----------------------|----------|---------|------
Ice Witch             | 110%     | 650     | 580
Crystal Spider        | 115%     | 1,250   | 900
Frost Dragon          | 110%     | 1,800   | 2,100
Massive Water Element | 110%     | 1,250   | 800`,
  },
  {
    question: "Dragon Lord vs Frost Dragon?",
    toolCall: 'compare_creatures("Dragon Lord", "Frost Dragon")',
    response: `Stat          | Dragon Lord  | Frost Dragon
--------------|-------------|-------------
HP            | 1,900       | 1,800
Exp           | 2,100       | 2,100
Fire          | 0% (immune) | 110% (weak)
Ice           | 110% (weak) | 0% (immune)
Earth         | 80%         | 100%
Loot Value    | ~2,800 gp   | ~3,100 gp`,
  },
  {
    question: "Most expensive items in the game?",
    toolCall: 'rank_entities("items", "npc_value")',
    response: `Item                  | NPC Value
----------------------|----------
Ferumbras' Hat        | 500,000 gp
Falcon Longsword      | 130,000 gp
Falcon Battleaxe      | 130,000 gp
Soulfire Rune         | 120,000 gp
Gnome Sword           | 100,000 gp`,
  },
  {
    question: "Where to sell Demon Helmet?",
    toolCall: 'where_to_sell_item("Demon Helmet")',
    response: `NPC          | City       | Price
-------------|------------|--------
Nah'Bob      | Ankrahmun  | 36,000 gp
Rashid       | Varies     | 36,000 gp
H.L.         | Venore     | 30,000 gp
Yaman        | Ankrahmun  | 32,000 gp`,
  },
];
