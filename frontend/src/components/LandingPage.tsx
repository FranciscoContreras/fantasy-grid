import { Hero } from './landing/Hero';
import { Features } from './landing/Features';
import { HowItWorks } from './landing/HowItWorks';
import PilonLogo from '../assets/logo.svg';

interface LandingPageProps {
  onGetStarted: () => void;
  onSignIn: () => void;
}

export function LandingPage({ onGetStarted, onSignIn }: LandingPageProps) {
  return (
    <div className="min-h-screen bg-gray-50">
      {/* Hero Section */}
      <Hero onGetStarted={onGetStarted} onSignIn={onSignIn} />

      {/* Features Section */}
      <Features />

      {/* How It Works Section */}
      <HowItWorks />

      {/* Final CTA Section */}
      <div className="relative py-24 sm:py-32 bg-white">
        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <div className="max-w-3xl mx-auto">
            <h3 className="text-4xl sm:text-5xl font-black mb-6 tracking-tight text-gray-900">
              READY TO DOMINATE YOUR LEAGUE?
            </h3>
            <p className="text-xl text-gray-600 mb-10 leading-relaxed">
              Join thousands of fantasy managers making smarter lineup decisions every week.
              Get started today - it's completely free.
            </p>
            <button
              onClick={onGetStarted}
              className="bg-gray-900 text-white hover:bg-gray-800 text-lg font-black px-12 py-4 rounded-xl hover:scale-105 transition-all shadow-sm inline-flex items-center gap-3"
            >
              START WINNING NOW
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M13 7l5 5m0 0l-5 5m5-5H6" />
              </svg>
            </button>
            <p className="text-gray-500 text-sm mt-6 font-medium">
              Setup in under 3 minutes • No credit card required
            </p>
          </div>
        </div>
      </div>

      {/* Footer */}
      <footer className="relative bg-white text-gray-600 py-16 border-t border-gray-200">
        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-12 mb-12">
            {/* Brand */}
            <div className="col-span-1 md:col-span-2">
              <div className="flex items-center mb-6">
                <img src={PilonLogo} alt="Pilon" className="w-16 h-12 object-contain" />
              </div>
              <p className="text-gray-600 mb-6 max-w-md leading-relaxed">
                AI-powered fantasy football analysis. Make smarter lineup decisions every week.
              </p>
              <div className="flex gap-3">
                <a
                  href="https://twitter.com"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="w-10 h-10 rounded-lg bg-gray-100 hover:bg-gray-200 border border-gray-200 hover:border-gray-300 flex items-center justify-center transition-all"
                >
                  <svg className="w-5 h-5 text-gray-600" fill="currentColor" viewBox="0 0 24 24">
                    <path d="M23 3a10.9 10.9 0 01-3.14 1.53 4.48 4.48 0 00-7.86 3v1A10.66 10.66 0 013 4s-4 9 5 13a11.64 11.64 0 01-7 2c9 5 20 0 20-11.5a4.5 4.5 0 00-.08-.83A7.72 7.72 0 0023 3z" />
                  </svg>
                </a>
                <a
                  href="https://facebook.com"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="w-10 h-10 rounded-lg bg-gray-100 hover:bg-gray-200 border border-gray-200 hover:border-gray-300 flex items-center justify-center transition-all"
                >
                  <svg className="w-5 h-5 text-gray-600" fill="currentColor" viewBox="0 0 24 24">
                    <path d="M18 2h-3a5 5 0 00-5 5v3H7v4h3v8h4v-8h3l1-4h-4V7a1 1 0 011-1h3z" />
                  </svg>
                </a>
                <a
                  href="https://reddit.com"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="w-10 h-10 rounded-lg bg-gray-100 hover:bg-gray-200 border border-gray-200 hover:border-gray-300 flex items-center justify-center transition-all"
                >
                  <svg className="w-5 h-5 text-gray-600" fill="currentColor" viewBox="0 0 24 24">
                    <path d="M12 0A12 12 0 0 0 0 12a12 12 0 0 0 12 12 12 12 0 0 0 12-12A12 12 0 0 0 12 0zm5.01 4.744c.688 0 1.25.561 1.25 1.249a1.25 1.25 0 0 1-2.498.056l-2.597-.547-.8 3.747c1.824.07 3.48.632 4.674 1.488.308-.309.73-.491 1.207-.491.968 0 1.754.786 1.754 1.754 0 .716-.435 1.333-1.01 1.614a3.111 3.111 0 0 1 .042.52c0 2.694-3.13 4.87-7.004 4.87-3.874 0-7.004-2.176-7.004-4.87 0-.183.015-.366.043-.534A1.748 1.748 0 0 1 4.028 12c0-.968.786-1.754 1.754-1.754.463 0 .898.196 1.207.49 1.207-.883 2.878-1.43 4.744-1.487l.885-4.182a.342.342 0 0 1 .14-.197.35.35 0 0 1 .238-.042l2.906.617a1.214 1.214 0 0 1 1.108-.701zM9.25 12C8.561 12 8 12.562 8 13.25c0 .687.561 1.248 1.25 1.248.687 0 1.248-.561 1.248-1.249 0-.688-.561-1.249-1.249-1.249zm5.5 0c-.687 0-1.248.561-1.248 1.25 0 .687.561 1.248 1.249 1.248.688 0 1.249-.561 1.249-1.249 0-.687-.562-1.249-1.25-1.249zm-5.466 3.99a.327.327 0 0 0-.231.094.33.33 0 0 0 0 .463c.842.842 2.484.913 2.961.913.477 0 2.105-.056 2.961-.913a.361.361 0 0 0 .029-.463.33.33 0 0 0-.464 0c-.547.533-1.684.73-2.512.73-.828 0-1.979-.196-2.512-.73a.326.326 0 0 0-.232-.095z" />
                  </svg>
                </a>
              </div>
            </div>

            {/* Product */}
            <div>
              <h4 className="text-gray-900 font-semibold mb-4 text-sm">Product</h4>
              <ul className="space-y-3">
                <li>
                  <a href="#features" className="hover:text-gray-900 transition-colors text-sm text-gray-600">
                    Features
                  </a>
                </li>
                <li>
                  <a href="#pricing" className="hover:text-gray-900 transition-colors text-sm text-gray-600">
                    Pricing
                  </a>
                </li>
                <li>
                  <a href="#how-it-works" className="hover:text-gray-900 transition-colors text-sm text-gray-600">
                    How It Works
                  </a>
                </li>
                <li>
                  <a href="#testimonials" className="hover:text-gray-900 transition-colors text-sm text-gray-600">
                    Testimonials
                  </a>
                </li>
              </ul>
            </div>

            {/* Company */}
            <div>
              <h4 className="text-gray-900 font-semibold mb-4 text-sm">Company</h4>
              <ul className="space-y-3">
                <li>
                  <a href="#about" className="hover:text-gray-900 transition-colors text-sm text-gray-600">
                    About Us
                  </a>
                </li>
                <li>
                  <a href="#blog" className="hover:text-gray-900 transition-colors text-sm text-gray-600">
                    Blog
                  </a>
                </li>
                <li>
                  <a href="#contact" className="hover:text-gray-900 transition-colors text-sm text-gray-600">
                    Contact
                  </a>
                </li>
                <li>
                  <a href="#careers" className="hover:text-gray-900 transition-colors text-sm text-gray-600">
                    Careers
                  </a>
                </li>
              </ul>
            </div>
          </div>

          {/* Bottom Bar */}
          <div className="pt-8 border-t border-gray-200 flex flex-col sm:flex-row justify-between items-center gap-4">
            <p className="text-sm text-gray-500 font-medium">
              © 2025 Fantasy Grid. All Rights Reserved.
            </p>
            <div className="flex gap-8 text-sm">
              <a href="#privacy" className="hover:text-gray-900 transition-colors text-gray-600">
                Privacy
              </a>
              <a href="#terms" className="hover:text-gray-900 transition-colors text-gray-600">
                Terms
              </a>
              <a href="#cookies" className="hover:text-gray-900 transition-colors text-gray-600">
                Cookies
              </a>
            </div>
          </div>

          {/* API Credit */}
          <div className="mt-8 pt-8 border-t border-gray-200 text-center text-sm">
            <p className="text-gray-500">
              Powered by{' '}
              <a
                href="https://nfl.wearemachina.com"
                target="_blank"
                rel="noopener noreferrer"
                className="text-gray-900 hover:text-gray-700 transition-colors font-semibold"
              >
                Grid Iron Mind NFL API
              </a>
              {' '}• NFL-Grade Analytics
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
}
