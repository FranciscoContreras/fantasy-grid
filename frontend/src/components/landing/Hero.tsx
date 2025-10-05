import { Button } from '../ui/button';
import PilonLogo from '../../assets/logo.svg';

interface HeroProps {
  onGetStarted: () => void;
  onSignIn: () => void;
}

export function Hero({ onGetStarted, onSignIn }: HeroProps) {
  return (
    <div className="relative min-h-screen bg-black text-white overflow-hidden font-body">
      {/* Geometric Background Pattern */}
      <div className="absolute inset-0">
        <div className="absolute top-0 right-0 w-1/3 h-full bg-gradient-to-l from-gray-900 to-transparent opacity-50"></div>
        <div className="absolute bottom-0 left-0 w-96 h-96 border-l-4 border-b-4 border-white opacity-10"></div>
        <div className="absolute top-20 right-20 w-32 h-32 border-2 border-white opacity-5 rotate-45"></div>
      </div>

      {/* Navigation */}
      <nav className="relative z-10 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="flex items-center justify-between">
          <div className="flex items-center">
            <img src={PilonLogo} alt="Pilon" className="w-20 h-14 object-contain invert" />
          </div>
          <Button
            variant="outline"
            onClick={onSignIn}
            className="border-white text-white hover:bg-white hover:text-black font-semibold tracking-wider uppercase text-sm px-8 py-3"
          >
            Sign In
          </Button>
        </div>
      </nav>

      {/* Hero Content */}
      <div className="relative z-10 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12 sm:py-20">
        <div className="max-w-5xl">
          {/* Vintage Athletic Badge */}
          <div className="inline-flex items-center gap-2 px-6 py-3 border-2 border-white bg-transparent mb-12">
            <div className="w-3 h-3 bg-white"></div>
            <span className="text-sm font-bold text-white uppercase tracking-[0.2em] font-display">
              Est. 2024 • NFL Analytics
            </span>
            <div className="w-3 h-3 bg-white"></div>
          </div>

          {/* Main Script Headline */}
          <h1 className="font-script text-7xl sm:text-8xl md:text-9xl lg:text-[12rem] leading-none mb-6 text-white">
            Dominate
          </h1>

          {/* Secondary Bold Text */}
          <div className="mb-12">
            <h2 className="font-display text-4xl sm:text-5xl md:text-6xl lg:text-7xl uppercase tracking-tighter text-white mb-4">
              YOUR LEAGUE
            </h2>
            <div className="w-32 h-1 bg-white mb-8"></div>
          </div>

          {/* Subheadline */}
          <p className="text-xl sm:text-2xl md:text-3xl text-gray-300 font-light mb-16 max-w-3xl leading-relaxed">
            AI-powered start/sit decisions.
            <br />
            Real-time analytics.
            <br />
            <span className="text-white font-semibold">Zero guesswork.</span>
          </p>

          {/* Neo-Vintage CTA Buttons */}
          <div className="flex flex-col sm:flex-row gap-6 mb-20">
            <Button
              size="lg"
              onClick={onGetStarted}
              className="px-12 py-6 bg-white text-black hover:bg-gray-100 text-lg font-display uppercase tracking-wider border-4 border-white transition-all hover:scale-105"
            >
              START WINNING
            </Button>
            <Button
              size="lg"
              variant="outline"
              onClick={onSignIn}
              className="px-12 py-6 border-4 border-white text-white hover:bg-white hover:text-black text-lg font-display uppercase tracking-wider transition-all hover:scale-105"
            >
              WATCH DEMO
            </Button>
          </div>

          {/* Vintage Athletic Stats */}
          <div className="flex flex-wrap gap-16 text-sm border-t-4 border-white pt-12">
            <div className="text-center">
              <div className="text-5xl font-display text-white mb-2">10K+</div>
              <div className="text-gray-300 uppercase tracking-[0.2em] font-bold text-sm">Champions</div>
            </div>
            <div className="text-center">
              <div className="text-5xl font-display text-white mb-2">73%</div>
              <div className="text-gray-300 uppercase tracking-[0.2em] font-bold text-sm">Win Rate</div>
            </div>
            <div className="text-center">
              <div className="text-5xl font-display text-white mb-2">4.9★</div>
              <div className="text-gray-300 uppercase tracking-[0.2em] font-bold text-sm">Rating</div>
            </div>
          </div>
        </div>

        {/* Neo-Vintage Preview Cards */}
        <div className="mt-32 grid grid-cols-1 md:grid-cols-3 gap-8 max-w-6xl">
          {/* START Card - Championship Gold */}
          <div className="group relative bg-white text-black border-4 border-black p-8 hover:scale-105 transition-all hover:shadow-2xl">
            <div className="absolute top-4 right-4 w-12 h-12 bg-black text-white flex items-center justify-center font-display text-xl font-bold">
              A+
            </div>
            <div className="w-20 h-20 bg-black mb-6"></div>
            <div className="text-3xl font-display mb-2 uppercase tracking-tight">P. MAHOMES</div>
            <div className="text-sm text-gray-600 mb-6 uppercase tracking-[0.3em] font-bold">QB · KANSAS CITY</div>
            <div className="inline-flex items-center gap-2 px-6 py-3 bg-black text-white font-display uppercase tracking-[0.2em] text-sm font-bold border-2 border-black">
              START
            </div>
          </div>

          {/* CONSIDER Card - Silver */}
          <div className="group relative bg-gray-800 text-white border-4 border-gray-600 p-8 hover:scale-105 transition-all hover:shadow-2xl">
            <div className="absolute top-4 right-4 w-12 h-12 bg-gray-600 text-white flex items-center justify-center font-display text-xl font-bold">
              B+
            </div>
            <div className="w-20 h-20 bg-gray-600 mb-6"></div>
            <div className="text-3xl font-display mb-2 uppercase tracking-tight">S. BARKLEY</div>
            <div className="text-sm text-gray-400 mb-6 uppercase tracking-[0.3em] font-bold">RB · NEW YORK</div>
            <div className="inline-flex items-center gap-2 px-6 py-3 bg-gray-600 text-white font-display uppercase tracking-[0.2em] text-sm font-bold border-2 border-gray-600">
              CONSIDER
            </div>
          </div>

          {/* BENCH Card - Bronze */}
          <div className="group relative bg-gray-200 text-gray-700 border-4 border-gray-400 p-8 hover:scale-105 transition-all hover:shadow-2xl opacity-80">
            <div className="absolute top-4 right-4 w-12 h-12 bg-gray-400 text-white flex items-center justify-center font-display text-xl font-bold">
              C
            </div>
            <div className="w-20 h-20 bg-gray-400 mb-6"></div>
            <div className="text-3xl font-display mb-2 uppercase tracking-tight">D. HOPKINS</div>
            <div className="text-sm text-gray-500 mb-6 uppercase tracking-[0.3em] font-bold">WR · TENNESSEE</div>
            <div className="inline-flex items-center gap-2 px-6 py-3 bg-gray-400 text-white font-display uppercase tracking-[0.2em] text-sm font-bold border-2 border-gray-400">
              BENCH
            </div>
          </div>
        </div>
      </div>

      {/* Neo-Vintage Scroll Indicator */}
      <div className="absolute bottom-12 left-1/2 -translate-x-1/2 z-10">
        <div className="flex flex-col items-center gap-4 text-white">
          <div className="w-px h-16 bg-white opacity-50"></div>
          <span className="text-sm uppercase tracking-[0.3em] font-bold font-display">EXPLORE</span>
          <svg className="w-8 h-8 animate-bounce" fill="currentColor" viewBox="0 0 24 24">
            <path d="M12 2L12 20M5 13L12 20L19 13" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round" fill="none"/>
          </svg>
        </div>
      </div>
    </div>
  );
}
