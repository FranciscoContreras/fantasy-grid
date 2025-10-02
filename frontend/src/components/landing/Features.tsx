import { Card, CardContent } from '../ui/card';

const features = [
  {
    icon: '🎯',
    title: 'Smart Start/Sit Recommendations',
    description:
      'Get clear START, CONSIDER, or BENCH recommendations for every player on your roster based on matchups, weather, and advanced analytics. No more second-guessing your lineup decisions.',
    color: 'from-green-500 to-emerald-500',
  },
  {
    icon: '🤖',
    title: 'AI-Powered Player Grading',
    description:
      'Machine learning models analyze 20+ factors to grade each player (A+ to F) with confidence scores. Know exactly who to trust in your lineup every week.',
    color: 'from-blue-500 to-indigo-500',
  },
  {
    icon: '📊',
    title: 'Next Gen Stats Integration',
    description:
      "Leverage NFL's official tracking data: EPA, CPOE, air yards, separation, route running, and more. Professional-grade analytics at your fingertips.",
    color: 'from-purple-500 to-pink-500',
  },
  {
    icon: '⛈️',
    title: 'Weather Impact Analysis',
    description:
      'Know exactly how weather conditions affect your players' performance before kickoff. Wind, rain, snow, and temperature all factored into recommendations.',
    color: 'from-cyan-500 to-blue-500',
  },
  {
    icon: '🏥',
    title: 'Real-Time Injury Updates',
    description:
      'Get instant alerts on injury status changes and practice participation. Never get caught off-guard by a last-minute inactive designation.',
    color: 'from-red-500 to-orange-500',
  },
  {
    icon: '🛡️',
    title: 'Defense Matchup Ratings',
    description:
      'See how defenses rank against each position with advanced defensive metrics. Target the weak defenses and avoid the elite units.',
    color: 'from-indigo-500 to-purple-500',
  },
];

export function Features() {
  return (
    <div className="py-16 sm:py-24 bg-white">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Section Header */}
        <div className="text-center max-w-3xl mx-auto mb-16">
          <h2 className="text-3xl sm:text-4xl lg:text-5xl font-extrabold text-gray-900 mb-4">
            Everything You Need to
            <span className="block bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent">
              Dominate Your League
            </span>
          </h2>
          <p className="text-lg sm:text-xl text-gray-600">
            Professional-grade analytics and AI-powered insights that give you the edge over your competition.
          </p>
        </div>

        {/* Features Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          {features.map((feature, index) => (
            <Card
              key={index}
              className="group hover:shadow-2xl transition-all duration-300 transform hover:-translate-y-2 border-2 hover:border-blue-200"
            >
              <CardContent className="p-6 sm:p-8">
                {/* Icon */}
                <div className="mb-6">
                  <div
                    className={`w-16 h-16 rounded-2xl bg-gradient-to-br ${feature.color} flex items-center justify-center text-3xl shadow-lg group-hover:shadow-xl group-hover:scale-110 transition-all`}
                  >
                    {feature.icon}
                  </div>
                </div>

                {/* Title */}
                <h3 className="text-xl font-bold text-gray-900 mb-3 group-hover:text-blue-600 transition-colors">
                  {feature.title}
                </h3>

                {/* Description */}
                <p className="text-gray-600 leading-relaxed">{feature.description}</p>
              </CardContent>
            </Card>
          ))}
        </div>

        {/* Additional Features */}
        <div className="mt-16 bg-gradient-to-br from-blue-50 to-indigo-50 rounded-3xl p-8 sm:p-12">
          <div className="text-center mb-8">
            <h3 className="text-2xl sm:text-3xl font-bold text-gray-900 mb-3">And Much More...</h3>
            <p className="text-lg text-gray-600">Additional features to give you every advantage</p>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
            <div className="flex items-start gap-3">
              <span className="text-2xl">📱</span>
              <div>
                <div className="font-semibold text-gray-900">Mobile Optimized</div>
                <div className="text-sm text-gray-600">Set lineups on the go</div>
              </div>
            </div>

            <div className="flex items-start gap-3">
              <span className="text-2xl">⚡</span>
              <div>
                <div className="font-semibold text-gray-900">Lightning Fast</div>
                <div className="text-sm text-gray-600">Instant analysis results</div>
              </div>
            </div>

            <div className="flex items-start gap-3">
              <span className="text-2xl">🔒</span>
              <div>
                <div className="font-semibold text-gray-900">Secure & Private</div>
                <div className="text-sm text-gray-600">Your data is protected</div>
              </div>
            </div>

            <div className="flex items-start gap-3">
              <span className="text-2xl">🔄</span>
              <div>
                <div className="font-semibold text-gray-900">Weekly Updates</div>
                <div className="text-sm text-gray-600">Fresh data every week</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
