import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';
import { Button } from './ui/button';

interface Team {
  id: string;
  team_id?: string;
  name: string;
  abbreviation: string;
  city?: string;
  conference?: string;
  division?: string;
  stadium?: string;
  head_coach?: string;
  colors?: {
    primary?: string;
    secondary?: string;
  };
  established?: number;
}

interface Injury {
  player_name: string;
  position: string;
  status: string;
  description?: string;
}

interface TeamDetailsCardProps {
  teamId: string;
  onClose?: () => void;
}

export function TeamDetailsCard({ teamId, onClose }: TeamDetailsCardProps) {
  const [team, setTeam] = useState<Team | null>(null);
  const [injuries, setInjuries] = useState<Injury[]>([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<'info' | 'injuries' | 'roster'>('info');

  useEffect(() => {
    fetchTeamDetails();
  }, [teamId]);

  const fetchTeamDetails = async () => {
    setLoading(true);
    try {
      // Fetch team details
      const teamResponse = await fetch(`/api/advanced/teams/${teamId}`);
      const teamData = await teamResponse.json();
      setTeam(teamData.data);

      // Fetch injuries
      const injuriesResponse = await fetch(`/api/advanced/teams/${teamId}/injuries`);
      const injuriesData = await injuriesResponse.json();
      setInjuries(injuriesData.data || []);
    } catch (error) {
      console.error('Failed to fetch team details:', error);
    } finally {
      setLoading(false);
    }
  };

  const getInjuryStatusColor = (status: string) => {
    const statusLower = status.toLowerCase();
    if (statusLower.includes('out')) return 'bg-red-100 text-red-800';
    if (statusLower.includes('doubtful')) return 'bg-orange-100 text-orange-800';
    if (statusLower.includes('questionable')) return 'bg-yellow-100 text-yellow-800';
    if (statusLower.includes('probable')) return 'bg-green-100 text-green-800';
    return 'bg-gray-100 text-gray-800';
  };

  if (loading) {
    return (
      <Card className="w-full">
        <CardContent className="p-12">
          <div className="flex items-center justify-center">
            <div className="text-center">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-black mx-auto mb-4"></div>
              <p className="text-sm text-muted-foreground">Loading team details...</p>
            </div>
          </div>
        </CardContent>
      </Card>
    );
  }

  if (!team) {
    return (
      <Card className="w-full">
        <CardContent className="p-12">
          <div className="text-center">
            <p className="text-lg font-semibold text-gray-600">Team not found</p>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="w-full">
      <CardHeader>
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <div className="flex items-center gap-3 mb-2">
              <div
                className="w-16 h-16 rounded-lg flex items-center justify-center text-white font-black text-2xl"
                style={{ backgroundColor: team.colors?.primary || '#000' }}
              >
                {team.abbreviation}
              </div>
              <div>
                <CardTitle className="text-2xl font-black">{team.name}</CardTitle>
                <p className="text-sm text-muted-foreground">
                  {team.city && `${team.city} • `}
                  {team.conference} {team.division}
                </p>
              </div>
            </div>
          </div>
          {onClose && (
            <Button variant="ghost" size="sm" onClick={onClose}>
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </Button>
          )}
        </div>

        {/* Tabs */}
        <div className="flex gap-2 pt-4 border-t">
          <Button
            variant={activeTab === 'info' ? 'default' : 'outline'}
            size="sm"
            onClick={() => setActiveTab('info')}
            className="font-bold"
          >
            Info
          </Button>
          <Button
            variant={activeTab === 'injuries' ? 'default' : 'outline'}
            size="sm"
            onClick={() => setActiveTab('injuries')}
            className="font-bold"
          >
            Injuries {injuries.length > 0 && `(${injuries.length})`}
          </Button>
          <Button
            variant={activeTab === 'roster' ? 'default' : 'outline'}
            size="sm"
            onClick={() => setActiveTab('roster')}
            className="font-bold"
          >
            Roster
          </Button>
        </div>
      </CardHeader>

      <CardContent>
        {/* Info Tab */}
        {activeTab === 'info' && (
          <div className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              {team.stadium && (
                <div className="bg-gray-50 p-4 rounded-lg">
                  <p className="text-xs text-gray-500 uppercase tracking-wider font-semibold mb-1">Stadium</p>
                  <p className="font-bold">{team.stadium}</p>
                </div>
              )}
              {team.head_coach && (
                <div className="bg-gray-50 p-4 rounded-lg">
                  <p className="text-xs text-gray-500 uppercase tracking-wider font-semibold mb-1">Head Coach</p>
                  <p className="font-bold">{team.head_coach}</p>
                </div>
              )}
              {team.established && (
                <div className="bg-gray-50 p-4 rounded-lg">
                  <p className="text-xs text-gray-500 uppercase tracking-wider font-semibold mb-1">Established</p>
                  <p className="font-bold">{team.established}</p>
                </div>
              )}
              {team.colors && (
                <div className="bg-gray-50 p-4 rounded-lg">
                  <p className="text-xs text-gray-500 uppercase tracking-wider font-semibold mb-1">Team Colors</p>
                  <div className="flex gap-2 mt-2">
                    {team.colors.primary && (
                      <div
                        className="w-8 h-8 rounded border-2 border-gray-300"
                        style={{ backgroundColor: team.colors.primary }}
                      />
                    )}
                    {team.colors.secondary && (
                      <div
                        className="w-8 h-8 rounded border-2 border-gray-300"
                        style={{ backgroundColor: team.colors.secondary }}
                      />
                    )}
                  </div>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Injuries Tab */}
        {activeTab === 'injuries' && (
          <div className="space-y-3">
            {injuries.length === 0 ? (
              <div className="text-center py-8 text-gray-500">
                <p className="font-semibold">No injuries reported</p>
                <p className="text-sm">All players are healthy</p>
              </div>
            ) : (
              injuries.map((injury, index) => (
                <div key={index} className="border rounded-lg p-4 hover:bg-gray-50 transition-colors">
                  <div className="flex items-start justify-between mb-2">
                    <div>
                      <p className="font-bold">{injury.player_name}</p>
                      <p className="text-sm text-gray-600">{injury.position}</p>
                    </div>
                    <Badge className={getInjuryStatusColor(injury.status)}>
                      {injury.status}
                    </Badge>
                  </div>
                  {injury.description && (
                    <p className="text-sm text-gray-600">{injury.description}</p>
                  )}
                </div>
              ))
            )}
          </div>
        )}

        {/* Roster Tab */}
        {activeTab === 'roster' && (
          <div className="text-center py-8 text-gray-500">
            <p className="font-semibold">Roster view coming soon</p>
            <p className="text-sm">Full team roster with stats and details</p>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
