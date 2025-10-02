const steps = [
  {
    number: '01',
    title: 'BUILD ROSTER',
    description:
      'Search and add your fantasy team players. All league formats supported.',
    time: '30s',
  },
  {
    number: '02',
    title: 'AI ANALYSIS',
    description:
      'Our AI analyzes matchups, weather, injuries, and trends automatically.',
    time: '5s',
  },
  {
    number: '03',
    title: 'WIN GAMES',
    description:
      'Get clear START/BENCH recommendations. Make decisions in seconds.',
    time: 'Instant',
  },
];

export function HowItWorks() {
  return (
    <div className="relative py-24 sm:py-32 bg-gradient-to-b from-black via-gray-900 to-black text-white overflow-hidden">
      {/* Background pattern */}
      <div className="absolute inset-0 opacity-10" style={{
        backgroundImage: 'linear-gradient(rgba(0, 247, 255, 0.1) 1px, transparent 1px), linear-gradient(90deg, rgba(0, 247, 255, 0.1) 1px, transparent 1px)',
        backgroundSize: '50px 50px'
      }}></div>

      {/* Glowing accent */}
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[800px] h-[800px] bg-gradient-to-r from-cyan-500 via-blue-500 to-purple-600 blur-3xl opacity-10"></div>

      <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Section Header */}
        <div className="text-center max-w-3xl mx-auto mb-20">
          <div className="inline-flex items-center gap-2 px-4 py-2 bg-white/5 backdrop-blur-sm border border-white/10 rounded-full mb-6">
            <div className="w-2 h-2 bg-cyan-400 rounded-full animate-pulse"></div>
            <span className="text-xs font-bold text-cyan-400 uppercase tracking-wider">
              Three Steps to Victory
            </span>
          </div>
          <h2 className="text-4xl sm:text-5xl md:text-6xl lg:text-7xl font-black tracking-tighter mb-6 leading-none">
            HOW IT
            <br />
            <span className="bg-gradient-to-r from-cyan-400 via-blue-500 to-purple-600 bg-clip-text text-transparent">
              WORKS
            </span>
          </h2>
          <p className="text-xl sm:text-2xl text-gray-400 font-light">
            From roster to recommendations in under 3 minutes.
          </p>
        </div>

        {/* Steps */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-20">
          {steps.map((step, index) => (
            <div key={index} className="relative group">
              {/* Connecting line (desktop) */}
              {index < steps.length - 1 && (
                <div className="hidden md:block absolute top-8 left-[60%] w-[80%] h-0.5 bg-gradient-to-r from-cyan-500/50 to-transparent"></div>
              )}

              <div className="relative bg-white/5 backdrop-blur-xl border border-white/10 rounded-2xl p-8 hover:bg-white/10 hover:border-cyan-500/50 transition-all">
                {/* Step number */}
                <div className="mb-8">
                  <div className="text-7xl font-black bg-gradient-to-r from-cyan-400 to-blue-600 bg-clip-text text-transparent opacity-20 group-hover:opacity-40 transition-opacity">
                    {step.number}
                  </div>
                </div>

                {/* Title */}
                <h3 className="text-2xl font-black mb-4 tracking-tight">
                  {step.title}
                </h3>

                {/* Description */}
                <p className="text-gray-400 leading-relaxed mb-6">
                  {step.description}
                </p>

                {/* Time indicator */}
                <div className="inline-flex items-center gap-2 px-4 py-2 bg-cyan-500/10 border border-cyan-500/30 rounded-full">
                  <svg className="w-4 h-4 text-cyan-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  <span className="text-sm font-bold text-cyan-400 uppercase tracking-wider">{step.time}</span>
                </div>
              </div>

              {/* Connecting arrow (mobile) */}
              {index < steps.length - 1 && (
                <div className="md:hidden flex justify-center my-6">
                  <svg className="w-8 h-8 text-cyan-500/50" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 14l-7 7m0 0l-7-7m7 7V3" />
                  </svg>
                </div>
              )}
            </div>
          ))}
        </div>

        {/* Bottom stats */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-6">
          <div className="bg-gradient-to-br from-emerald-500/10 to-green-600/10 backdrop-blur-xl border border-emerald-500/30 rounded-2xl p-8 text-center">
            <div className="text-4xl font-black text-emerald-400 mb-2">&lt; 3 min</div>
            <div className="text-gray-400 uppercase tracking-wider text-sm font-semibold">Setup Time</div>
          </div>
          <div className="bg-gradient-to-br from-cyan-500/10 to-blue-600/10 backdrop-blur-xl border border-cyan-500/30 rounded-2xl p-8 text-center">
            <div className="text-4xl font-black text-cyan-400 mb-2">Instant</div>
            <div className="text-gray-400 uppercase tracking-wider text-sm font-semibold">Recommendations</div>
          </div>
          <div className="bg-gradient-to-br from-purple-500/10 to-pink-600/10 backdrop-blur-xl border border-purple-500/30 rounded-2xl p-8 text-center">
            <div className="text-4xl font-black text-purple-400 mb-2">Weekly</div>
            <div className="text-gray-400 uppercase tracking-wider text-sm font-semibold">Auto Updates</div>
          </div>
        </div>
      </div>
    </div>
  );
}
