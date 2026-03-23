export default function WhatIsThis() {
  return (
    <section className="py-20 px-6">
      <div className="max-w-5xl mx-auto">
        <h2 className="font-pixel text-tibia-gold text-sm sm:text-base text-center mb-12">
          What Is This?
        </h2>

        {/* Two columns */}
        <div className="grid md:grid-cols-2 gap-8 mb-14">
          <div className="rpg-frame p-6 rounded-lg">
            <div className="text-3xl mb-3">&#x1F50C;</div>
            <h3 className="font-terminal text-tibia-gold-light text-2xl mb-3">
              MCP Server
            </h3>
            <p className="text-tibia-text-dim leading-relaxed">
              The{" "}
              <span className="text-tibia-text">
                Model Context Protocol
              </span>{" "}
              is an open standard that lets AI agents call external tools. This
              server exposes 19 specialized tools for querying structured Tibia
              game data — no hallucinations, just real wiki data.
            </p>
          </div>

          <div className="rpg-frame p-6 rounded-lg">
            <div className="text-3xl mb-3">&#x1F4D6;</div>
            <h3 className="font-terminal text-tibia-gold-light text-2xl mb-3">
              TibiaWiki Data
            </h3>
            <p className="text-tibia-text-dim leading-relaxed">
              Over{" "}
              <span className="text-tibia-text">20,000 entities</span>{" "}
              crawled from TibiaWiki and stored in PostgreSQL. Creatures, items,
              spells, NPCs, quests, and 15 more entity types — all parsed,
              normalized, and cross-referenced.
            </p>
          </div>
        </div>

        {/* Flow diagram */}
        <div className="flex flex-col sm:flex-row items-center justify-center gap-4 sm:gap-0">
          <div className="border border-tibia-blue/40 bg-tibia-blue-dark/20 rounded-lg px-5 py-3 text-center">
            <div className="font-terminal text-tibia-blue text-xl">AI Agent</div>
            <div className="font-terminal text-tibia-text-dim text-sm">
              &quot;Ask anything&quot;
            </div>
          </div>
          <div className="font-terminal text-tibia-gold text-2xl px-4 rotate-90 sm:rotate-0">
            &#x2192;
          </div>
          <div className="border border-tibia-gold/40 bg-tibia-gold/5 rounded-lg px-5 py-3 text-center">
            <div className="font-terminal text-tibia-gold text-xl">
              MCP Server
            </div>
            <div className="font-terminal text-tibia-text-dim text-sm">
              19 tools
            </div>
          </div>
          <div className="font-terminal text-tibia-gold text-2xl px-4 rotate-90 sm:rotate-0">
            &#x2192;
          </div>
          <div className="border border-tibia-green/40 bg-tibia-green-dark/20 rounded-lg px-5 py-3 text-center">
            <div className="font-terminal text-tibia-green text-xl">
              PostgreSQL
            </div>
            <div className="font-terminal text-tibia-text-dim text-sm">
              20,000+ entities
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
