"use client";

import RetroTerminal from "./RetroTerminal";

function CopyButton({ text }: { text: string }) {
  const handleCopy = () => {
    navigator.clipboard.writeText(text);
  };

  return (
    <button
      onClick={handleCopy}
      className="absolute top-3 right-3 p-1.5 rounded bg-tibia-panel hover:bg-tibia-panel-light transition-colors cursor-pointer"
      title="Copy to clipboard"
    >
      <svg
        className="w-4 h-4 text-tibia-text-dim"
        fill="none"
        stroke="currentColor"
        viewBox="0 0 24 24"
      >
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth={2}
          d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z"
        />
      </svg>
    </button>
  );
}

const dockerCommands = `git clone https://github.com/miltonhit/tibia_mcp
cd tibia_mcp
docker compose up -d`;

const mcpConfig = `{
  "mcpServers": {
    "tibiawiki": {
      "url": "http://localhost:8000/sse"
    }
  }
}`;

export default function QuickStart() {
  return (
    <section id="quickstart" className="py-20 px-6 bg-tibia-darker/50">
      <div className="max-w-5xl mx-auto">
        <h2 className="font-pixel text-tibia-gold text-sm sm:text-base text-center mb-4">
          Quick Start
        </h2>
        <p className="font-terminal text-tibia-text-dim text-xl text-center mb-10">
          Up and running in under a minute
        </p>

        <div className="grid md:grid-cols-2 gap-6 mb-8">
          {/* Panel 1: Docker */}
          <div>
            <h3 className="font-pixel text-[10px] text-tibia-gold-light mb-4 flex items-center gap-2">
              <span className="bg-tibia-gold text-tibia-dark w-6 h-6 rounded-full flex items-center justify-center text-[10px]">
                1
              </span>
              Start the Server
            </h3>
            <div className="relative">
              <CopyButton text={dockerCommands} />
              <RetroTerminal title="terminal">
                <div>
                  <span className="text-tibia-text-dim">$ </span>
                  <span className="text-tibia-text">
                    git clone https://github.com/miltonhit/tibia_mcp
                  </span>
                </div>
                <div>
                  <span className="text-tibia-text-dim">$ </span>
                  <span className="text-tibia-text">cd tibia_mcp</span>
                </div>
                <div>
                  <span className="text-tibia-text-dim">$ </span>
                  <span className="text-tibia-text">docker compose up -d</span>
                </div>
                <div className="mt-3 text-tibia-green text-base">
                  &#x2714; MCP server running on localhost:8000
                </div>
              </RetroTerminal>
            </div>
          </div>

          {/* Panel 2: MCP Config */}
          <div>
            <h3 className="font-pixel text-[10px] text-tibia-gold-light mb-4 flex items-center gap-2">
              <span className="bg-tibia-gold text-tibia-dark w-6 h-6 rounded-full flex items-center justify-center text-[10px]">
                2
              </span>
              Connect Your AI
            </h3>
            <div className="relative">
              <CopyButton text={mcpConfig} />
              <RetroTerminal title="mcp-config.json">
                <pre className="text-base">
                  <span className="text-tibia-text-dim">{"{"}</span>
                  {"\n"}
                  <span className="text-tibia-text-dim">{"  "}</span>
                  <span className="text-tibia-gold">
                    &quot;mcpServers&quot;
                  </span>
                  <span className="text-tibia-text-dim">: {"{"}</span>
                  {"\n"}
                  <span className="text-tibia-text-dim">{"    "}</span>
                  <span className="text-tibia-gold">
                    &quot;tibiawiki&quot;
                  </span>
                  <span className="text-tibia-text-dim">: {"{"}</span>
                  {"\n"}
                  <span className="text-tibia-text-dim">{"      "}</span>
                  <span className="text-tibia-gold">&quot;url&quot;</span>
                  <span className="text-tibia-text-dim">: </span>
                  <span className="text-tibia-green">
                    &quot;http://localhost:8000/sse&quot;
                  </span>
                  {"\n"}
                  <span className="text-tibia-text-dim">
                    {"    }"}
                    {"\n"}
                    {"  }"}
                    {"\n"}
                    {"}"}
                  </span>
                </pre>
              </RetroTerminal>
            </div>
          </div>
        </div>

        <p className="font-terminal text-tibia-text-dim text-center text-lg">
          Works with{" "}
          <span className="text-tibia-text">Claude Desktop</span>,{" "}
          <span className="text-tibia-text">Claude Code</span>,{" "}
          <span className="text-tibia-text">Cursor</span>,{" "}
          <span className="text-tibia-text">Windsurf</span>, and any
          MCP-compatible client.
        </p>
      </div>
    </section>
  );
}
