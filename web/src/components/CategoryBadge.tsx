import { categories, type ToolCategory } from "@/lib/tools-data";

interface CategoryBadgeProps {
  category: ToolCategory;
}

const bgColors: Record<ToolCategory, string> = {
  discovery: "bg-tibia-blue/15 text-tibia-blue",
  search: "bg-tibia-green/15 text-tibia-green",
  creatures: "bg-tibia-red/15 text-tibia-red-glow",
  items: "bg-tibia-gold/15 text-tibia-gold-light",
  hunting: "bg-tibia-green-dark/30 text-tibia-green",
  map: "bg-tibia-blue-dark/30 text-tibia-blue",
  advanced: "bg-tibia-text-dim/10 text-tibia-text-dim",
};

export default function CategoryBadge({ category }: CategoryBadgeProps) {
  return (
    <span
      className={`inline-block px-2 py-0.5 rounded font-pixel text-[8px] tracking-wider uppercase ${bgColors[category]}`}
    >
      {categories[category].label}
    </span>
  );
}
