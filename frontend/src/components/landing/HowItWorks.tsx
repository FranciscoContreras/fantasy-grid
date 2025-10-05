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
    <div className="relative py-12 bg-white text-black overflow-hidden">
      <div className="relative max-w-7xl mx-auto px-4">
        {/* Section Header */}
        <div className="text-center max-w-2xl mx-auto mb-8">
          <div className="inline-flex items-center gap-2 px-3 py-1 bg-gray-100 rounded-full mb-3">
            <span className="text-xs font-bold text-gray-900 uppercase tracking-wider">
              Three Steps to Victory
            </span>
          </div>
          <h2 className="text-2xl sm:text-3xl lg:text-4xl font-black tracking-tight mb-3 leading-tight">
            How it works
          </h2>
          <p className="text-base text-gray-600 font-light">
            From roster to recommendations in under 3 minutes.
          </p>
        </div>

        {/* Steps */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
          {steps.map((step, index) => (
            <div key={index} className="relative group">
              <div className="relative bg-gray-50 border border-gray-200 rounded-lg p-4 hover:bg-gray-100 transition-all">
                {/* Step number */}
                <div className="mb-3">
                  <div className="text-3xl font-bold text-gray-200 group-hover:text-gray-300 transition-colors">
                    {step.number}
                  </div>
                </div>

                {/* Title */}
                <h3 className="text-sm font-bold mb-2 tracking-tight">
                  {step.title}
                </h3>

                {/* Description */}
                <p className="text-gray-600 leading-snug mb-3 text-xs">
                  {step.description}
                </p>

                {/* Time indicator */}
                <div className="inline-flex items-center gap-1 px-2 py-1 bg-gray-900 text-white rounded-full">
                  <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  <span className="text-xs font-bold uppercase tracking-wider">{step.time}</span>
                </div>
              </div>

              {/* Connecting arrow (mobile) */}
              {index < steps.length - 1 && (
                <div className="md:hidden flex justify-center my-3">
                  <svg className="w-6 h-6 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 14l-7 7m0 0l-7-7m7 7V3" />
                  </svg>
                </div>
              )}
            </div>
          ))}
        </div>

        {/* Bottom stats */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
          <div className="bg-gray-900 text-white rounded-lg p-4 text-center shadow-sm">
            <div className="text-xl font-bold mb-1">&lt; 3 min</div>
            <div className="text-gray-300 uppercase tracking-wider text-xs font-semibold">Setup Time</div>
          </div>
          <div className="bg-gray-900 text-white rounded-lg p-4 text-center shadow-sm">
            <div className="text-xl font-bold mb-1">Instant</div>
            <div className="text-gray-300 uppercase tracking-wider text-xs font-semibold">Recommendations</div>
          </div>
          <div className="bg-gray-900 text-white rounded-lg p-4 text-center shadow-sm">
            <div className="text-xl font-bold mb-1">Weekly</div>
            <div className="text-gray-300 uppercase tracking-wider text-xs font-semibold">Auto Updates</div>
          </div>
        </div>
      </div>
    </div>
  );
}
