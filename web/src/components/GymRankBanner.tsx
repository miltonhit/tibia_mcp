import Link from "next/link";

export default function GymRankBanner() {
  return (
    <section className="py-16 px-6">
      <div className="max-w-5xl mx-auto">
        <Link
          href="/gymrankx"
          aria-label="Learn more about Gym Rank X, the gamified fitness app"
          className="group block rounded-xl border-2 border-[#23C972]/50 bg-gradient-to-br from-[#0d1f16] via-black to-[#1a0a1f] p-8 sm:p-10 transition-all hover:border-[#23C972] hover:shadow-[0_0_30px_rgba(35,201,114,0.25)]"
        >
          <div className="flex flex-col sm:flex-row items-center gap-6 sm:gap-8">
            {/* Logo */}
            <img
              src="/gymrankx-logo.png"
              alt="Gym Rank X logo"
              width={120}
              height={120}
              className="w-24 h-24 sm:w-28 sm:h-28 object-contain shrink-0 drop-shadow-[0_0_12px_rgba(35,201,114,0.4)]"
            />

            {/* Copy */}
            <div className="flex-1 text-center sm:text-left">
              <p className="font-pixel text-[#FFEB3B] text-[10px] mb-3">
                From the same maker &#x2014; Advertisement
              </p>
              <h2 className="font-terminal text-3xl sm:text-4xl text-[#34e288] mb-2">
                Gym Rank X
              </h2>
              <p className="text-tibia-text-dim leading-relaxed mb-1">
                The ultimate{" "}
                <span className="text-tibia-text">gamified fitness</span> social
                network. Personalized workouts, AI photo calorie counting, and
                real coaching to{" "}
                <span className="text-[#34e288]">lose weight</span> &#x2014;
                compete with friends and climb the ranking.
              </p>
            </div>

            {/* CTA */}
            <div className="shrink-0">
              <span className="inline-flex items-center gap-2 rounded-lg bg-[#23C972] px-6 py-3 font-terminal text-xl text-black transition-transform group-hover:scale-105">
                Discover it &#x2192;
              </span>
            </div>
          </div>
        </Link>
      </div>
    </section>
  );
}
