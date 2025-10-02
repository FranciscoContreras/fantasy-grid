import { Button } from '../ui/button';

interface HeroProps {
  onGetStarted: () => void;
  onSignIn: () => void;
}

export function Hero({ onGetStarted, onSignIn }: HeroProps) {
  return (
    <div className="relative min-h-screen bg-black text-white overflow-hidden">
      {/* Dynamic grid background */}
      <div className="absolute inset-0 bg-gradient-to-br from-black via-gray-900 to-black">
        <div className="absolute inset-0 opacity-20" style={{
          backgroundImage: 'linear-gradient(rgba(0, 247, 255, 0.1) 1px, transparent 1px), linear-gradient(90deg, rgba(0, 247, 255, 0.1) 1px, transparent 1px)',
          backgroundSize: '50px 50px'
        }}></div>
      </div>

      {/* Glowing orbs */}
      <div className="absolute inset-0 overflow-hidden">
        <div className="absolute top-1/4 -left-48 w-96 h-96 bg-cyan-500 rounded-full mix-blend-screen filter blur-3xl opacity-20 animate-blob"></div>
        <div className="absolute top-1/3 -right-48 w-96 h-96 bg-purple-500 rounded-full mix-blend-screen filter blur-3xl opacity-20 animate-blob animation-delay-2000"></div>
        <div className="absolute -bottom-32 left-1/2 w-96 h-96 bg-blue-500 rounded-full mix-blend-screen filter blur-3xl opacity-20 animate-blob animation-delay-4000"></div>
      </div>

      {/* Navigation */}
      <nav className="relative z-10 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-gradient-to-br from-cyan-400 to-blue-600 rounded-lg"></div>
            <span className="text-2xl font-black tracking-tight">FANTASY GRID</span>
          </div>
          <Button
            variant="ghost"
            onClick={onSignIn}
            className="text-white hover:bg-white/10 font-semibold"
          >
            Sign In
          </Button>
        </div>
      </nav>

      {/* Hero Content */}
      <div className="relative z-10 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20 sm:py-32">
        <div className="max-w-4xl">
          {/* Label */}
          <div className="inline-flex items-center gap-2 px-4 py-2 bg-white/5 backdrop-blur-sm border border-white/10 rounded-full mb-8">
            <div className="w-2 h-2 bg-cyan-400 rounded-full animate-pulse"></div>
            <span className="text-sm font-semibold text-cyan-400 uppercase tracking-wider">
              Powered by Next Gen Stats + AI
            </span>
          </div>

          {/* Main headline */}
          <h1 className="text-5xl sm:text-6xl md:text-7xl lg:text-8xl font-black tracking-tighter mb-8 leading-none">
            DOMINATE
            <br />
            <span className="bg-gradient-to-r from-cyan-400 via-blue-500 to-purple-600 bg-clip-text text-transparent">
              YOUR LEAGUE
            </span>
          </h1>

          {/* Subheadline */}
          <p className="text-xl sm:text-2xl md:text-3xl text-gray-300 font-light mb-12 max-w-2xl leading-relaxed">
            AI-powered start/sit decisions.
            <br />
            Real-time analytics.
            <br />
            <span className="text-white font-semibold">Zero guesswork.</span>
          </p>

          {/* CTA */}
          <div className="flex flex-col sm:flex-row gap-4 mb-16">
            <Button
              size="lg"
              onClick={onGetStarted}
              className="group relative px-8 py-7 bg-white text-black hover:bg-gray-100 text-lg font-bold overflow-hidden transition-all"
            >
              <span className="relative z-10">START WINNING</span>
              <div className="absolute inset-0 bg-gradient-to-r from-cyan-400 to-blue-600 opacity-0 group-hover:opacity-100 transition-opacity"></div>
              <svg className="relative z-10 ml-2 w-5 h-5 group-hover:translate-x-1 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M13 7l5 5m0 0l-5 5m5-5H6" />
              </svg>
            </Button>
            <Button
              size="lg"
              variant="outline"
              onClick={onSignIn}
              className="px-8 py-7 border-2 border-white/20 text-white hover:bg-white/10 text-lg font-bold backdrop-blur-sm"
            >
              WATCH DEMO
            </Button>
          </div>

          {/* Stats */}
          <div className="flex flex-wrap gap-8 text-sm">
            <div>
              <div className="text-3xl font-black text-white mb-1">10K+</div>
              <div className="text-gray-400 uppercase tracking-wider font-semibold">Active Users</div>
            </div>
            <div>
              <div className="text-3xl font-black text-white mb-1">73%</div>
              <div className="text-gray-400 uppercase tracking-wider font-semibold">Win Rate</div>
            </div>
            <div>
              <div className="text-3xl font-black text-white mb-1">4.9★</div>
              <div className="text-gray-400 uppercase tracking-wider font-semibold">Rating</div>
            </div>
          </div>
        </div>

        {/* Preview Cards */}
        <div className="mt-20 grid grid-cols-1 md:grid-cols-3 gap-6 max-w-5xl">
          {/* START Card */}
          <div className="group relative bg-gradient-to-br from-emerald-500/20 to-green-600/20 backdrop-blur-xl border border-emerald-500/30 rounded-2xl p-6 hover:scale-105 transition-transform">
            <div className="absolute inset-0 bg-gradient-to-br from-emerald-500/0 to-green-600/20 opacity-0 group-hover:opacity-100 transition-opacity rounded-2xl"></div>
            <div className="relative">
              <div className="flex items-center justify-between mb-4">
                <div className="w-14 h-14 bg-gradient-to-br from-emerald-400 to-green-600 rounded-xl"></div>
                <div className="text-4xl font-black text-emerald-400">A+</div>
              </div>
              <div className="text-xl font-bold mb-1">P. Mahomes</div>
              <div className="text-sm text-gray-400 mb-4">QB · KANSAS CITY</div>
              <div className="inline-flex items-center gap-2 px-4 py-2 bg-emerald-500/20 border border-emerald-500/50 rounded-full">
                <div className="w-2 h-2 bg-emerald-400 rounded-full"></div>
                <span className="text-sm font-bold text-emerald-400 uppercase tracking-wider">START</span>
              </div>
            </div>
          </div>

          {/* CONSIDER Card */}
          <div className="group relative bg-gradient-to-br from-yellow-500/20 to-orange-600/20 backdrop-blur-xl border border-yellow-500/30 rounded-2xl p-6 hover:scale-105 transition-transform">
            <div className="absolute inset-0 bg-gradient-to-br from-yellow-500/0 to-orange-600/20 opacity-0 group-hover:opacity-100 transition-opacity rounded-2xl"></div>
            <div className="relative">
              <div className="flex items-center justify-between mb-4">
                <div className="w-14 h-14 bg-gradient-to-br from-yellow-400 to-orange-600 rounded-xl"></div>
                <div className="text-4xl font-black text-yellow-400">B+</div>
              </div>
              <div className="text-xl font-bold mb-1">S. Barkley</div>
              <div className="text-sm text-gray-400 mb-4">RB · NEW YORK</div>
              <div className="inline-flex items-center gap-2 px-4 py-2 bg-yellow-500/20 border border-yellow-500/50 rounded-full">
                <div className="w-2 h-2 bg-yellow-400 rounded-full"></div>
                <span className="text-sm font-bold text-yellow-400 uppercase tracking-wider">CONSIDER</span>
              </div>
            </div>
          </div>

          {/* BENCH Card */}
          <div className="group relative bg-gradient-to-br from-red-500/20 to-rose-600/20 backdrop-blur-xl border border-red-500/30 rounded-2xl p-6 hover:scale-105 transition-transform opacity-60">
            <div className="absolute inset-0 bg-gradient-to-br from-red-500/0 to-rose-600/20 opacity-0 group-hover:opacity-100 transition-opacity rounded-2xl"></div>
            <div className="relative">
              <div className="flex items-center justify-between mb-4">
                <div className="w-14 h-14 bg-gradient-to-br from-red-400 to-rose-600 rounded-xl"></div>
                <div className="text-4xl font-black text-red-400">C</div>
              </div>
              <div className="text-xl font-bold mb-1">D. Hopkins</div>
              <div className="text-sm text-gray-400 mb-4">WR · TENNESSEE</div>
              <div className="inline-flex items-center gap-2 px-4 py-2 bg-red-500/20 border border-red-500/50 rounded-full">
                <div className="w-2 h-2 bg-red-400 rounded-full"></div>
                <span className="text-sm font-bold text-red-400 uppercase tracking-wider">BENCH</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Scroll indicator */}
      <div className="absolute bottom-8 left-1/2 -translate-x-1/2 z-10">
        <div className="flex flex-col items-center gap-2 text-gray-400">
          <span className="text-xs uppercase tracking-wider font-semibold">Scroll</span>
          <svg className="w-6 h-6 animate-bounce" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 14l-7 7m0 0l-7-7m7 7V3" />
          </svg>
        </div>
      </div>
    </div>
  );
}
