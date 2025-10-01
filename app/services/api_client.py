import requests
import os

class FantasyAPIClient:
    def __init__(self):
        self.base_url = os.getenv('API_BASE_URL', 'https://nfl.wearemachina.com/api/v1')
        self.api_key = os.getenv('API_KEY')
        self._teams_cache = None
        self._schedule_cache = {}

    def _get_headers(self, include_api_key=False):
        headers = {'Content-Type': 'application/json'}
        if include_api_key and self.api_key:
            headers['X-API-Key'] = self.api_key
        return headers

    def _get_teams(self):
        """Get and cache all teams"""
        if self._teams_cache is None:
            try:
                response = requests.get(
                    f'{self.base_url}/teams',
                    params={'limit': 100},
                    headers=self._get_headers()
                )
                response.raise_for_status()
                teams = response.json().get('data', [])
                # Create map of team_id -> abbreviation
                self._teams_cache = {team['id']: team['abbreviation'] for team in teams}
            except Exception as e:
                print(f"Warning: Failed to load teams cache: {e}")
                self._teams_cache = {}
        return self._teams_cache

    def _enrich_player_with_team(self, player):
        """Add team abbreviation to player data"""
        teams = self._get_teams()
        team_id = player.get('team_id')
        if team_id and team_id in teams:
            player['team'] = teams[team_id]
        elif not player.get('team'):
            # If no team found, use a default
            player['team'] = 'FA'  # Free Agent
        return player

    def get_player_data(self, player_id):
        """Get player details by ID"""
        response = requests.get(
            f'{self.base_url}/players/{player_id}',
            headers=self._get_headers()
        )
        response.raise_for_status()
        player = response.json()
        # Enrich with team abbreviation if it's in the data wrapper
        if 'data' in player:
            player['data'] = self._enrich_player_with_team(player['data'])
        else:
            player = self._enrich_player_with_team(player)
        return player

    def search_players(self, query, position=None):
        """Search for players by name and optionally filter by position"""
        # Special case: DEF means team defenses, not individual players
        if position == 'DEF':
            return self._search_team_defenses(query)

        # The API limits responses to 100 per request, so we need to paginate
        # Fetch ALL players for the position to ensure we don't miss anyone

        all_players = []
        limit = 100
        offset = 0

        # First request to get total count
        params = {'limit': limit, 'offset': offset}
        if position:
            params['position'] = position

        response = requests.get(
            f'{self.base_url}/players',
            params=params,
            headers=self._get_headers()
        )
        response.raise_for_status()
        data = response.json()
        all_players.extend(data.get('data', []))
        total = data.get('meta', {}).get('total', 0)

        # Fetch remaining pages (limit to 1000 total for performance)
        max_fetch = min(total, 1000 if not position else total)
        while offset + limit < max_fetch:
            offset += limit
            params['offset'] = offset
            response = requests.get(
                f'{self.base_url}/players',
                params=params,
                headers=self._get_headers()
            )
            response.raise_for_status()
            all_players.extend(response.json().get('data', []))

        # Enrich all players with team abbreviation
        all_players = [self._enrich_player_with_team(player) for player in all_players]

        # Advanced search with relevance scoring
        # This will further filter and rank results from the API
        if query and all_players:
            scored_players = self._score_and_filter_players(all_players, query)
            return scored_players[:20]  # Return top 20 most relevant

        return all_players[:20]

    def _search_team_defenses(self, query):
        """Search for team defenses"""
        response = requests.get(
            f'{self.base_url}/teams',
            params={'limit': 100},
            headers=self._get_headers()
        )
        response.raise_for_status()
        teams = response.json().get('data', [])

        # Convert teams to player-like format for consistency
        defenses = []
        for team in teams:
            defense = {
                'id': team['id'],
                'player_id': team['id'],
                'name': f"{team['city']} {team['name']}",
                'position': 'DEF',
                'team': team['abbreviation'],
                'status': 'active'
            }
            defenses.append(defense)

        # Filter by query if provided
        if query:
            query_lower = query.lower()
            defenses = [d for d in defenses if
                       query_lower in d['name'].lower() or
                       query_lower in d['team'].lower()]

        return defenses[:20]

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

                # Check each query part against each name part
                for query_part in query_parts:
                    best_part_score = 0
                    for name_part in name_parts:
                        # Exact word match
                        if name_part == query_part:
                            best_part_score = max(best_part_score, 40)
                        # Starts with
                        elif name_part.startswith(query_part):
                            best_part_score = max(best_part_score, 35)
                        # Contains
                        elif query_part in name_part:
                            best_part_score = max(best_part_score, 25)
                        # Edit distance check for misspellings
                        else:
                            edit_dist = self._levenshtein_distance(query_part, name_part)
                            # Allow up to 2 character differences for words > 4 chars
                            if len(query_part) > 4 and edit_dist <= 2:
                                best_part_score = max(best_part_score, 30 - (edit_dist * 5))
                            elif len(query_part) > 3 and edit_dist <= 1:
                                best_part_score = max(best_part_score, 25)

                    score += best_part_score

                # Calculate sequential fuzzy score for full name
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

    def _levenshtein_distance(self, s1, s2):
        """Calculate Levenshtein distance between two strings (edit distance)"""
        if len(s1) < len(s2):
            return self._levenshtein_distance(s2, s1)

        if len(s2) == 0:
            return len(s1)

        previous_row = range(len(s2) + 1)
        for i, c1 in enumerate(s1):
            current_row = [i + 1]
            for j, c2 in enumerate(s2):
                # Cost of insertions, deletions, or substitutions
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row

        return previous_row[-1]

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

    def get_weekly_schedule(self, season, week):
        """
        Get NFL schedule for a specific week.
        Returns matchups showing which teams are playing each other.
        """
        cache_key = f"{season}_{week}"
        if cache_key in self._schedule_cache:
            return self._schedule_cache[cache_key]

        try:
            response = requests.get(
                f'{self.base_url}/games',
                params={'season': season, 'week': week, 'limit': 100},
                headers=self._get_headers()
            )
            response.raise_for_status()
            games = response.json().get('data', [])
            self._schedule_cache[cache_key] = games
            return games
        except Exception as e:
            print(f"Failed to fetch schedule: {e}")
            return []

    def get_team_opponent(self, team_abbr, season, week):
        """
        Get the opponent team for a given team in a specific week.
        Returns opponent team abbreviation or None.
        """
        games = self.get_weekly_schedule(season, week)
        teams_map = self._get_teams()

        # Reverse map to get team_id from abbreviation
        abbr_to_id = {abbr: tid for tid, abbr in teams_map.items()}
        team_id = abbr_to_id.get(team_abbr)

        if not team_id:
            return None

        for game in games:
            home_team_id = game.get('home_team_id')
            away_team_id = game.get('away_team_id')

            if home_team_id == team_id:
                return teams_map.get(away_team_id)
            elif away_team_id == team_id:
                return teams_map.get(home_team_id)

        return None

    def get_player_stats_vs_team(self, player_id, opponent_team_abbr):
        """
        Get historical stats for a player against a specific team.
        Returns summary of performance in past matchups.
        """
        try:
            # Fetch player's game logs
            response = requests.get(
                f'{self.base_url}/players/{player_id}/games',
                params={'limit': 100},  # Last 100 games
                headers=self._get_headers()
            )
            response.raise_for_status()
            games = response.json().get('data', [])

            # Get team_id for opponent
            teams_map = self._get_teams()
            abbr_to_id = {abbr: tid for tid, abbr in teams_map.items()}
            opponent_team_id = abbr_to_id.get(opponent_team_abbr)

            if not opponent_team_id:
                return None

            # Filter games against this opponent
            vs_games = [g for g in games if g.get('opponent_team_id') == opponent_team_id]

            if not vs_games:
                return None

            # Calculate averages
            total_points = sum(g.get('fantasy_points', 0) for g in vs_games)
            avg_points = total_points / len(vs_games) if vs_games else 0

            return {
                'games_played': len(vs_games),
                'avg_fantasy_points': round(avg_points, 1),
                'total_fantasy_points': round(total_points, 1),
                'recent_games': vs_games[:3]  # Last 3 games vs this team
            }
        except Exception as e:
            print(f"Failed to fetch player vs team stats: {e}")
            return None
