const features = [
  {
    title: 'START/SIT AI',
    description:
      'Clear START, CONSIDER, or BENCH recommendations powered by machine learning. No more second-guessing.',
    stat: '92%',
    statLabel: 'Accuracy',
  },
  {
    title: 'NEXT GEN STATS',
    description:
      "NFL's official tracking data: EPA, CPOE, air yards, separation. Professional analytics.",
    stat: '20+',
    statLabel: 'Data Points',
  },
  {
    title: 'WEATHER INTEL',
    description:
      'Real-time weather impact analysis. Know how wind, rain, and snow affect performance.',
    stat: '100%',
    statLabel: 'Coverage',
  },
  {
    title: 'INJURY TRACKING',
    description:
      'Instant alerts on status changes and practice participation. Stay ahead of the news.',
    stat: 'Live',
    statLabel: 'Updates',
  },
  {
    title: 'MATCHUP RATINGS',
    description:
      'Advanced defensive metrics for every position. Target the weak defenses.',
    stat: 'A+ to F',
    statLabel: 'Grading',
  },
  {
    title: 'PLAYER GRADES',
    description:
      'AI analyzes 20+ factors to grade each player with confidence scores every week.',
    stat: '73%',
    statLabel: 'Win Rate',
  },
];

export function Features() {
  return (
    <div className="relative py-24 sm:py-32 bg-black text-white overflow-hidden">
      <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Section Header */}
        <div className="max-w-3xl mb-20">
          <div className="inline-flex items-center gap-2 px-4 py-2 bg-white/10 rounded-full mb-6">
            <span className="text-xs font-bold text-white uppercase tracking-wider">
              Built for Winners
            </span>
          </div>
          <h2 className="text-5xl sm:text-6xl md:text-7xl lg:text-8xl font-black tracking-tighter mb-6 leading-none">
            EVERY
            <br />
            ADVANTAGE
          </h2>
          <p className="text-xl sm:text-2xl text-gray-400 font-light max-w-2xl">
            Professional-grade analytics. Real-time insights. Zero compromise.
          </p>
        </div>

        {/* Features Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {features.map((feature, index) => (
            <div
              key={index}
              className="group relative bg-white/5 border border-white/10 rounded-2xl p-8 hover:bg-white/10 transition-all hover:scale-105"
            >
              <div className="relative">
                {/* Stat */}
                <div className="mb-6">
                  <div className="text-5xl font-black text-white mb-1">
                    {feature.stat}
                  </div>
                  <div className="text-xs text-gray-500 uppercase tracking-wider font-semibold">
                    {feature.statLabel}
                  </div>
                </div>

                {/* Title */}
                <h3 className="text-xl font-black mb-3 tracking-tight">
                  {feature.title}
                </h3>

                {/* Description */}
                <p className="text-gray-400 leading-relaxed text-sm">
                  {feature.description}
                </p>
              </div>
            </div>
          ))}
        </div>

        {/* Bottom CTA Section */}
        <div className="mt-20 relative">
          <div className="relative bg-white/5 border border-white/10 rounded-3xl p-12 sm:p-16">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
              <div>
                <h3 className="text-3xl sm:text-4xl font-black mb-4 tracking-tight">
                  POWERED BY
                  <br />
                  NEXT GEN TECH
                </h3>
                <p className="text-lg text-gray-400 leading-relaxed">
                  Real-time data pipeline. Machine learning models. NFL-grade analytics.
                  All working together to give you the edge.
                </p>
              </div>

              <div className="grid grid-cols-2 gap-6">
                <div className="bg-white/5 border border-white/10 rounded-xl p-6">
                  <div className="text-3xl font-black text-white mb-1">&lt; 50ms</div>
                  <div className="text-xs text-gray-500 uppercase tracking-wider font-semibold">Response Time</div>
                </div>
                <div className="bg-white/5 border border-white/10 rounded-xl p-6">
                  <div className="text-3xl font-black text-white mb-1">1M+</div>
                  <div className="text-xs text-gray-500 uppercase tracking-wider font-semibold">Predictions</div>
                </div>
                <div className="bg-white/5 border border-white/10 rounded-xl p-6">
                  <div className="text-3xl font-black text-white mb-1">24/7</div>
                  <div className="text-xs text-gray-500 uppercase tracking-wider font-semibold">Live Updates</div>
                </div>
                <div className="bg-white/5 border border-white/10 rounded-xl p-6">
                  <div className="text-3xl font-black text-white mb-1">99.9%</div>
                  <div className="text-xs text-gray-500 uppercase tracking-wider font-semibold">Uptime</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
