import requests
import os

class FantasyAPIClient:
    def __init__(self):
        self.base_url = os.getenv('API_BASE_URL', 'https://nfl.wearemachina.com/api/v1')
        self.api_key = os.getenv('API_KEY')

    def _get_headers(self, include_api_key=False):
        headers = {'Content-Type': 'application/json'}
        if include_api_key and self.api_key:
            headers['X-API-Key'] = self.api_key
        return headers

    def get_player_data(self, player_id):
        """Get player details by ID"""
        response = requests.get(
            f'{self.base_url}/players/{player_id}',
            headers=self._get_headers()
        )
        response.raise_for_status()
        return response.json()

    def search_players(self, query, position=None):
        """Search for players by name and optionally filter by position"""
        params = {'limit': 20}
        if position:
            params['position'] = position

        response = requests.get(
            f'{self.base_url}/players',
            params=params,
            headers=self._get_headers()
        )
        response.raise_for_status()
        return response.json().get('data', [])

    def get_defense_stats(self, team_id):
        """Get defensive statistics for a team"""
        response = requests.get(
            f'{self.base_url}/teams/{team_id}',
            headers=self._get_headers()
        )
        response.raise_for_status()
        return response.json()

    def get_weather_data(self, location):
        """Get current weather for a location"""
        response = requests.get(
            f'{self.base_url}/weather/current',
            params={'location': location},
            headers=self._get_headers()
        )
        response.raise_for_status()
        return response.json()

    def get_player_career_stats(self, player_id):
        """Get career statistics for a player"""
        response = requests.get(
            f'{self.base_url}/players/{player_id}/career',
            headers=self._get_headers()
        )
        response.raise_for_status()
        return response.json()
