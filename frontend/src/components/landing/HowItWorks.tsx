const steps = [
  {
    number: '1',
    icon: '📝',
    title: 'Build Your Roster',
    description:
      'Search and add your fantasy team players in seconds. Support for all league formats: PPR, Half-PPR, and Standard scoring.',
    details: [
      'Quick player search',
      'Multiple roster support',
      'All league formats',
    ],
  },
  {
    number: '2',
    icon: '🔍',
    title: 'Get Weekly Analysis',
    description:
      'Every week, our AI analyzes all matchups, weather, injuries, and trends for your entire roster automatically.',
    details: [
      '20+ data points analyzed',
      'Real-time updates',
      'Advanced statistics',
    ],
  },
  {
    number: '3',
    icon: '🏆',
    title: 'Set Your Lineup & Win',
    description:
      'See clear START/BENCH recommendations with confidence scores. Make informed decisions in seconds, not hours.',
    details: [
      'Clear recommendations',
      'Confidence scores',
      'One-click lineup',
    ],
  },
];

export function HowItWorks() {
  return (
    <div className="py-16 sm:py-24 bg-gradient-to-br from-gray-50 to-gray-100">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Section Header */}
        <div className="text-center max-w-3xl mx-auto mb-16">
          <h2 className="text-3xl sm:text-4xl lg:text-5xl font-extrabold text-gray-900 mb-4">
            How It Works
          </h2>
          <p className="text-lg sm:text-xl text-gray-600">
            Get from roster to recommendations in 3 simple steps.
            <br className="hidden sm:block" />
            Start making smarter lineup decisions today.
          </p>
        </div>

        {/* Steps */}
        <div className="relative">
          {/* Connection line (desktop) */}
          <div className="hidden lg:block absolute top-1/4 left-0 right-0 h-1 bg-gradient-to-r from-blue-200 via-indigo-200 to-purple-200"></div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 lg:gap-12 relative">
            {steps.map((step, index) => (
              <div key={index} className="relative">
                {/* Step Card */}
                <div className="bg-white rounded-2xl p-8 shadow-lg hover:shadow-2xl transition-shadow border-2 border-gray-100 hover:border-blue-200 h-full">
                  {/* Step Number */}
                  <div className="absolute -top-6 left-8 w-12 h-12 bg-gradient-to-br from-blue-600 to-indigo-600 rounded-full flex items-center justify-center shadow-lg">
                    <span className="text-2xl font-bold text-white">{step.number}</span>
                  </div>

                  {/* Icon */}
                  <div className="mb-6 mt-4">
                    <div className="w-20 h-20 mx-auto bg-gradient-to-br from-blue-50 to-indigo-50 rounded-2xl flex items-center justify-center text-5xl">
                      {step.icon}
                    </div>
                  </div>

                  {/* Title */}
                  <h3 className="text-2xl font-bold text-gray-900 mb-4 text-center">
                    {step.title}
                  </h3>

                  {/* Description */}
                  <p className="text-gray-600 leading-relaxed mb-6 text-center">
                    {step.description}
                  </p>

                  {/* Details */}
                  <div className="space-y-2 pt-4 border-t border-gray-200">
                    {step.details.map((detail, idx) => (
                      <div key={idx} className="flex items-center gap-2 text-sm text-gray-700">
                        <svg className="w-5 h-5 text-green-500 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                        </svg>
                        <span>{detail}</span>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Arrow (desktop) */}
                {index < steps.length - 1 && (
                  <div className="hidden md:block absolute top-1/4 -right-6 lg:-right-8 transform translate-y-1/2">
                    <svg className="w-12 h-12 text-indigo-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
                    </svg>
                  </div>
                )}

                {/* Arrow (mobile) */}
                {index < steps.length - 1 && (
                  <div className="md:hidden flex justify-center my-6">
                    <svg className="w-12 h-12 text-indigo-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 14l-7 7m0 0l-7-7m7 7V3" />
                    </svg>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>

        {/* Time to Value */}
        <div className="mt-16 text-center">
          <div className="inline-flex items-center gap-4 bg-white rounded-full px-8 py-4 shadow-lg border-2 border-blue-200">
            <span className="text-3xl">⚡</span>
            <div className="text-left">
              <div className="text-sm text-gray-600">From signup to recommendations in</div>
              <div className="text-2xl font-bold bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent">
                Less than 3 minutes
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
