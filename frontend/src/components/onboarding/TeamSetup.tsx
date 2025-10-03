import { useState } from 'react';
import { Input } from '../ui/input';
import { Button } from '../ui/button';
import { Card, CardContent } from '../ui/card';

interface TeamSetupProps {
  onNext: (data: { name: string; leagueName: string; scoringType: string }) => void;
}

export function TeamSetup({ onNext }: TeamSetupProps) {
  const [name, setName] = useState('');
  const [leagueName, setLeagueName] = useState('');
  const [scoringType, setScoringType] = useState('PPR');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (name.trim()) {
      onNext({ name, leagueName, scoringType });
    }
  };

  return (
    <div className="max-w-2xl mx-auto">
      <div className="text-center mb-12">
        <div className="inline-flex items-center gap-2 px-4 py-2 bg-gray-100 rounded-full mb-6">
          <span className="text-xs font-bold text-gray-900 uppercase tracking-wider">
            Step 1 of 3
          </span>
        </div>
        <h2 className="text-5xl font-black tracking-tight mb-4">
          NAME YOUR TEAM
        </h2>
        <p className="text-xl text-gray-600">
          Let's get your roster set up in under 3 minutes
        </p>
      </div>

      <Card>
        <CardContent className="pt-8">
          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Team Name */}
            <div>
              <label className="block text-sm font-bold text-gray-700 uppercase tracking-wider mb-2">
                Team Name *
              </label>
              <Input
                type="text"
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="e.g., The Champs"
                className="text-lg p-6 border-2 border-gray-300 focus:border-black"
                required
              />
            </div>

            {/* League Name */}
            <div>
              <label className="block text-sm font-bold text-gray-700 uppercase tracking-wider mb-2">
                League Name (Optional)
              </label>
              <Input
                type="text"
                value={leagueName}
                onChange={(e) => setLeagueName(e.target.value)}
                placeholder="e.g., Friends & Family League"
                className="text-lg p-6 border-2 border-gray-300 focus:border-black"
              />
            </div>

            {/* Scoring Type */}
            <div>
              <label className="block text-sm font-bold text-gray-700 uppercase tracking-wider mb-3">
                Scoring Format *
              </label>
              <div className="grid grid-cols-3 gap-3">
                <button
                  type="button"
                  onClick={() => setScoringType('PPR')}
                  className={`p-4 border-2 rounded-xl font-bold transition-all ${
                    scoringType === 'PPR'
                      ? 'border-black bg-black text-white'
                      : 'border-gray-300 hover:border-gray-400'
                  }`}
                >
                  <div className="text-lg mb-1">PPR</div>
                  <div className="text-xs opacity-70 font-normal">Point Per Reception</div>
                </button>

                <button
                  type="button"
                  onClick={() => setScoringType('HALF_PPR')}
                  className={`p-4 border-2 rounded-xl font-bold transition-all ${
                    scoringType === 'HALF_PPR'
                      ? 'border-black bg-black text-white'
                      : 'border-gray-300 hover:border-gray-400'
                  }`}
                >
                  <div className="text-lg mb-1">HALF PPR</div>
                  <div className="text-xs opacity-70 font-normal">0.5 Per Reception</div>
                </button>

                <button
                  type="button"
                  onClick={() => setScoringType('STANDARD')}
                  className={`p-4 border-2 rounded-xl font-bold transition-all ${
                    scoringType === 'STANDARD'
                      ? 'border-black bg-black text-white'
                      : 'border-gray-300 hover:border-gray-400'
                  }`}
                >
                  <div className="text-lg mb-1">STANDARD</div>
                  <div className="text-xs opacity-70 font-normal">No PPR</div>
                </button>
              </div>
            </div>

            {/* Submit Button */}
            <Button
              type="submit"
              disabled={!name.trim()}
              className="w-full bg-black text-white hover:bg-gray-900 py-7 text-lg font-black uppercase tracking-wider"
            >
              NEXT: ADD PLAYERS
              <svg className="ml-2 w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M13 7l5 5m0 0l-5 5m5-5H6" />
              </svg>
            </Button>
          </form>
        </CardContent>
      </Card>
    </div>
  );
}
