"use client";

import { useState } from "react";
import { tools, categories, type ToolCategory } from "@/lib/tools-data";
import ToolCard from "./ToolCard";

const allCategories: ("all" | ToolCategory)[] = [
  "all",
  "discovery",
  "search",
  "creatures",
  "items",
  "hunting",
  "map",
  "advanced",
];

export default function ToolsShowcase() {
  const [active, setActive] = useState<"all" | ToolCategory>("all");

  const filtered =
    active === "all" ? tools : tools.filter((t) => t.category === active);

  return (
    <section className="py-20 px-6 bg-tibia-darker/50">
      <div className="max-w-6xl mx-auto">
        <h2 className="font-pixel text-tibia-gold text-sm sm:text-base text-center mb-4">
          19 Tools for AI Agents
        </h2>
        <p className="font-terminal text-tibia-text-dim text-xl text-center mb-10">
          From quick lookups to complex cross-entity analysis
        </p>

        {/* Category tabs */}
        <div className="flex flex-wrap justify-center gap-2 mb-10">
          {allCategories.map((cat) => (
            <button
              key={cat}
              onClick={() => setActive(cat)}
              className={`px-4 py-2 rounded font-terminal text-lg transition-colors cursor-pointer ${
                active === cat
                  ? "bg-tibia-gold text-tibia-dark"
                  : "bg-tibia-panel text-tibia-text-dim hover:text-tibia-text hover:bg-tibia-panel-light"
              }`}
            >
              {cat === "all" ? "All" : categories[cat].label}
            </button>
          ))}
        </div>

        {/* Tools grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {filtered.map((tool) => (
            <ToolCard key={tool.name} tool={tool} />
          ))}
        </div>
      </div>
    </section>
  );
}
