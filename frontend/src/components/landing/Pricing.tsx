import { Button } from '../ui/button';
import { Card, CardContent } from '../ui/card';

interface PricingProps {
  onGetStarted: () => void;
}

const plans = [
  {
    name: 'Free',
    price: '$0',
    period: '/season',
    description: 'Perfect for casual fantasy players',
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
    cta: 'Start Free Now',
    popular: false,
    color: 'from-gray-600 to-gray-700',
  },
  {
    name: 'Pro',
    price: '$19',
    period: '/season',
    description: 'For serious players who want every edge',
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
    cta: 'Upgrade to Pro',
    popular: true,
    color: 'from-blue-600 to-indigo-600',
  },
];

export function Pricing({ onGetStarted }: PricingProps) {
  return (
    <div className="py-16 sm:py-24 bg-gradient-to-br from-gray-50 to-gray-100">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Section Header */}
        <div className="text-center max-w-3xl mx-auto mb-16">
          <h2 className="text-3xl sm:text-4xl lg:text-5xl font-extrabold text-gray-900 mb-4">
            Simple, Transparent Pricing
          </h2>
          <p className="text-lg sm:text-xl text-gray-600">
            Start free and upgrade anytime. No credit card required.
          </p>
        </div>

        {/* Pricing Cards */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 max-w-5xl mx-auto">
          {plans.map((plan, index) => (
            <Card
              key={index}
              className={`relative overflow-hidden ${
                plan.popular
                  ? 'border-4 border-blue-500 shadow-2xl transform lg:scale-105'
                  : 'border-2 border-gray-200 shadow-lg'
              }`}
            >
              {/* Popular Badge */}
              {plan.popular && (
                <div className="absolute top-0 right-0">
                  <div className="bg-gradient-to-r from-blue-600 to-indigo-600 text-white px-6 py-2 text-sm font-bold uppercase tracking-wide transform rotate-45 translate-x-8 translate-y-4">
                    Most Popular
                  </div>
                </div>
              )}

              <CardContent className="p-8 sm:p-10">
                {/* Plan Name */}
                <div className="mb-6">
                  <h3 className="text-2xl font-bold text-gray-900 mb-2">{plan.name}</h3>
                  <p className="text-gray-600">{plan.description}</p>
                </div>

                {/* Price */}
                <div className="mb-8">
                  <div className="flex items-baseline gap-1">
                    <span className={`text-5xl font-extrabold bg-gradient-to-r ${plan.color} bg-clip-text text-transparent`}>
                      {plan.price}
                    </span>
                    <span className="text-xl text-gray-600">{plan.period}</span>
                  </div>
                  <p className="text-sm text-gray-500 mt-2">
                    {plan.name === 'Free' ? 'No credit card required' : 'One-time payment per season'}
                  </p>
                </div>

                {/* CTA Button */}
                <Button
                  size="lg"
                  onClick={onGetStarted}
                  className={`w-full mb-8 text-lg py-6 ${
                    plan.popular
                      ? `bg-gradient-to-r ${plan.color} hover:opacity-90 shadow-lg hover:shadow-xl`
                      : 'bg-gray-900 hover:bg-gray-800'
                  } transform hover:scale-105 transition-all`}
                >
                  {plan.cta}
                  <svg className="ml-2 w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
                  </svg>
                </Button>

                {/* Features */}
                <div className="space-y-4">
                  <div className="text-sm font-semibold text-gray-900 uppercase tracking-wide">
                    What's Included:
                  </div>
                  {plan.features.map((feature, idx) => (
                    <div key={idx} className="flex items-start gap-3">
                      <svg
                        className={`w-6 h-6 flex-shrink-0 ${
                          plan.popular ? 'text-blue-600' : 'text-green-600'
                        }`}
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
                        className={`text-gray-700 ${
                          feature.includes('Everything in') ? 'font-semibold text-gray-900' : ''
                        }`}
                      >
                        {feature}
                      </span>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          ))}
        </div>

        {/* FAQ */}
        <div className="mt-16 max-w-3xl mx-auto">
          <div className="text-center mb-8">
            <h3 className="text-2xl font-bold text-gray-900 mb-2">Frequently Asked Questions</h3>
          </div>

          <div className="space-y-4">
            <details className="bg-white rounded-lg p-6 shadow-sm border border-gray-200 cursor-pointer hover:shadow-md transition-shadow">
              <summary className="font-semibold text-gray-900 text-lg">
                Is the Free plan really free?
              </summary>
              <p className="mt-3 text-gray-600">
                Yes! No credit card required, no hidden fees. You get full access to start/sit
                recommendations, AI grading, and all core features. Upgrade to Pro only if you want
                advanced analytics and unlimited rosters.
              </p>
            </details>

            <details className="bg-white rounded-lg p-6 shadow-sm border border-gray-200 cursor-pointer hover:shadow-md transition-shadow">
              <summary className="font-semibold text-gray-900 text-lg">
                Can I cancel anytime?
              </summary>
              <p className="mt-3 text-gray-600">
                Pro is a one-time payment per season (not a subscription). If you're not satisfied,
                contact support within 7 days for a full refund. No questions asked.
              </p>
            </details>

            <details className="bg-white rounded-lg p-6 shadow-sm border border-gray-200 cursor-pointer hover:shadow-md transition-shadow">
              <summary className="font-semibold text-gray-900 text-lg">
                How accurate are the recommendations?
              </summary>
              <p className="mt-3 text-gray-600">
                Our AI models analyze 20+ data points including matchups, weather, injuries, and Next
                Gen Stats. Users report a 73% win rate when following START recommendations. However,
                fantasy football always has unpredictability - no tool can guarantee wins.
              </p>
            </details>

            <details className="bg-white rounded-lg p-6 shadow-sm border border-gray-200 cursor-pointer hover:shadow-md transition-shadow">
              <summary className="font-semibold text-gray-900 text-lg">
                What league formats do you support?
              </summary>
              <p className="mt-3 text-gray-600">
                We support PPR (Point Per Reception), Half-PPR, and Standard scoring formats. You can
                set your league format when creating your roster, and recommendations will be tailored
                accordingly.
              </p>
            </details>
          </div>
        </div>

        {/* Final CTA */}
        <div className="mt-16 text-center bg-gradient-to-br from-blue-600 to-indigo-600 rounded-3xl p-12 sm:p-16">
          <h3 className="text-3xl sm:text-4xl font-extrabold text-white mb-4">
            Ready to Dominate Your League?
          </h3>
          <p className="text-xl text-blue-100 mb-8 max-w-2xl mx-auto">
            Join thousands of fantasy managers making smarter lineup decisions every week.
            Start free today - no credit card required.
          </p>
          <Button
            size="lg"
            onClick={onGetStarted}
            className="bg-white text-blue-600 hover:bg-gray-100 text-lg px-12 py-6 shadow-xl hover:shadow-2xl transform hover:scale-105 transition-all font-bold"
          >
            Get Started Free
            <svg className="ml-2 w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
            </svg>
          </Button>
          <p className="text-blue-100 text-sm mt-4">Start analyzing your roster in under 3 minutes</p>
        </div>
      </div>
    </div>
  );
}
