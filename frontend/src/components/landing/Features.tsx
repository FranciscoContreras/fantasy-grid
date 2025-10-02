const features = [
  {
    title: 'START/SIT AI',
    description:
      'Clear START, CONSIDER, or BENCH recommendations powered by machine learning. No more second-guessing.',
    stat: '92%',
    statLabel: 'Accuracy',
    gradient: 'from-emerald-400 to-green-600',
  },
  {
    title: 'NEXT GEN STATS',
    description:
      "NFL's official tracking data: EPA, CPOE, air yards, separation. Professional analytics.",
    stat: '20+',
    statLabel: 'Data Points',
    gradient: 'from-cyan-400 to-blue-600',
  },
  {
    title: 'WEATHER INTEL',
    description:
      'Real-time weather impact analysis. Know how wind, rain, and snow affect performance.',
    stat: '100%',
    statLabel: 'Coverage',
    gradient: 'from-blue-400 to-indigo-600',
  },
  {
    title: 'INJURY TRACKING',
    description:
      'Instant alerts on status changes and practice participation. Stay ahead of the news.',
    stat: 'Live',
    statLabel: 'Updates',
    gradient: 'from-red-400 to-rose-600',
  },
  {
    title: 'MATCHUP RATINGS',
    description:
      'Advanced defensive metrics for every position. Target the weak defenses.',
    stat: 'A+ to F',
    statLabel: 'Grading',
    gradient: 'from-purple-400 to-pink-600',
  },
  {
    title: 'PLAYER GRADES',
    description:
      'AI analyzes 20+ factors to grade each player with confidence scores every week.',
    stat: '73%',
    statLabel: 'Win Rate',
    gradient: 'from-yellow-400 to-orange-600',
  },
];

export function Features() {
  return (
    <div className="relative py-24 sm:py-32 bg-black text-white overflow-hidden">
      {/* Background pattern */}
      <div className="absolute inset-0 opacity-10" style={{
        backgroundImage: 'linear-gradient(rgba(0, 247, 255, 0.1) 1px, transparent 1px), linear-gradient(90deg, rgba(0, 247, 255, 0.1) 1px, transparent 1px)',
        backgroundSize: '50px 50px'
      }}></div>

      <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Section Header */}
        <div className="max-w-3xl mb-20">
          <div className="inline-flex items-center gap-2 px-4 py-2 bg-white/5 backdrop-blur-sm border border-white/10 rounded-full mb-6">
            <div className="w-2 h-2 bg-cyan-400 rounded-full animate-pulse"></div>
            <span className="text-xs font-bold text-cyan-400 uppercase tracking-wider">
              Built for Winners
            </span>
          </div>
          <h2 className="text-4xl sm:text-5xl md:text-6xl lg:text-7xl font-black tracking-tighter mb-6 leading-none">
            EVERY
            <br />
            <span className="bg-gradient-to-r from-cyan-400 via-blue-500 to-purple-600 bg-clip-text text-transparent">
              ADVANTAGE
            </span>
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
              className="group relative bg-white/5 backdrop-blur-xl border border-white/10 rounded-2xl p-8 hover:bg-white/10 transition-all hover:scale-105 hover:border-cyan-500/50"
            >
              {/* Gradient overlay on hover */}
              <div className={`absolute inset-0 bg-gradient-to-br ${feature.gradient} opacity-0 group-hover:opacity-10 rounded-2xl transition-opacity`}></div>

              <div className="relative">
                {/* Stat */}
                <div className="mb-6">
                  <div className={`text-5xl font-black bg-gradient-to-r ${feature.gradient} bg-clip-text text-transparent mb-1`}>
                    {feature.stat}
                  </div>
                  <div className="text-sm text-gray-400 uppercase tracking-wider font-semibold">
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
          <div className="absolute inset-0 bg-gradient-to-r from-cyan-500 via-blue-500 to-purple-600 blur-3xl opacity-20"></div>
          <div className="relative bg-gradient-to-br from-white/10 to-white/5 backdrop-blur-xl border border-white/20 rounded-3xl p-12 sm:p-16">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
              <div>
                <h3 className="text-3xl sm:text-4xl font-black mb-4 tracking-tight">
                  POWERED BY
                  <br />
                  <span className="bg-gradient-to-r from-cyan-400 to-blue-600 bg-clip-text text-transparent">
                    NEXT GEN TECH
                  </span>
                </h3>
                <p className="text-lg text-gray-300 leading-relaxed">
                  Real-time data pipeline. Machine learning models. NFL-grade analytics.
                  All working together to give you the edge.
                </p>
              </div>

              <div className="grid grid-cols-2 gap-6">
                <div className="bg-white/5 border border-white/10 rounded-xl p-6">
                  <div className="text-3xl font-black text-white mb-1">&lt; 50ms</div>
                  <div className="text-sm text-gray-400 uppercase tracking-wider font-semibold">Response Time</div>
                </div>
                <div className="bg-white/5 border border-white/10 rounded-xl p-6">
                  <div className="text-3xl font-black text-white mb-1">1M+</div>
                  <div className="text-sm text-gray-400 uppercase tracking-wider font-semibold">Predictions</div>
                </div>
                <div className="bg-white/5 border border-white/10 rounded-xl p-6">
                  <div className="text-3xl font-black text-white mb-1">24/7</div>
                  <div className="text-sm text-gray-400 uppercase tracking-wider font-semibold">Live Updates</div>
                </div>
                <div className="bg-white/5 border border-white/10 rounded-xl p-6">
                  <div className="text-3xl font-black text-white mb-1">99.9%</div>
                  <div className="text-sm text-gray-400 uppercase tracking-wider font-semibold">Uptime</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
