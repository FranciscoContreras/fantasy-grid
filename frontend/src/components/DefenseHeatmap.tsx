import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';
import { Button } from './ui/button';

interface HeatmapTeam {
  team_id: string;
  team_name: string;
  team_abbr: string;
  division: string;
  conference: string;
  defense_rank: number;
  percentile: number;
  color_category: string;
}

interface DefenseHeatmapData {
  heatmap: HeatmapTeam[];
  position: string | null;
  season: number;
  legend: {
    excellent: { range: string; color: string; description: string };
    good: { range: string; color: string; description: string };
    average: { range: string; color: string; description: string };
    tough: { range: string; color: string; description: string };
    elite: { range: string; color: string; description: string };
  };
}

export function DefenseHeatmap() {
  const [data, setData] = useState<DefenseHeatmapData | null>(null);
  const [loading, setLoading] = useState(true);
  const [selectedPosition, setSelectedPosition] = useState<string>('ALL');
  const [selectedConference, setSelectedConference] = useState<string>('ALL');

  const positions = ['ALL', 'QB', 'RB', 'WR', 'TE'];
  const conferences = ['ALL', 'AFC', 'NFC'];

  useEffect(() => {
    fetchDefenseHeatmap();
  }, [selectedPosition]);

  const fetchDefenseHeatmap = async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams({
        season: '2024',
      });

      if (selectedPosition !== 'ALL') {
        params.append('position', selectedPosition);
      }

      const response = await fetch(`/api/analysis/defense-heatmap?${params}`);
      const result = await response.json();
      setData(result.data);
    } catch (error) {
      console.error('Failed to fetch defense heatmap:', error);
    } finally {
      setLoading(false);
    }
  };

  const getCategoryColor = (category: string) => {
    switch (category.toLowerCase()) {
      case 'excellent':
        return 'bg-green-500 text-white';
      case 'good':
        return 'bg-green-300 text-gray-900';
      case 'average':
        return 'bg-yellow-400 text-gray-900';
      case 'tough':
        return 'bg-orange-400 text-white';
      case 'elite':
        return 'bg-red-500 text-white';
      default:
        return 'bg-gray-400 text-white';
    }
  };

  const getCategoryBorderColor = (category: string) => {
    switch (category.toLowerCase()) {
      case 'excellent':
        return 'border-green-500';
      case 'good':
        return 'border-green-300';
      case 'average':
        return 'border-yellow-400';
      case 'tough':
        return 'border-orange-400';
      case 'elite':
        return 'border-red-500';
      default:
        return 'border-gray-400';
    }
  };

  const filterByConference = (teams: HeatmapTeam[]) => {
    if (selectedConference === 'ALL') return teams;
    return teams.filter((team) => team.conference === selectedConference);
  };

  const groupByDivision = (teams: HeatmapTeam[]) => {
    const grouped: { [key: string]: HeatmapTeam[] } = {};
    teams.forEach((team) => {
      if (!grouped[team.division]) {
        grouped[team.division] = [];
      }
      grouped[team.division].push(team);
    });
    return grouped;
  };

  if (loading) {
    return (
      <Card className="w-full">
        <CardContent className="p-12">
          <div className="flex items-center justify-center">
            <div className="text-center">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-black mx-auto mb-4"></div>
              <p className="text-sm text-muted-foreground">Loading defense heatmap...</p>
            </div>
          </div>
        </CardContent>
      </Card>
    );
  }

  if (!data) {
    return (
      <Card className="w-full">
        <CardContent className="p-12">
          <div className="text-center">
            <p className="text-lg font-semibold text-gray-600">Heatmap not available</p>
          </div>
        </CardContent>
      </Card>
    );
  }

  const filteredTeams = filterByConference(data.heatmap);
  const groupedTeams = groupByDivision(filteredTeams);

  return (
    <div className="space-y-6">
      {/* Header & Filters */}
      <Card className="w-full">
        <CardHeader>
          <CardTitle className="text-2xl font-black">Defense Heatmap</CardTitle>
          <p className="text-sm text-muted-foreground">
            Visual guide to defensive strength across the NFL
          </p>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {/* Position Filter */}
            <div>
              <p className="text-xs text-gray-500 uppercase tracking-wider font-semibold mb-2">
                Position
              </p>
              <div className="flex flex-wrap gap-2">
                {positions.map((pos) => (
                  <Button
                    key={pos}
                    variant={selectedPosition === pos ? 'default' : 'outline'}
                    onClick={() => setSelectedPosition(pos)}
                    className="font-bold"
                  >
                    {pos}
                  </Button>
                ))}
              </div>
            </div>

            {/* Conference Filter */}
            <div>
              <p className="text-xs text-gray-500 uppercase tracking-wider font-semibold mb-2">
                Conference
              </p>
              <div className="flex flex-wrap gap-2">
                {conferences.map((conf) => (
                  <Button
                    key={conf}
                    variant={selectedConference === conf ? 'default' : 'outline'}
                    onClick={() => setSelectedConference(conf)}
                  >
                    {conf}
                  </Button>
                ))}
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Legend */}
      <Card className="w-full">
        <CardHeader>
          <CardTitle className="text-lg font-black">Legend</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-5 gap-3">
            {Object.entries(data.legend).map(([key, value]) => (
              <div
                key={key}
                className={`${getCategoryColor(key)} rounded-lg p-4 text-center border-2 ${getCategoryBorderColor(key)}`}
              >
                <p className="font-black text-sm uppercase mb-1">{key}</p>
                <p className="text-xs mb-2">{value.range}</p>
                <p className="text-xs">{value.description}</p>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Heatmap by Division */}
      {Object.entries(groupedTeams)
        .sort(([divA], [divB]) => divA.localeCompare(divB))
        .map(([division, teams]) => (
          <Card key={division} className="w-full">
            <CardHeader>
              <CardTitle className="text-xl font-black">{division}</CardTitle>
              <p className="text-sm text-muted-foreground">{teams.length} teams</p>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                {teams
                  .sort((a, b) => a.defense_rank - b.defense_rank)
                  .map((team) => (
                    <div
                      key={team.team_id}
                      className={`border-4 ${getCategoryBorderColor(team.color_category)} rounded-lg p-4 hover:shadow-lg transition-shadow`}
                    >
                      <div className="flex items-start justify-between mb-3">
                        <div>
                          <h3 className="font-black text-lg">{team.team_abbr}</h3>
                          <p className="text-xs text-gray-600">{team.team_name}</p>
                        </div>
                        <Badge
                          className={`${getCategoryColor(team.color_category)} font-bold`}
                        >
                          {team.color_category.toUpperCase()}
                        </Badge>
                      </div>

                      <div className="space-y-2">
                        <div className="flex justify-between items-center">
                          <p className="text-xs text-gray-500 uppercase tracking-wider font-semibold">
                            Rank
                          </p>
                          <p className="text-lg font-black">#{team.defense_rank}</p>
                        </div>
                        <div className="flex justify-between items-center">
                          <p className="text-xs text-gray-500 uppercase tracking-wider font-semibold">
                            Percentile
                          </p>
                          <p className="text-lg font-black">{team.percentile}%</p>
                        </div>
                      </div>

                      <div className="mt-3 pt-3 border-t">
                        <div className="w-full bg-gray-200 rounded-full h-2">
                          <div
                            className={`h-2 rounded-full ${getCategoryColor(team.color_category)}`}
                            style={{ width: `${team.percentile}%` }}
                          ></div>
                        </div>
                      </div>
                    </div>
                  ))}
              </div>
            </CardContent>
          </Card>
        ))}

      {/* Quick Stats */}
      <Card className="w-full">
        <CardHeader>
          <CardTitle className="text-xl font-black">Quick Stats</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
            <div className="bg-green-50 rounded-lg p-4 text-center">
              <p className="text-2xl font-black">
                {filteredTeams.filter((t) => t.color_category === 'excellent').length}
              </p>
              <p className="text-xs text-gray-500 uppercase tracking-wider font-semibold">
                Excellent (Exploit)
              </p>
            </div>
            <div className="bg-green-50 rounded-lg p-4 text-center">
              <p className="text-2xl font-black">
                {filteredTeams.filter((t) => t.color_category === 'good').length}
              </p>
              <p className="text-xs text-gray-500 uppercase tracking-wider font-semibold">
                Good (Target)
              </p>
            </div>
            <div className="bg-yellow-50 rounded-lg p-4 text-center">
              <p className="text-2xl font-black">
                {filteredTeams.filter((t) => t.color_category === 'average').length}
              </p>
              <p className="text-xs text-gray-500 uppercase tracking-wider font-semibold">
                Average (Neutral)
              </p>
            </div>
            <div className="bg-orange-50 rounded-lg p-4 text-center">
              <p className="text-2xl font-black">
                {filteredTeams.filter((t) => t.color_category === 'tough').length}
              </p>
              <p className="text-xs text-gray-500 uppercase tracking-wider font-semibold">
                Tough (Caution)
              </p>
            </div>
            <div className="bg-red-50 rounded-lg p-4 text-center">
              <p className="text-2xl font-black">
                {filteredTeams.filter((t) => t.color_category === 'elite').length}
              </p>
              <p className="text-xs text-gray-500 uppercase tracking-wider font-semibold">
                Elite (Avoid)
              </p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
