import type { Metadata } from "next";
import Link from "next/link";

export const metadata: Metadata = {
  title:
    "Gym Rank X — Free Gamified Fitness App | Lose Weight with AI Coaching",
  description:
    "Gym Rank X is the ultimate free gamified fitness social network: personalized workouts, AI photo calorie counting, and real weight-loss coaching with Geni. Compete with friends and dominate the ranking.",
  keywords: [
    "free fitness app no subscription",
    "fitness gamification app",
    "workout challenge friends",
    "fitness leaderboard app",
    "social fitness app",
    "AI calorie counter",
    "lose weight app",
    "personalized workout app",
  ],
  alternates: {
    canonical: "https://gymrankx.com",
  },
  robots: {
    index: true,
    follow: true,
  },
  openGraph: {
    title: "Gym Rank X — Free Gamified Fitness App",
    description:
      "Personalized workouts, AI photo calorie counting, and real coaching to lose weight. Compete with friends and climb the ranking.",
    url: "https://gymrankx.com",
    siteName: "Gym Rank X",
    type: "website",
  },
};

const GRX = "https://gymrankx.com";

type Feature = {
  emoji: string;
  title: string;
  href: string;
  anchor: string;
  body: string;
};

const features: Feature[] = [
  {
    emoji: "\u{1F525}",
    title: "Lose Weight with Real Coaching",
    href: `${GRX}/en/weight-loss`,
    anchor: "Learn more",
    body: "Don't do it alone. Geni, the 24/7 AI coach, guides you on diet, workout, and consistency — the trio that actually works for healthy, sustainable weight loss. Track your progress and stay accountable through friendly competition.",
  },
  {
    emoji: "\u{1F4AA}",
    title: "Personalized Workouts",
    href: `${GRX}/en/personalized-workout`,
    anchor: "Learn more",
    body: "Tell Geni your goal and she builds a custom workout plan tailored to you. No fitness expertise required — just show up and follow along while the app adapts to your progress.",
  },
  {
    emoji: "\u{1F4F8}",
    title: "AI Photo Calorie Counter",
    href: `${GRX}/en/calorie-counter`,
    anchor: "Learn more",
    body: "Snap a photo of your meal and Geni does the rest: she calculates calories and macros, and tells you whether you're on track — no tedious manual entry needed.",
  },
  {
    emoji: "\u{1F3C6}",
    title: "Groups & Competition",
    href: `${GRX}/en/groups`,
    anchor: "Learn more",
    body: "Create groups, set the requirements, and challenge your friends. Earn badges, trophies, and level up as you stay consistent and reach milestones. Fitness is more fun when you're winning.",
  },
];

export default function GymRankPage() {
  return (
    <main className="min-h-screen px-6 py-16">
      <div className="max-w-4xl mx-auto">
        {/* Back link */}
        <Link
          href="/"
          className="font-terminal text-tibia-gold hover:text-tibia-gold-light text-lg"
        >
          &#x2190; Back to TibiaWiki MCP
        </Link>

        {/* Hero */}
        <header className="mt-10 text-center">
          <img
            src="/gymrankx-logo.png"
            alt="Gym Rank X logo"
            width={140}
            height={140}
            className="mx-auto w-32 h-32 object-contain drop-shadow-[0_0_16px_rgba(35,201,114,0.5)]"
          />
          <h1 className="font-terminal text-4xl sm:text-5xl text-[#34e288] mt-6">
            Gym Rank X
          </h1>
          <p className="text-tibia-text-dim text-lg max-w-2xl mx-auto mt-4 leading-relaxed">
            The ultimate <strong className="text-tibia-text">free</strong>{" "}
            gamified fitness social network. Custom workouts, photo calorie
            counting, and daily coaching with Geni. Ranking, disputes,
            competition and much more with your friends.{" "}
            <strong className="text-[#34e288]">
              Get in the game and be the best.
            </strong>
          </p>

          <div className="flex flex-wrap items-center justify-center gap-4 mt-8">
            <a
              href={GRX}
              target="_blank"
              rel="noopener"
              className="rounded-lg bg-[#23C972] px-7 py-3 font-terminal text-xl text-black transition-transform hover:scale-105"
            >
              Visit gymrankx.com
            </a>
            <a
              href={`${GRX}/en/download`}
              target="_blank"
              rel="noopener"
              className="rounded-lg border-2 border-[#23C972]/60 px-7 py-3 font-terminal text-xl text-[#34e288] transition-colors hover:border-[#23C972]"
            >
              Download the app
            </a>
          </div>
        </header>

        {/* Feature backlinks */}
        <section className="mt-16 grid sm:grid-cols-2 gap-6">
          {features.map((f) => (
            <article
              key={f.href}
              className="rounded-xl border border-[#23C972]/30 bg-[#0d1f16]/40 p-6"
            >
              <div className="text-3xl mb-3">{f.emoji}</div>
              <h2 className="font-terminal text-2xl text-[#34e288] mb-3">
                {f.title}
              </h2>
              <p className="text-tibia-text-dim leading-relaxed mb-4">
                {f.body}
              </p>
              <a
                href={f.href}
                target="_blank"
                rel="noopener"
                className="font-terminal text-lg text-tibia-gold hover:text-tibia-gold-light underline"
              >
                {f.anchor} &#x2192;
              </a>
            </article>
          ))}
        </section>

        {/* Download / store links */}
        <section className="mt-14 text-center">
          <h2 className="font-terminal text-2xl text-tibia-text mb-5">
            Download Gym Rank X for free
          </h2>
          <div className="flex flex-wrap items-center justify-center gap-4">
            <a
              href="https://apps.apple.com/br/app/gym-rank-x/id6745733221"
              target="_blank"
              rel="noopener"
              className="font-terminal text-lg text-[#34e288] hover:underline"
            >
              Gym Rank X on the App Store
            </a>
            <span className="text-tibia-text-dim/40">&#x2022;</span>
            <a
              href="https://play.google.com/store/apps/details?id=com.mcriativo.gymrankx"
              target="_blank"
              rel="noopener"
              className="font-terminal text-lg text-[#34e288] hover:underline"
            >
              Gym Rank X on Google Play
            </a>
          </div>
          <p className="text-tibia-text-dim mt-8 max-w-2xl mx-auto leading-relaxed">
            Visit the official{" "}
            <a
              href={GRX}
              target="_blank"
              rel="noopener"
              className="text-tibia-gold hover:text-tibia-gold-light underline"
            >
              gymrankx.com
            </a>{" "}
            website or follow{" "}
            <a
              href="https://instagram.com/gymrankx"
              target="_blank"
              rel="noopener"
              className="text-tibia-gold hover:text-tibia-gold-light underline"
            >
              @gymrankx on Instagram
            </a>
            .
          </p>
        </section>

        <div className="pixel-divider max-w-3xl mx-auto my-14" />
        <p className="text-center font-terminal text-tibia-text-dim/50 text-base">
          Gym Rank X is a separate product by the same maker as TibiaWiki MCP.
        </p>
      </div>
    </main>
  );
}
