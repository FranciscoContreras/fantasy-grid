import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'https://fantasy-grid-8e65f9ca9754.herokuapp.com/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add token to requests if available
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('auth_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Handle auth errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Clear invalid token
      localStorage.removeItem('auth_token');
      localStorage.removeItem('user');
      // Optionally redirect to login
      // window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Authentication API
export const register = async (data: {
  email: string;
  username: string;
  password: string;
  first_name?: string;
  last_name?: string;
}) => {
  const response = await api.post('/auth/register', data);
  if (response.data.data?.token) {
    localStorage.setItem('auth_token', response.data.data.token);
    localStorage.setItem('user', JSON.stringify(response.data.data.user));
  }
  return response.data;
};

export const login = async (email_or_username: string, password: string) => {
  const response = await api.post('/auth/login', { email_or_username, password });
  if (response.data.data?.token) {
    localStorage.setItem('auth_token', response.data.data.token);
    localStorage.setItem('user', JSON.stringify(response.data.data.user));
  }
  return response.data;
};

export const logout = () => {
  localStorage.removeItem('auth_token');
  localStorage.removeItem('user');
};

export const getCurrentUser = async () => {
  const response = await api.get('/auth/me');
  return response.data;
};

export const isAuthenticated = () => {
  return !!localStorage.getItem('auth_token');
};

export const getStoredUser = () => {
  const user = localStorage.getItem('user');
  return user ? JSON.parse(user) : null;
};

// Player API
export const searchPlayers = async (query: string, position?: string) => {
  const response = await api.get('/players/search', {
    params: { query, position },
  });
  return response.data;
};

// New Search Engine API
export const searchPlayersV2 = async (query: string, options?: {
  type?: 'player' | 'team';
  position?: string;
  team?: string;
  limit?: number;
}) => {
  const response = await api.get('/search/query', {
    params: {
      q: query,
      type: options?.type,
      position: options?.position,
      team: options?.team,
      limit: options?.limit
    },
  });
  return response.data;
};

export const autocompleteSearch = async (query: string, options?: {
  type?: 'player' | 'team';
  limit?: number;
}) => {
  const response = await api.get('/search/autocomplete', {
    params: {
      q: query,
      type: options?.type,
      limit: options?.limit
    },
  });
  return response.data;
};

export const analyzePlayer = async (
  playerId: string,
  opponent: string,
  location?: string
) => {
  const response = await api.get(`/players/${playerId}/analysis`, {
    params: { opponent, location },
  });
  return response.data;
};

export const comparePlayers = async (playerIds: string[]) => {
  const response = await api.post('/analysis/compare', { player_ids: playerIds });
  return response.data;
};

// Roster API
export const getRosters = async () => {
  const response = await api.get('/rosters');
  return response.data;
};

export const createRoster = async (data: {
  name: string;
  league_name?: string;
  scoring_type?: string;
}) => {
  const response = await api.post('/rosters', data);
  return response.data;
};

export const getRoster = async (rosterId: number) => {
  const response = await api.get(`/rosters/${rosterId}`);
  return response.data;
};

export const updateRoster = async (rosterId: number, data: any) => {
  const response = await api.put(`/rosters/${rosterId}`, data);
  return response.data;
};

export const deleteRoster = async (rosterId: number) => {
  const response = await api.delete(`/rosters/${rosterId}`);
  return response.data;
};

export const addPlayerToRoster = async (rosterId: number, data: {
  player_id?: string;
  player_name: string;
  position: string;
  team: string;
  roster_slot?: string;
  is_starter?: boolean;
  injury_status?: string;
}) => {
  const response = await api.post(`/rosters/${rosterId}/players`, data);
  return response.data;
};

export const updateRosterPlayer = async (
  rosterId: number,
  playerRosterId: number,
  data: any
) => {
  const response = await api.put(`/rosters/${rosterId}/players/${playerRosterId}`, data);
  return response.data;
};

export const removePlayerFromRoster = async (rosterId: number, playerRosterId: number) => {
  const response = await api.delete(`/rosters/${rosterId}/players/${playerRosterId}`);
  return response.data;
};

export const analyzeRoster = async (rosterId: number, week?: number, season?: number) => {
  const response = await api.post(`/rosters/${rosterId}/analyze`, {
    week,
    season
  });
  return response.data;
};

// Matchup API
export const createMatchup = async (data: {
  week: number;
  season: number;
  user_roster_id: number;
  opponent_roster_id?: number;
}) => {
  const response = await api.post('/matchups', data);
  return response.data;
};

export const getMatchup = async (matchupId: number) => {
  const response = await api.get(`/matchups/${matchupId}`);
  return response.data;
};

export const analyzeMatchup = async (matchupId: number) => {
  const response = await api.post(`/matchups/${matchupId}/analyze`);
  return response.data;
};

export const getMatchups = async (week?: number, season?: number) => {
  const response = await api.get('/matchups', { params: { week, season } });
  return response.data;
};

export const getSeasonMatchups = async (rosterId: number) => {
  const response = await api.get(`/matchups/season/${rosterId}`);
  return response.data;
};

export const getCurrentWeek = async () => {
  const response = await api.get('/matchups/current-week');
  return response.data;
};

export const getAvailableWeeks = async (season?: number, startWeek?: number) => {
  const response = await api.get('/matchups/available-weeks', {
    params: { season, start_week: startWeek }
  });
  return response.data;
};

export const getPlayerDetails = async (playerId: string) => {
  const response = await api.get(`/matchups/player/${playerId}`);
  return response.data;
};

// Get top fantasy players for current week - ACTUAL TOP PERFORMERS ONLY
export const getTopFantasyPlayers = async (limit: number = 10) => {
  try {
    // First get current week
    const currentWeekResponse = await getCurrentWeek();
    const currentWeek = currentWeekResponse.data?.week || 5;

    // Get top fantasy performers for current week with stricter filtering
    const response = await api.get('/advanced/players', {
      params: {
        season: 2025,
        week: currentWeek,
        status: 'active',
        limit: limit * 3, // Get many more to filter down to actual stars
        sort_by: 'fantasy_points',
        order: 'desc'
      }
    });

    if (response.data?.data) {
      // STRICT filtering for actual top fantasy performers - NO FREE AGENTS
      const topPerformers = response.data.data.filter((player: any) =>
        player.name &&
        player.team &&
        player.team !== 'FA' &&
        player.team !== 'FREE' &&
        player.team !== '' &&
        !player.name.includes('Practice') &&
        !player.name.includes('practice') &&
        player.jersey_number &&
        player.jersey_number > 0 &&
        player.jersey_number < 90 &&
        ['QB', 'RB', 'WR', 'TE'].includes(player.position) &&
        // Only include players with known fantasy relevance
        (player.fantasy_points > 0 || isKnownFantasyPlayer(player.name))
      );

      console.log(`Filtered to ${topPerformers.length} actual top performers from ${response.data.data.length} total players`);

      return {
        data: topPerformers.slice(0, limit),
        week: currentWeek
      };
    }
  } catch (error) {
    console.warn('Failed to get current week top players, using curated list:', error);
  }

  // Fallback: Use curated list of actual NFL stars for current week
  const currentWeek = 5;
  const curatedTopPlayers = [
    { name: 'Josh Allen', position: 'QB', team: 'BUF', nfl_id: '3918298', jersey_number: 17 },
    { name: 'Lamar Jackson', position: 'QB', team: 'BAL', nfl_id: '3916387', jersey_number: 8 },
    { name: 'Dak Prescott', position: 'QB', team: 'DAL', nfl_id: '2577417', jersey_number: 4 },
    { name: 'Saquon Barkley', position: 'RB', team: 'PHI', nfl_id: '3929630', jersey_number: 26 },
    { name: 'Josh Jacobs', position: 'RB', team: 'GB', nfl_id: '4035687', jersey_number: 8 },
    { name: 'Derrick Henry', position: 'RB', team: 'BAL', nfl_id: '4038524', jersey_number: 22 },
    { name: 'Tyreek Hill', position: 'WR', team: 'MIA', nfl_id: '3116406', jersey_number: 10 },
    { name: 'Stefon Diggs', position: 'WR', team: 'HOU', nfl_id: '2976499', jersey_number: 1 },
    { name: 'CeeDee Lamb', position: 'WR', team: 'DAL', nfl_id: '4262921', jersey_number: 88 },
    { name: 'Travis Kelce', position: 'TE', team: 'KC', nfl_id: '15847', jersey_number: 87 }
  ];

  return {
    data: curatedTopPlayers.slice(0, limit),
    week: currentWeek
  };
};

// Helper function to identify known fantasy players
function isKnownFantasyPlayer(name: string): boolean {
  const knownStars = [
    'Josh Allen', 'Lamar Jackson', 'Dak Prescott', 'Jayden Daniels', 'Tua Tagovailoa',
    'Saquon Barkley', 'Josh Jacobs', 'Derrick Henry', 'Jonathan Taylor', 'Christian McCaffrey',
    'Tyreek Hill', 'Stefon Diggs', 'CeeDee Lamb', 'Ja\'Marr Chase', 'Justin Jefferson',
    'Travis Kelce', 'Mark Andrews', 'George Kittle', 'Kyle Pitts', 'Sam LaPorta',
    'Cooper Kupp', 'Mike Evans', 'DeVonta Smith', 'A.J. Brown', 'Davante Adams'
  ];

  return knownStars.some(star => name.includes(star) || star.includes(name));
}

// Get featured players for landing page showcase (legacy)
export const getFeaturedPlayers = async (limit: number = 6) => {
  return getTopFantasyPlayers(limit);
};

// Get player analysis with multiple scoring formats
export const getPlayerAnalysisWithScoring = async (
  playerId: string,
  opponent?: string,
  scoringFormats: string[] = ['PPR', 'HALF_PPR', 'STANDARD']
) => {
  const promises = scoringFormats.map(format =>
    api.get(`/players/${playerId}/analysis`, {
      params: {
        opponent,
        scoring_format: format
      }
    })
  );

  const responses = await Promise.all(promises);
  return responses.map((response, index) => ({
    format: scoringFormats[index],
    data: response.data
  }));
};

// Yahoo Fantasy API
export const getYahooLeagues = async () => {
  const response = await api.get('/yahoo/leagues');
  return response.data;
};

export const importYahooRoster = async (data: { team_key: string; roster_name?: string }) => {
  const response = await api.post('/yahoo/import', data);
  return response.data;
};

export const getYahooStatus = async () => {
  const response = await api.get('/yahoo/status');
  return response.data;
};

export default api;
