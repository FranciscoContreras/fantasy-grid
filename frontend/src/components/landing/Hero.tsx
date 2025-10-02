import { Button } from '../ui/button';

interface HeroProps {
  onGetStarted: () => void;
  onSignIn: () => void;
}

export function Hero({ onGetStarted, onSignIn }: HeroProps) {
  return (
    <div className="relative overflow-hidden bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50">
      {/* Decorative background */}
      <div className="absolute inset-0 overflow-hidden">
        <div className="absolute -top-40 -right-40 w-80 h-80 bg-blue-400 rounded-full mix-blend-multiply filter blur-xl opacity-20 animate-blob"></div>
        <div className="absolute -bottom-40 -left-40 w-80 h-80 bg-purple-400 rounded-full mix-blend-multiply filter blur-xl opacity-20 animate-blob animation-delay-2000"></div>
        <div className="absolute top-40 left-40 w-80 h-80 bg-indigo-400 rounded-full mix-blend-multiply filter blur-xl opacity-20 animate-blob animation-delay-4000"></div>
      </div>

      <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16 sm:py-24 lg:py-32">
        <div className="text-center space-y-8">
          {/* Badge */}
          <div className="inline-flex items-center gap-2 px-4 py-2 bg-white rounded-full shadow-sm border border-gray-200">
            <span className="text-2xl">🏈</span>
            <span className="text-sm font-semibold text-gray-900">
              Powered by NFL Next Gen Stats & AI
            </span>
          </div>

          {/* Headline */}
          <h1 className="text-4xl sm:text-5xl md:text-6xl lg:text-7xl font-extrabold text-gray-900 tracking-tight">
            Win Your Fantasy Week
            <br />
            <span className="bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent">
              with AI-Powered
            </span>
            <br />
            Start/Sit Decisions
          </h1>

          {/* Subheadline */}
          <p className="max-w-3xl mx-auto text-lg sm:text-xl md:text-2xl text-gray-600 leading-relaxed">
            Stop guessing. Get data-driven recommendations for every player, every week.
            <br className="hidden sm:block" />
            Backed by <span className="font-semibold text-gray-900">20+ analytics</span> including
            matchups, weather, injuries, and Next Gen Stats.
          </p>

          {/* CTAs */}
          <div className="flex flex-col sm:flex-row gap-4 justify-center items-center pt-4">
            <Button
              size="lg"
              onClick={onGetStarted}
              className="w-full sm:w-auto text-lg px-8 py-6 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 shadow-lg hover:shadow-xl transform hover:scale-105 transition-all"
            >
              Get Started Free
              <svg className="ml-2 w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
              </svg>
            </Button>
            <Button
              size="lg"
              variant="outline"
              onClick={onSignIn}
              className="w-full sm:w-auto text-lg px-8 py-6 border-2 hover:bg-gray-50"
            >
              Sign In
            </Button>
          </div>

          {/* Social Proof */}
          <div className="pt-8 flex flex-col sm:flex-row gap-6 sm:gap-12 justify-center items-center text-sm text-gray-600">
            <div className="flex items-center gap-2">
              <div className="flex -space-x-2">
                <div className="w-8 h-8 rounded-full bg-blue-500 border-2 border-white"></div>
                <div className="w-8 h-8 rounded-full bg-indigo-500 border-2 border-white"></div>
                <div className="w-8 h-8 rounded-full bg-purple-500 border-2 border-white"></div>
              </div>
              <span className="font-semibold text-gray-900">10,000+</span> fantasy managers
            </div>
            <div className="flex items-center gap-2">
              <span className="text-2xl">⭐</span>
              <span className="font-semibold text-gray-900">4.9/5</span> average rating
            </div>
            <div className="flex items-center gap-2">
              <span className="text-2xl">🏆</span>
              <span className="font-semibold text-gray-900">73%</span> win rate
            </div>
          </div>
        </div>

        {/* Screenshot Preview */}
        <div className="mt-16 relative">
          <div className="relative mx-auto max-w-5xl">
            {/* Glow effect */}
            <div className="absolute inset-0 bg-gradient-to-r from-blue-600 to-indigo-600 blur-3xl opacity-20"></div>

            {/* Screenshot placeholder */}
            <div className="relative bg-white rounded-2xl shadow-2xl border border-gray-200 overflow-hidden">
              <div className="bg-gradient-to-br from-gray-50 to-gray-100 p-8 sm:p-12">
                {/* Browser bar */}
                <div className="flex items-center gap-2 mb-6 pb-4 border-b border-gray-300">
                  <div className="flex gap-2">
                    <div className="w-3 h-3 rounded-full bg-red-500"></div>
                    <div className="w-3 h-3 rounded-full bg-yellow-500"></div>
                    <div className="w-3 h-3 rounded-full bg-green-500"></div>
                  </div>
                  <div className="flex-1 text-center text-sm text-gray-500 font-mono">
                    fantasy-grid.com
                  </div>
                </div>

                {/* Content preview */}
                <div className="space-y-6">
                  <div className="flex items-center justify-between">
                    <div className="text-2xl font-bold text-gray-900">Week 5 Lineup</div>
                    <div className="px-4 py-2 bg-green-100 text-green-800 rounded-lg font-semibold">
                      87% Confidence
                    </div>
                  </div>

                  <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
                    {/* START card */}
                    <div className="bg-white rounded-lg p-4 shadow-md border-2 border-green-500">
                      <div className="flex items-center gap-3 mb-3">
                        <div className="w-12 h-12 rounded-full bg-gradient-to-br from-blue-600 to-indigo-600"></div>
                        <div>
                          <div className="font-semibold text-gray-900">P. Mahomes</div>
                          <div className="text-sm text-gray-500">QB · KC</div>
                        </div>
                        <div className="ml-auto text-2xl font-bold text-green-600">A+</div>
                      </div>
                      <div className="inline-flex items-center gap-2 px-3 py-1 bg-green-100 text-green-800 rounded-full text-sm font-semibold">
                        ✓ START
                      </div>
                    </div>

                    {/* CONSIDER card */}
                    <div className="bg-white rounded-lg p-4 shadow-md border-2 border-yellow-500">
                      <div className="flex items-center gap-3 mb-3">
                        <div className="w-12 h-12 rounded-full bg-gradient-to-br from-purple-600 to-pink-600"></div>
                        <div>
                          <div className="font-semibold text-gray-900">S. Barkley</div>
                          <div className="text-sm text-gray-500">RB · NYG</div>
                        </div>
                        <div className="ml-auto text-2xl font-bold text-yellow-600">B+</div>
                      </div>
                      <div className="inline-flex items-center gap-2 px-3 py-1 bg-yellow-100 text-yellow-800 rounded-full text-sm font-semibold">
                        ⚠ CONSIDER
                      </div>
                    </div>

                    {/* BENCH card */}
                    <div className="bg-white rounded-lg p-4 shadow-md border-2 border-red-500 opacity-75">
                      <div className="flex items-center gap-3 mb-3">
                        <div className="w-12 h-12 rounded-full bg-gradient-to-br from-red-600 to-orange-600"></div>
                        <div>
                          <div className="font-semibold text-gray-900">D. Hopkins</div>
                          <div className="text-sm text-gray-500">WR · TEN</div>
                        </div>
                        <div className="ml-auto text-2xl font-bold text-red-600">C</div>
                      </div>
                      <div className="inline-flex items-center gap-2 px-3 py-1 bg-red-100 text-red-800 rounded-full text-sm font-semibold">
                        ✕ BENCH
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
