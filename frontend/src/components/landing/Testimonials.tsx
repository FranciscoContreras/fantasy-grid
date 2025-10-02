import { Card, CardContent } from '../ui/card';

const testimonials = [
  {
    quote:
      "Fantasy Grid completely changed my fantasy game. I'm 8-2 this season thanks to the start/sit recommendations. The AI grading is scary accurate - it's like having a fantasy analyst on speed dial.",
    author: 'Mike R.',
    role: '3-time league champion',
    avatar: 'M',
    rating: 5,
  },
  {
    quote:
      "The advanced analytics are unmatched. It caught a bad matchup for my RB1 that I would have totally missed. Saved my week and probably saved my season. Worth every penny.",
    author: 'Sarah K.',
    role: 'Fantasy analyst',
    avatar: 'S',
    rating: 5,
  },
  {
    quote:
      "Finally, data I can trust. No more endless Reddit debates or conflicting advice. Just clear, confident recommendations backed by real analytics. This is what fantasy football should be.",
    author: 'James P.',
    role: '5-year player',
    avatar: 'J',
    rating: 5,
  },
  {
    quote:
      "The weather impact analysis alone is worth it. I've won two weeks this season by benching players in bad weather that everyone else started. Game changer.",
    author: 'Alex M.',
    role: 'DFS player',
    avatar: 'A',
    rating: 5,
  },
  {
    quote:
      "Managing multiple leagues used to be a nightmare. Now I can analyze all my rosters in minutes and make confident decisions across the board. Absolute time saver.",
    author: 'Chris T.',
    role: '4 leagues, 2 championships',
    avatar: 'C',
    rating: 5,
  },
  {
    quote:
      "The confidence scores are brilliant. I know exactly when to trust my gut and when to follow the data. It's the perfect balance of analytics and intuition.",
    author: 'Emily R.',
    role: 'First-year champion',
    avatar: 'E',
    rating: 5,
  },
];

const stats = [
  {
    icon: '👥',
    value: '10,000+',
    label: 'Active Users',
  },
  {
    icon: '🎯',
    value: '1M+',
    label: 'Recommendations',
  },
  {
    icon: '🏆',
    value: '73%',
    label: 'Win Rate',
  },
  {
    icon: '⭐',
    value: '4.9/5',
    label: 'Average Rating',
  },
];

export function Testimonials() {
  return (
    <div className="py-16 sm:py-24 bg-white">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Section Header */}
        <div className="text-center max-w-3xl mx-auto mb-16">
          <h2 className="text-3xl sm:text-4xl lg:text-5xl font-extrabold text-gray-900 mb-4">
            Trusted by Thousands of
            <span className="block bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent">
              Fantasy Champions
            </span>
          </h2>
          <p className="text-lg sm:text-xl text-gray-600">
            See what our community is saying about Fantasy Grid
          </p>
        </div>

        {/* Testimonials Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8 mb-16">
          {testimonials.map((testimonial, index) => (
            <Card key={index} className="hover:shadow-xl transition-shadow border-2 hover:border-blue-200">
              <CardContent className="p-6">
                {/* Rating */}
                <div className="flex gap-1 mb-4">
                  {[...Array(testimonial.rating)].map((_, i) => (
                    <svg
                      key={i}
                      className="w-5 h-5 text-yellow-400 fill-current"
                      viewBox="0 0 20 20"
                    >
                      <path d="M10 15l-5.878 3.09 1.123-6.545L.489 6.91l6.572-.955L10 0l2.939 5.955 6.572.955-4.756 4.635 1.123 6.545z" />
                    </svg>
                  ))}
                </div>

                {/* Quote */}
                <p className="text-gray-700 leading-relaxed mb-6 italic">
                  "{testimonial.quote}"
                </p>

                {/* Author */}
                <div className="flex items-center gap-3 pt-4 border-t border-gray-200">
                  <div className="w-12 h-12 rounded-full bg-gradient-to-br from-blue-600 to-indigo-600 flex items-center justify-center text-white font-bold text-lg">
                    {testimonial.avatar}
                  </div>
                  <div>
                    <div className="font-semibold text-gray-900">{testimonial.author}</div>
                    <div className="text-sm text-gray-600">{testimonial.role}</div>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>

        {/* Stats */}
        <div className="bg-gradient-to-br from-blue-600 to-indigo-600 rounded-3xl p-8 sm:p-12">
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-8">
            {stats.map((stat, index) => (
              <div key={index} className="text-center">
                <div className="text-5xl mb-3">{stat.icon}</div>
                <div className="text-3xl sm:text-4xl font-bold text-white mb-2">{stat.value}</div>
                <div className="text-blue-100 font-medium">{stat.label}</div>
              </div>
            ))}
          </div>
        </div>

        {/* Trust Badges */}
        <div className="mt-16 flex flex-col sm:flex-row gap-8 justify-center items-center text-center">
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 rounded-full bg-green-100 flex items-center justify-center">
              <svg className="w-7 h-7 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <div className="text-left">
              <div className="font-semibold text-gray-900">Secure & Private</div>
              <div className="text-sm text-gray-600">Your data is protected</div>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <div className="w-12 h-12 rounded-full bg-blue-100 flex items-center justify-center">
              <svg className="w-7 h-7 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
              </svg>
            </div>
            <div className="text-left">
              <div className="font-semibold text-gray-900">Lightning Fast</div>
              <div className="text-sm text-gray-600">Instant recommendations</div>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <div className="w-12 h-12 rounded-full bg-purple-100 flex items-center justify-center">
              <svg className="w-7 h-7 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
              </svg>
            </div>
            <div className="text-left">
              <div className="font-semibold text-gray-900">Customer Love</div>
              <div className="text-sm text-gray-600">4.9/5 rating</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
