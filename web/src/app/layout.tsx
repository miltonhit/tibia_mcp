import type { Metadata } from "next";
import { Press_Start_2P, VT323, Inter } from "next/font/google";
import "./globals.css";
import { Analytics } from "@vercel/analytics/next";

const pressStart = Press_Start_2P({
  weight: "400",
  subsets: ["latin"],
  variable: "--font-pixel",
});

const vt323 = VT323({
  weight: "400",
  subsets: ["latin"],
  variable: "--font-terminal",
});

const inter = Inter({
  subsets: ["latin"],
  variable: "--font-body",
});

export const metadata: Metadata = {
  title: "TibiaWiki MCP Server | AI-Powered Tibia Data",
  description:
    "An MCP server that gives AI agents access to the entire TibiaWiki database — creatures, items, spells, NPCs, quests, and more from the MMORPG Tibia.",
  openGraph: {
    title: "TibiaWiki MCP Server",
    description:
      "Give your AI access to 20,000+ Tibia entities. 19 tools. Zero hallucinations.",
    url: "https://github.com/miltonhit/tibia_mcp",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html
      lang="en"
      className={`${pressStart.variable} ${vt323.variable} ${inter.variable}`}
    >
      <body className="min-h-screen bg-tibia-dark text-tibia-text font-body antialiased">
        {children}
        <Analytics />
      </body>
    </html>
  );
}
