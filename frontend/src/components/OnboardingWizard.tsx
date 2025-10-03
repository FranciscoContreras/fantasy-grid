import { useState } from 'react';
import { TeamSetup } from './onboarding/TeamSetup';
import { QuickRosterBuilder } from './onboarding/QuickRosterBuilder';
import { FirstAnalysis } from './onboarding/FirstAnalysis';
import { Player } from '@/types';

interface OnboardingWizardProps {
  onComplete: (rosterId: number) => void;
}

export function OnboardingWizard({ onComplete }: OnboardingWizardProps) {
  const [step, setStep] = useState(1);
  const [teamData, setTeamData] = useState<{ name: string; leagueName: string; scoringType: string } | null>(null);
  const [players, setPlayers] = useState<Player[]>([]);
  const [rosterId, setRosterId] = useState<number | null>(null);
  const [creating, setCreating] = useState(false);
  const [error, setError] = useState('');

  const handleTeamSetup = async (data: { name: string; leagueName: string; scoringType: string }) => {
    setTeamData(data);
    setStep(2);
  };

  const handleAddPlayers = async (selectedPlayers: Player[]) => {
    setCreating(true);
    setError('');

    try {
      // Create the roster
      const token = localStorage.getItem('auth_token');
      const response = await fetch('/api/rosters', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          name: teamData?.name,
          league_name: teamData?.leagueName,
          scoring_type: teamData?.scoringType,
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to create roster');
      }

      const result = await response.json();
      const newRosterId = result.data.id;
      setRosterId(newRosterId);

      // Add players to roster
      if (selectedPlayers.length > 0) {
        await Promise.all(
          selectedPlayers.map(async (player) => {
            const playerResponse = await fetch(`/api/rosters/${newRosterId}/players`, {
              method: 'POST',
              headers: {
                'Content-Type': 'application/json',
                Authorization: `Bearer ${token}`,
              },
              body: JSON.stringify({
                player_id: player.id || player.player_id,
                player_name: player.name,
                position: player.position,
                team: player.team,
                roster_slot: 'BENCH',
                is_starter: false,
                injury_status: 'HEALTHY',
              }),
            });

            if (!playerResponse.ok) {
              console.error(`Failed to add player ${player.name}`);
            }
          })
        );
      }

      setPlayers(selectedPlayers);
      setStep(3);
    } catch (err) {
      console.error('Error creating roster:', err);
      setError('Failed to create roster. Please try again.');
    } finally {
      setCreating(false);
    }
  };

  const handleSkip = async () => {
    // Create roster without players
    await handleAddPlayers([]);
  };

  const handleComplete = () => {
    if (rosterId) {
      onComplete(rosterId);
    }
  };

  if (creating) {
    return (
      <div className="min-h-screen bg-white flex items-center justify-center">
        <div className="text-center">
          <div className="w-16 h-16 border-4 border-black border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-lg font-semibold text-gray-600 uppercase tracking-wider">Creating your roster...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-white flex items-center justify-center p-4">
        <div className="max-w-md w-full text-center">
          <div className="text-6xl mb-6"> </div>
          <h2 className="text-3xl font-black mb-4">OOPS!</h2>
          <p className="text-gray-600 mb-6">{error}</p>
          <button
            onClick={() => setError('')}
            className="px-6 py-3 bg-black text-white rounded-lg font-bold hover:bg-gray-900"
          >
            TRY AGAIN
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-white py-12 px-4">
      {step === 1 && <TeamSetup onNext={handleTeamSetup} />}
      {step === 2 && <QuickRosterBuilder onNext={handleAddPlayers} onSkip={handleSkip} />}
      {step === 3 && rosterId && (
        <FirstAnalysis rosterId={rosterId} playerCount={players.length} onComplete={handleComplete} />
      )}
    </div>
  );
}
