export default function Hero() {
  return (
    <section className="relative min-h-screen flex flex-col items-center justify-center px-6 overflow-hidden">
      {/* Radial glow */}
      <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_center,_rgba(212,160,23,0.08)_0%,_transparent_60%)]" />

      <div className="relative z-10 text-center max-w-4xl mx-auto">
        {/* Pixel decorations */}
        <div className="flex items-center justify-center gap-3 mb-6">
          <span className="text-2xl">&#x2694;&#xFE0F;</span>
          <span className="font-pixel text-[10px] text-tibia-gold-dim tracking-widest uppercase">
            Model Context Protocol
          </span>
          <span className="text-2xl">&#x1F6E1;&#xFE0F;</span>
        </div>

        {/* Title */}
        <h1 className="font-pixel text-tibia-gold text-xl sm:text-2xl md:text-3xl leading-relaxed mb-6 animate-flicker">
          Tibia
          <br />
          <span className="text-tibia-text">MCP Server</span>
        </h1>

        {/* Tagline */}
        <p className="font-terminal text-2xl sm:text-3xl text-tibia-text-dim mb-8 max-w-2xl mx-auto">
          Give your AI access to the{" "}
          <span className="text-tibia-gold-light">entire TibiaWiki database</span>
        </p>

        {/* Stats */}
        <div className="flex flex-wrap justify-center gap-6 sm:gap-10 mb-10 font-terminal text-xl">
          <div>
            <span className="text-tibia-gold text-2xl font-bold">20,000+</span>
            <span className="text-tibia-text-dim ml-2">entities</span>
          </div>
          <div>
            <span className="text-tibia-gold text-2xl font-bold">19</span>
            <span className="text-tibia-text-dim ml-2">tools</span>
          </div>
          <div>
            <span className="text-tibia-gold text-2xl font-bold">20</span>
            <span className="text-tibia-text-dim ml-2">entity types</span>
          </div>
        </div>

        {/* CTAs */}
        <div className="flex flex-col sm:flex-row gap-4 justify-center">
          <a
            href="https://github.com/miltonhit/tibia_mcp"
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center justify-center gap-2 px-8 py-3 bg-tibia-gold text-tibia-dark font-pixel text-xs rounded hover:bg-tibia-gold-light transition-colors"
          >
            <svg
              className="w-5 h-5"
              fill="currentColor"
              viewBox="0 0 24 24"
              aria-hidden="true"
            >
              <path
                fillRule="evenodd"
                d="M12 2C6.477 2 2 6.484 2 12.017c0 4.425 2.865 8.18 6.839 9.504.5.092.682-.217.682-.483 0-.237-.008-.868-.013-1.703-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466-.908-.62.069-.608.069-.608 1.003.07 1.531 1.032 1.531 1.032.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.026A9.564 9.564 0 0112 6.844c.85.004 1.705.115 2.504.337 1.909-1.296 2.747-1.027 2.747-1.027.546 1.379.202 2.398.1 2.651.64.7 1.028 1.595 1.028 2.688 0 3.848-2.339 4.695-4.566 4.943.359.309.678.92.678 1.855 0 1.338-.012 2.419-.012 2.747 0 .268.18.58.688.482A10.019 10.019 0 0022 12.017C22 6.484 17.522 2 12 2z"
                clipRule="evenodd"
              />
            </svg>
            View on GitHub
          </a>
          <a
            href="#quickstart"
            className="inline-flex items-center justify-center px-8 py-3 border-2 border-tibia-gold text-tibia-gold font-pixel text-xs rounded hover:bg-tibia-gold/10 transition-colors"
          >
            Quick Start
          </a>
        </div>

        <p className="font-terminal text-tibia-text-dim/50 text-base tracking-wide mt-6">
          feito por brasileiros &#x1F1E7;&#x1F1F7;
        </p>
      </div>

      {/* Scroll hint */}
      <div className="absolute bottom-8 animate-pixel-pulse">
        <span className="font-terminal text-tibia-text-dim text-xl">&#x25BC;</span>
      </div>
    </section>
  );
}
