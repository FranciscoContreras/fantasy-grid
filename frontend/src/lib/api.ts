import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000/api';

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

export default api;
