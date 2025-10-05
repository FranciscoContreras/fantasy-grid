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
    <div className="relative py-24 sm:py-32 bg-white text-black overflow-hidden">

      <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Section Header */}
        <div className="text-center max-w-3xl mx-auto mb-20">
          <div className="inline-flex items-center gap-2 px-4 py-2 bg-gray-100 rounded-full mb-6">
            <span className="text-xs font-bold text-gray-900 uppercase tracking-wider">
              Three Steps to Victory
            </span>
          </div>
          <h2 className="text-5xl sm:text-6xl md:text-7xl lg:text-8xl font-black tracking-tighter mb-6 leading-none">
            HOW IT
            <br />
            WORKS
          </h2>
          <p className="text-xl sm:text-2xl text-gray-600 font-light">
            From roster to recommendations in under 3 minutes.
          </p>
        </div>

        {/* Steps */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-20">
          {steps.map((step, index) => (
            <div key={index} className="relative group">
              <div className="relative bg-gray-50 border border-gray-200 rounded-2xl p-8 hover:bg-gray-100 transition-all">
                {/* Step number */}
                <div className="mb-8">
                  <div className="text-7xl font-black text-gray-200 group-hover:text-gray-300 transition-colors">
                    {step.number}
                  </div>
                </div>

                {/* Title */}
                <h3 className="text-2xl font-black mb-4 tracking-tight">
                  {step.title}
                </h3>

                {/* Description */}
                <p className="text-gray-600 leading-relaxed mb-6">
                  {step.description}
                </p>

                {/* Time indicator */}
                <div className="inline-flex items-center gap-2 px-4 py-2 bg-gray-900 text-white rounded-full">
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  <span className="text-xs font-bold uppercase tracking-wider">{step.time}</span>
                </div>
              </div>

              {/* Connecting arrow (mobile) */}
              {index < steps.length - 1 && (
                <div className="md:hidden flex justify-center my-6">
                  <svg className="w-8 h-8 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 14l-7 7m0 0l-7-7m7 7V3" />
                  </svg>
                </div>
              )}
            </div>
          ))}
        </div>

        {/* Bottom stats */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-6">
          <div className="bg-gray-900 text-white rounded-2xl p-8 text-center shadow-sm">
            <div className="text-4xl font-black mb-2">&lt; 3 min</div>
            <div className="text-gray-300 uppercase tracking-wider text-xs font-semibold">Setup Time</div>
          </div>
          <div className="bg-gray-900 text-white rounded-2xl p-8 text-center shadow-sm">
            <div className="text-4xl font-black mb-2">Instant</div>
            <div className="text-gray-300 uppercase tracking-wider text-xs font-semibold">Recommendations</div>
          </div>
          <div className="bg-gray-900 text-white rounded-2xl p-8 text-center shadow-sm">
            <div className="text-4xl font-black mb-2">Weekly</div>
            <div className="text-gray-300 uppercase tracking-wider text-xs font-semibold">Auto Updates</div>
          </div>
        </div>
      </div>
    </div>
  );
}
