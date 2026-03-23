import CategoryBadge from "./CategoryBadge";
import type { Tool } from "@/lib/tools-data";

interface ToolCardProps {
  tool: Tool;
}

export default function ToolCard({ tool }: ToolCardProps) {
  return (
    <div className="group border border-tibia-gold-dim/20 bg-tibia-panel/50 rounded-lg p-4 hover:border-tibia-gold-dim/50 hover:bg-tibia-panel transition-all">
      <div className="flex items-start justify-between mb-2">
        <span className="text-xl">{tool.emoji}</span>
        <CategoryBadge category={tool.category} />
      </div>
      <h3 className="font-terminal text-tibia-gold-light text-xl mb-1">
        {tool.name}
      </h3>
      <p className="text-tibia-text-dim text-sm mb-3 leading-relaxed">
        {tool.description}
      </p>
      {tool.example && (
        <code className="block text-xs bg-terminal-bg/60 text-terminal-green px-3 py-1.5 rounded font-terminal text-base overflow-x-auto">
          {tool.example}
        </code>
      )}
    </div>
  );
}
