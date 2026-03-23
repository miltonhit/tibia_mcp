"use client";

import { useState } from "react";
import { examples } from "@/lib/examples-data";
import RetroTerminal from "./RetroTerminal";

export default function UsageExamples() {
  const [activeIndex, setActiveIndex] = useState(0);
  const active = examples[activeIndex];

  return (
    <section className="py-20 px-6">
      <div className="max-w-4xl mx-auto">
        <h2 className="font-pixel text-tibia-gold text-sm sm:text-base text-center mb-4">
          See It In Action
        </h2>
        <p className="font-terminal text-tibia-text-dim text-xl text-center mb-10">
          Ask a question, get structured data
        </p>

        {/* Tab buttons */}
        <div className="flex gap-2 mb-6 overflow-x-auto pb-2">
          {examples.map((ex, i) => (
            <button
              key={i}
              onClick={() => setActiveIndex(i)}
              className={`shrink-0 px-4 py-2 rounded font-terminal text-base transition-colors cursor-pointer ${
                activeIndex === i
                  ? "bg-tibia-gold text-tibia-dark"
                  : "bg-tibia-panel text-tibia-text-dim hover:text-tibia-text"
              }`}
            >
              {ex.question.length > 30
                ? ex.question.slice(0, 28) + "..."
                : ex.question}
            </button>
          ))}
        </div>

        {/* Terminal */}
        <RetroTerminal>
          <div className="mb-4">
            <span className="text-tibia-text-dim">&gt; </span>
            <span className="text-terminal-green">
              &quot;{active.question}&quot;
            </span>
          </div>
          <div className="mb-4">
            <span className="text-tibia-text-dim">Tool: </span>
            <span className="text-tibia-gold">{active.toolCall}</span>
          </div>
          <div className="border-t border-tibia-gold-dim/20 pt-4">
            <pre className="text-tibia-text whitespace-pre overflow-x-auto text-base">
              {active.response}
            </pre>
          </div>
        </RetroTerminal>
      </div>
    </section>
  );
}
