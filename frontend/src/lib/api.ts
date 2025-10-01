import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const searchPlayers = async (query: string, position?: string) => {
  const response = await api.get('/players/search', {
    params: { q: query, position },
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
export const getRosters = async (userId = 'default_user') => {
  const response = await api.get('/rosters', { params: { user_id: userId } });
  return response.data;
};

export const createRoster = async (data: {
  name: string;
  league_name?: string;
  scoring_type?: string;
  user_id?: string;
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

// Matchup API
export const createMatchup = async (data: {
  week: number;
  season: number;
  user_roster_id: number;
  opponent_roster_id: number;
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

export default api;
