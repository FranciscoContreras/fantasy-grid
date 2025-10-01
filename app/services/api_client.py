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
        params = {'limit': 100}  # Get more results for better filtering
        if position:
            params['position'] = position

        response = requests.get(
            f'{self.base_url}/players',
            params=params,
            headers=self._get_headers()
        )
        response.raise_for_status()
        all_players = response.json().get('data', [])

        # Advanced search with relevance scoring
        if query:
            scored_players = self._score_and_filter_players(all_players, query)
            return scored_players[:20]  # Return top 20 most relevant

        return all_players[:20]

    def _score_and_filter_players(self, players, query):
        """
        Advanced search algorithm with fuzzy matching and relevance scoring

        Scoring criteria:
        - Exact name match: 100 points
        - Name starts with query: 80 points
        - Name contains query: 50 points
        - Fuzzy match (edit distance): 30-60 points
        - Word boundary match: +20 points
        - Recent/active players: +10 points
        """
        query_lower = query.lower().strip()
        query_parts = query_lower.split()

        scored_results = []

        for player in players:
            name = player.get('name', '')
            name_lower = name.lower()
            score = 0

            # Exact match
            if name_lower == query_lower:
                score = 100
            # Name starts with query
            elif name_lower.startswith(query_lower):
                score = 80
            # Name contains query as substring
            elif query_lower in name_lower:
                score = 50
            else:
                # Fuzzy matching with word boundaries
                name_parts = name_lower.split()

                # Check if any name part starts with any query part
                for query_part in query_parts:
                    for name_part in name_parts:
                        if name_part.startswith(query_part):
                            score += 30
                        elif query_part in name_part:
                            score += 20

                # Calculate Levenshtein-like score
                if len(query_lower) >= 3:
                    fuzzy_score = self._fuzzy_match_score(name_lower, query_lower)
                    score += fuzzy_score

            # Bonus for word boundary matches (e.g., "T Brady" matches "Tom Brady")
            if self._matches_word_boundaries(name_lower, query_parts):
                score += 20

            # Bonus for active status
            if player.get('status', '').upper() == 'ACTIVE':
                score += 10

            # Only include results with some relevance
            if score > 15:
                scored_results.append({
                    'player': player,
                    'score': score,
                    'name': name
                })

        # Sort by score (descending) then by name (alphabetically)
        scored_results.sort(key=lambda x: (-x['score'], x['name']))

        return [item['player'] for item in scored_results]

    def _fuzzy_match_score(self, text, pattern):
        """Calculate fuzzy match score based on character proximity"""
        if not pattern:
            return 0

        score = 0
        pattern_idx = 0

        for i, char in enumerate(text):
            if pattern_idx < len(pattern) and char == pattern[pattern_idx]:
                # Characters match in sequence
                score += max(30 - pattern_idx, 5)
                pattern_idx += 1

        # Penalize if pattern wasn't fully matched
        if pattern_idx < len(pattern):
            score = max(0, score - (len(pattern) - pattern_idx) * 10)

        return min(score, 60)

    def _matches_word_boundaries(self, name, query_parts):
        """Check if query parts match word boundaries (e.g., initials)"""
        name_words = name.split()

        if len(query_parts) > 1 and len(name_words) >= len(query_parts):
            # Check if query parts match first letters of name words
            matches = 0
            for i, query_part in enumerate(query_parts):
                if i < len(name_words):
                    if name_words[i].startswith(query_part):
                        matches += 1

            # If most query parts match word starts, return True
            return matches >= len(query_parts) * 0.7

        return False

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
