interface RetroTerminalProps {
  title?: string;
  children: React.ReactNode;
  className?: string;
}

export default function RetroTerminal({
  title = "tibiawiki-mcp",
  children,
  className = "",
}: RetroTerminalProps) {
  return (
    <div
      className={`rounded-lg overflow-hidden border border-tibia-gold-dim/30 ${className}`}
    >
      {/* Title bar */}
      <div className="flex items-center gap-2 px-4 py-2.5 bg-tibia-panel border-b border-tibia-gold-dim/20">
        <div className="flex gap-1.5">
          <div className="w-3 h-3 rounded-full bg-tibia-red" />
          <div className="w-3 h-3 rounded-full bg-tibia-gold" />
          <div className="w-3 h-3 rounded-full bg-tibia-green" />
        </div>
        <span className="font-terminal text-tibia-text-dim text-sm ml-2">
          {title}
        </span>
      </div>
      {/* Content */}
      <div className="scanlines bg-terminal-bg p-5 font-terminal text-lg leading-relaxed overflow-x-auto">
        {children}
      </div>
    </div>
  );
}
