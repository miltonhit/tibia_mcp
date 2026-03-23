import { entityTypes } from "@/lib/entities-data";

export default function EntityTypes() {
  return (
    <section className="py-20 px-6">
      <div className="max-w-5xl mx-auto">
        <h2 className="font-pixel text-tibia-gold text-sm sm:text-base text-center mb-4">
          20 Entity Types
        </h2>
        <p className="font-terminal text-tibia-text-dim text-xl text-center mb-10">
          Every corner of the Tibia universe, structured and queryable
        </p>

        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-3">
          {entityTypes.map((entity) => (
            <div
              key={entity.name}
              className="border border-tibia-gold-dim/20 bg-tibia-panel/30 rounded-lg p-4 text-center hover:border-tibia-gold-dim/50 hover:bg-tibia-panel/60 transition-all group"
            >
              <div className="text-2xl mb-2 group-hover:scale-110 transition-transform">
                {entity.emoji}
              </div>
              <div className="font-terminal text-tibia-text text-lg">
                {entity.name}
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
