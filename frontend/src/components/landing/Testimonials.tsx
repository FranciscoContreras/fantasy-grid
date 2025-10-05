const testimonials = [
  {
    quote: "Pilon completely changed my game. 8-2 this season. The AI grading is scary accurate.",
    author: 'MIKE R.',
    role: '3X League Champion',
  },
  {
    quote: "The advanced analytics are unmatched. Caught a bad matchup I would have totally missed. Saved my season.",
    author: 'SARAH K.',
    role: 'Fantasy Analyst',
  },
  {
    quote: "Finally, data I can trust. No more Reddit debates. Just clear, confident recommendations backed by real analytics.",
    author: 'JAMES P.',
    role: '5-Year Player',
  },
  {
    quote: "Weather analysis alone is worth it. Won two weeks benching players in bad weather everyone else started.",
    author: 'ALEX M.',
    role: 'DFS Player',
  },
  {
    quote: "Managing multiple leagues used to be a nightmare. Now I analyze all rosters in minutes. Absolute time saver.",
    author: 'CHRIS T.',
    role: '4 Leagues · 2 Championships',
  },
  {
    quote: "The confidence scores are brilliant. Know exactly when to trust my gut and when to follow the data.",
    author: 'EMILY R.',
    role: 'First-Year Champion',
  },
];

export function Testimonials() {
  return (
    <div className="relative py-24 sm:py-32 bg-gray-50 text-gray-900 overflow-hidden">
      <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Section Header */}
        <div className="text-center max-w-3xl mx-auto mb-20">
          <div className="inline-flex items-center gap-2 px-4 py-2 bg-gray-200 border border-gray-300 rounded-full mb-6">
            <span className="text-xs font-bold text-gray-700 uppercase tracking-wider">
              Join 10K+ Winners
            </span>
          </div>
          <h2 className="text-5xl sm:text-6xl md:text-7xl lg:text-8xl font-black tracking-tighter mb-6 leading-none text-gray-900">
            REAL
            <br />
            RESULTS
          </h2>
          <p className="text-xl sm:text-2xl text-gray-600 font-light">
            See what champions are saying about Pilon.
          </p>
        </div>

        {/* Stats Bar */}
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-20">
          <div className="bg-white border border-gray-200 rounded-xl p-6 text-center shadow-sm">
            <div className="text-4xl font-black text-gray-900 mb-2">10K+</div>
            <div className="text-xs text-gray-500 uppercase tracking-wider font-semibold">Active Users</div>
          </div>
          <div className="bg-white border border-gray-200 rounded-xl p-6 text-center shadow-sm">
            <div className="text-4xl font-black text-gray-900 mb-2">1M+</div>
            <div className="text-xs text-gray-500 uppercase tracking-wider font-semibold">Recommendations</div>
          </div>
          <div className="bg-white border border-gray-200 rounded-xl p-6 text-center shadow-sm">
            <div className="text-4xl font-black text-gray-900 mb-2">73%</div>
            <div className="text-xs text-gray-500 uppercase tracking-wider font-semibold">Win Rate</div>
          </div>
          <div className="bg-white border border-gray-200 rounded-xl p-6 text-center shadow-sm">
            <div className="text-4xl font-black text-gray-900 mb-2">4.9★</div>
            <div className="text-xs text-gray-500 uppercase tracking-wider font-semibold">Average Rating</div>
          </div>
        </div>

        {/* Testimonials Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {testimonials.map((testimonial, index) => (
            <div
              key={index}
              className="group relative bg-white border border-gray-200 rounded-2xl p-8 hover:shadow-md transition-all shadow-sm"
            >
              {/* Quote mark */}
              <div className="text-7xl font-black text-gray-100 leading-none mb-4">
                "
              </div>

              {/* Quote */}
              <p className="text-gray-700 leading-relaxed mb-8 relative z-10">
                {testimonial.quote}
              </p>

              {/* Author */}
              <div className="flex items-center gap-4 pt-6 border-t border-gray-200">
                <div className="w-12 h-12 rounded-lg bg-gray-900 flex items-center justify-center text-white font-black text-lg">
                  {testimonial.author[0]}
                </div>
                <div>
                  <div className="font-black text-gray-900 tracking-tight">{testimonial.author}</div>
                  <div className="text-xs text-gray-500 uppercase tracking-wider font-semibold">{testimonial.role}</div>
                </div>
              </div>

              {/* 5 stars */}
              <div className="flex gap-1 mt-4">
                {[...Array(5)].map((_, i) => (
                  <svg key={i} className="w-4 h-4 text-yellow-400 fill-current" viewBox="0 0 20 20">
                    <path d="M10 15l-5.878 3.09 1.123-6.545L.489 6.91l6.572-.955L10 0l2.939 5.955 6.572.955-4.756 4.635 1.123 6.545z" />
                  </svg>
                ))}
              </div>
            </div>
          ))}
        </div>

        {/* Social Proof Banner */}
        <div className="mt-20 relative">
          <div className="relative bg-white border border-gray-200 rounded-3xl p-12 text-center shadow-sm">
            <div className="max-w-3xl mx-auto">
              <h3 className="text-3xl sm:text-4xl font-black mb-4 tracking-tight text-gray-900">
                TRUSTED BY THE
                <br />
                BEST IN THE GAME
              </h3>
              <p className="text-lg text-gray-600 mb-8">
                Thousands of fantasy champions rely on Pilon every week to make winning decisions.
                Join the community dominating leagues nationwide.
              </p>
              <div className="flex flex-wrap justify-center gap-8 text-sm">
                <div className="flex items-center gap-2">
                  <svg className="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  <span className="text-gray-700 uppercase tracking-wider font-semibold">Secure & Private</span>
                </div>
                <div className="flex items-center gap-2">
                  <svg className="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                  </svg>
                  <span className="text-gray-700 uppercase tracking-wider font-semibold">Lightning Fast</span>
                </div>
                <div className="flex items-center gap-2">
                  <svg className="w-6 h-6 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  <span className="text-gray-700 uppercase tracking-wider font-semibold">24/7 Updates</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
