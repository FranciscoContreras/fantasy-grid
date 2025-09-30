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

export default api;
