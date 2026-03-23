export interface EntityType {
  name: string;
  emoji: string;
}

export const entityTypes: EntityType[] = [
  { name: "Creatures", emoji: "\uD83D\uDC32" },
  { name: "Items", emoji: "\u2694\uFE0F" },
  { name: "Spells", emoji: "\u2728" },
  { name: "NPCs", emoji: "\uD83D\uDC64" },
  { name: "Quests", emoji: "\uD83D\uDCDC" },
  { name: "Achievements", emoji: "\uD83C\uDFC6" },
  { name: "Mounts", emoji: "\uD83D\uDC0E" },
  { name: "Outfits", emoji: "\uD83D\uDC55" },
  { name: "Hunts", emoji: "\uD83C\uDFAF" },
  { name: "Books", emoji: "\uD83D\uDCD6" },
  { name: "Buildings", emoji: "\uD83C\uDFE0" },
  { name: "Worlds", emoji: "\uD83C\uDF0D" },
  { name: "Runes", emoji: "\uD83D\uDC8E" },
  { name: "Imbuements", emoji: "\uD83E\uDDEC" },
  { name: "World Quests", emoji: "\uD83D\uDDFA\uFE0F" },
  { name: "World Changes", emoji: "\uD83C\uDF00" },
  { name: "Familiars", emoji: "\uD83D\uDC7B" },
  { name: "Tasks", emoji: "\uD83D\uDCCB" },
  { name: "Updates", emoji: "\uD83D\uDCE6" },
  { name: "Fansites", emoji: "\uD83D\uDD17" },
];
