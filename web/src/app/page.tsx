import Hero from "@/components/Hero";
import GymRankBanner from "@/components/GymRankBanner";
import WhatIsThis from "@/components/WhatIsThis";
import ToolsShowcase from "@/components/ToolsShowcase";
import UsageExamples from "@/components/UsageExamples";
import QuickStart from "@/components/QuickStart";
import EntityTypes from "@/components/EntityTypes";
import Footer from "@/components/Footer";

export default function Home() {
  return (
    <>
      <Hero />
      <GymRankBanner />
      <WhatIsThis />
      <ToolsShowcase />
      <UsageExamples />
      <QuickStart />
      <EntityTypes />
      <Footer />
    </>
  );
}
