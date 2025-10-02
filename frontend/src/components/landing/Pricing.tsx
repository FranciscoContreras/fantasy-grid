import { Button } from '../ui/button';

interface PricingProps {
  onGetStarted: () => void;
}

const plans = [
  {
    name: 'FREE',
    price: '$0',
    description: 'For casual players',
    features: [
      'Unlimited start/sit recommendations',
      'AI player grading (A+ to F)',
      'Weather impact analysis',
      'Injury tracking & alerts',
      'Defense matchup ratings',
      'Up to 2 rosters',
      'Weekly lineup analysis',
      'Email support',
    ],
    cta: 'START FREE',
    popular: false,
  },
  {
    name: 'PRO',
    price: '$19',
    description: 'For champions',
    features: [
      'Everything in Free, plus:',
      'Next Gen Stats & EPA analysis',
      'Advanced matchup scoring',
      'Trade analyzer & suggestions',
      'Waiver wire recommendations',
      'Player comparison tool',
      'Unlimited rosters',
      'Historical trend analysis',
      'Priority support',
      'Early access to new features',
    ],
    cta: 'GO PRO',
    popular: true,
  },
];

export function Pricing({ onGetStarted }: PricingProps) {
  return (
    <div className="relative py-24 sm:py-32 bg-white text-black overflow-hidden">
      <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Section Header */}
        <div className="text-center max-w-3xl mx-auto mb-20">
          <div className="inline-flex items-center gap-2 px-4 py-2 bg-gray-100 rounded-full mb-6">
            <span className="text-xs font-bold text-gray-900 uppercase tracking-wider">
              Simple Pricing
            </span>
          </div>
          <h2 className="text-5xl sm:text-6xl md:text-7xl lg:text-8xl font-black tracking-tighter mb-6 leading-none">
            CHOOSE
            <br />
            YOUR PLAN
          </h2>
          <p className="text-xl sm:text-2xl text-gray-600 font-light">
            Start free. Upgrade anytime. No credit card required.
          </p>
        </div>

        {/* Pricing Cards */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 max-w-5xl mx-auto mb-20">
          {plans.map((plan, index) => (
            <div
              key={index}
              className={`relative ${
                plan.popular ? 'lg:scale-105' : ''
              }`}
            >
              {/* Popular Badge */}
              {plan.popular && (
                <div className="absolute -top-4 left-1/2 -translate-x-1/2 z-10">
                  <div className="bg-black text-white px-6 py-2 rounded-full text-xs font-black uppercase tracking-wider">
                    Most Popular
                  </div>
                </div>
              )}

              <div className={`relative bg-gray-50 border ${
                plan.popular ? 'border-black' : 'border-gray-200'
              } rounded-3xl p-8 sm:p-10 hover:bg-gray-100 transition-all`}>
                {/* Plan Name & Description */}
                <div className="mb-8">
                  <h3 className="text-4xl font-black mb-2 tracking-tight">{plan.name}</h3>
                  <p className="text-gray-600 uppercase tracking-wider text-sm font-semibold">{plan.description}</p>
                </div>

                {/* Price */}
                <div className="mb-8">
                  <div className="flex items-baseline gap-2">
                    <span className="text-6xl sm:text-7xl font-black text-black">
                      {plan.price}
                    </span>
                    <span className="text-xl text-gray-600 font-semibold">/SEASON</span>
                  </div>
                  <p className="text-sm text-gray-500 mt-3 uppercase tracking-wider font-semibold">
                    {plan.name === 'FREE' ? 'No credit card required' : 'One-time payment'}
                  </p>
                </div>

                {/* CTA Button */}
                <Button
                  size="lg"
                  onClick={onGetStarted}
                  className={`w-full mb-10 text-lg py-7 font-black tracking-tight ${
                    plan.popular
                      ? 'bg-black text-white hover:bg-gray-900'
                      : 'bg-white border-2 border-black text-black hover:bg-gray-50'
                  } transform hover:scale-105 transition-all`}
                >
                  {plan.cta}
                  <svg className="ml-2 w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M13 7l5 5m0 0l-5 5m5-5H6" />
                  </svg>
                </Button>

                {/* Features */}
                <div className="space-y-4">
                  <div className="text-xs font-black text-gray-600 uppercase tracking-wider mb-6">
                    What's Included:
                  </div>
                  {plan.features.map((feature, idx) => (
                    <div key={idx} className="flex items-start gap-3">
                      <svg
                        className="w-6 h-6 flex-shrink-0 text-black"
                        fill="none"
                        stroke="currentColor"
                        viewBox="0 0 24 24"
                      >
                        <path
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          strokeWidth={2}
                          d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
                        />
                      </svg>
                      <span
                        className={`text-gray-700 text-sm ${
                          feature.includes('Everything in') ? 'font-bold text-black' : ''
                        }`}
                      >
                        {feature}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* FAQ */}
        <div className="max-w-3xl mx-auto mb-20">
          <div className="text-center mb-12">
            <h3 className="text-3xl sm:text-4xl font-black mb-2 tracking-tight">FAQ</h3>
            <p className="text-gray-600">Common questions answered</p>
          </div>

          <div className="space-y-4">
            <details className="bg-gray-50 border border-gray-200 rounded-2xl p-6 cursor-pointer hover:bg-gray-100 transition-all group">
              <summary className="font-black text-black text-lg tracking-tight">
                Is the Free plan really free?
              </summary>
              <p className="mt-4 text-gray-600 leading-relaxed">
                Yes! No credit card required, no hidden fees. You get full access to start/sit
                recommendations, AI grading, and all core features. Upgrade to Pro only if you want
                advanced analytics and unlimited rosters.
              </p>
            </details>

            <details className="bg-gray-50 border border-gray-200 rounded-2xl p-6 cursor-pointer hover:bg-gray-100 transition-all group">
              <summary className="font-black text-black text-lg tracking-tight">
                Can I cancel anytime?
              </summary>
              <p className="mt-4 text-gray-600 leading-relaxed">
                Pro is a one-time payment per season (not a subscription). If you're not satisfied,
                contact support within 7 days for a full refund. No questions asked.
              </p>
            </details>

            <details className="bg-gray-50 border border-gray-200 rounded-2xl p-6 cursor-pointer hover:bg-gray-100 transition-all group">
              <summary className="font-black text-black text-lg tracking-tight">
                How accurate are the recommendations?
              </summary>
              <p className="mt-4 text-gray-600 leading-relaxed">
                Our AI models analyze 20+ data points including matchups, weather, injuries, and Next
                Gen Stats. Users report a 73% win rate when following START recommendations. However,
                fantasy football always has unpredictability - no tool can guarantee wins.
              </p>
            </details>

            <details className="bg-gray-50 border border-gray-200 rounded-2xl p-6 cursor-pointer hover:bg-gray-100 transition-all group">
              <summary className="font-black text-black text-lg tracking-tight">
                What league formats do you support?
              </summary>
              <p className="mt-4 text-gray-600 leading-relaxed">
                We support PPR (Point Per Reception), Half-PPR, and Standard scoring formats. You can
                set your league format when creating your roster, and recommendations will be tailored
                accordingly.
              </p>
            </details>
          </div>
        </div>

        {/* Final CTA */}
        <div className="relative">
          <div className="relative bg-black text-white rounded-3xl p-12 sm:p-16 text-center">
            <h3 className="text-4xl sm:text-5xl font-black mb-6 tracking-tight">
              READY TO
              <br />
              DOMINATE?
            </h3>
            <p className="text-xl text-gray-300 mb-10 max-w-2xl mx-auto leading-relaxed">
              Join thousands of fantasy managers making smarter lineup decisions every week.
              Start free today - no credit card required.
            </p>
            <Button
              size="lg"
              onClick={onGetStarted}
              className="bg-white text-black hover:bg-gray-100 text-lg font-black px-12 py-7 hover:scale-105 transition-all tracking-tight"
            >
              START WINNING NOW
              <svg className="ml-2 w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M13 7l5 5m0 0l-5 5m5-5H6" />
              </svg>
            </Button>
            <p className="text-gray-400 text-sm mt-6 uppercase tracking-wider font-semibold">
              Setup in under 3 minutes
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
