import requests
import os
import logging

logger = logging.getLogger(__name__)

class FantasyAPIClient:
    # API request timeout in seconds
    REQUEST_TIMEOUT = 10

    def __init__(self):
        # Use API v2 by default, fallback to v1 if specified
        api_version = os.getenv('API_VERSION', 'v2')
        self.base_url = os.getenv('API_BASE_URL', f'https://nfl.wearemachina.com/api/{api_version}')
        self.api_key = os.getenv('API_KEY')
        self.api_version = api_version
        self._teams_cache = None
        self._schedule_cache = {}
        
        logger.info(f"FantasyAPIClient initialized with API {api_version}: {self.base_url}")

    def _get_headers(self, include_api_key=True):
        """Get request headers, including API key by default for unlimited access"""
        headers = {'Content-Type': 'application/json'}
        # Always include API key if available (provides unlimited rate limit)
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
                    headers=self._get_headers(),
                    timeout=self.REQUEST_TIMEOUT
                )
                response.raise_for_status()
                teams = response.json().get('data', [])
                # Create map of team_id -> abbreviation
                self._teams_cache = {team['id']: team['abbreviation'] for team in teams}
            except requests.Timeout:
                logger.error("Timeout loading teams cache")
                self._teams_cache = {}
            except Exception as e:
                logger.error(f"Failed to load teams cache: {e}")
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
        try:
            response = requests.get(
                f'{self.base_url}/players/{player_id}',
                headers=self._get_headers(),
                timeout=self.REQUEST_TIMEOUT
            )
            response.raise_for_status()
            player = response.json()
            # Enrich with team abbreviation if it's in the data wrapper
            if 'data' in player:
                player['data'] = self._enrich_player_with_team(player['data'])
            else:
                player = self._enrich_player_with_team(player)
            return player
        except requests.Timeout:
            logger.error(f"Timeout getting player data for {player_id}")
            return None
        except Exception as e:
            logger.error(f"Failed to get player data for {player_id}: {e}")
            return None

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

        try:
            # First request to get total count
            params = {'limit': limit, 'offset': offset}
            if position:
                params['position'] = position

            response = requests.get(
                f'{self.base_url}/players',
                params=params,
                headers=self._get_headers(),
                timeout=self.REQUEST_TIMEOUT
            )
            response.raise_for_status()
            data = response.json()
            all_players.extend(data.get('data', []))
            total = data.get('meta', {}).get('total', 0)

            # Fetch remaining pages (when searching by query, fetch all for accurate results)
            max_fetch = total if query else min(total, 1000 if not position else total)
            while offset + limit < max_fetch:
                offset += limit
                params['offset'] = offset
                response = requests.get(
                    f'{self.base_url}/players',
                    params=params,
                    headers=self._get_headers(),
                    timeout=self.REQUEST_TIMEOUT
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
        except requests.Timeout:
            logger.error(f"Timeout searching for players: query={query}, position={position}")
            return []
        except Exception as e:
            logger.error(f"Failed to search players: {e}")
            return []

    def _search_team_defenses(self, query):
        """Search for team defenses"""
        try:
            response = requests.get(
                f'{self.base_url}/teams',
                params={'limit': 100},
                headers=self._get_headers(),
                timeout=self.REQUEST_TIMEOUT
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
        except requests.Timeout:
            logger.error(f"Timeout searching for team defenses: query={query}")
            return []
        except Exception as e:
            logger.error(f"Failed to search team defenses: {e}")
            return []

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
        try:
            response = requests.get(
                f'{self.base_url}/teams/{team_id}',
                headers=self._get_headers(),
                timeout=self.REQUEST_TIMEOUT
            )
            response.raise_for_status()
            return response.json()
        except requests.Timeout:
            logger.error(f"Timeout getting defense stats for team {team_id}")
            return None
        except Exception as e:
            logger.error(f"Failed to get defense stats for team {team_id}: {e}")
            return None

    def get_weather_data(self, location):
        """Get current weather for a location"""
        try:
            response = requests.get(
                f'{self.base_url}/weather/current',
                params={'location': location},
                headers=self._get_headers(),
                timeout=self.REQUEST_TIMEOUT
            )
            response.raise_for_status()
            return response.json()
        except requests.Timeout:
            logger.error(f"Timeout getting weather data for {location}")
            return None
        except Exception as e:
            logger.error(f"Failed to get weather data for {location}: {e}")
            return None

    def get_player_career_stats(self, player_id):
        """Get career statistics for a player"""
        try:
            response = requests.get(
                f'{self.base_url}/players/{player_id}/career',
                headers=self._get_headers(),
                timeout=self.REQUEST_TIMEOUT
            )
            response.raise_for_status()
            return response.json()
        except requests.Timeout:
            logger.error(f"Timeout getting career stats for player {player_id}")
            return None
        except Exception as e:
            logger.error(f"Failed to get career stats for player {player_id}: {e}")
            return None

    def get_player_recent_games(self, player_id, limit=20):
        """
        Get recent game logs for a player.

        Args:
            player_id: Player ID
            limit: Number of recent games to fetch (default 20)

        Returns:
            List of recent game stats
        """
        import logging
        logger = logging.getLogger(__name__)

        try:
            response = requests.get(
                f'{self.base_url}/players/{player_id}/games',
                params={'limit': limit},
                headers=self._get_headers(),
                timeout=10
            )
            response.raise_for_status()
            games = response.json().get('data', [])
            logger.info(f"Fetched {len(games)} recent games for player {player_id}")
            return games
        except Exception as e:
            logger.error(f"Failed to fetch recent games for player {player_id}: {e}")
            return []

    def get_weekly_schedule(self, season, week):
        """
        Get NFL schedule for a specific week.
        Returns matchups showing which teams are playing each other.
        """
        import logging
        logger = logging.getLogger(__name__)

        cache_key = f"{season}_{week}"
        if cache_key in self._schedule_cache:
            return self._schedule_cache[cache_key]

        try:
            response = requests.get(
                f'{self.base_url}/games',
                params={'season': season, 'week': week, 'limit': 100},
                headers=self._get_headers(),
                timeout=self.REQUEST_TIMEOUT
            )
            response.raise_for_status()
            games = response.json().get('data') or []
            if games is None:
                games = []
            logger.info(f"Fetched {len(games)} games for {season} Week {week}")
            self._schedule_cache[cache_key] = games
            return games
        except Exception as e:
            logger.error(f"Failed to fetch schedule for {season} Week {week}: {e}")
            return []

    def get_team_opponent(self, team_abbr, season, week):
        """
        Get the opponent team for a given team in a specific week.
        Returns opponent team abbreviation or None.
        """
        games = self.get_weekly_schedule(season, week)
        if not games:
            return None

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
                headers=self._get_headers(),
                timeout=self.REQUEST_TIMEOUT
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
        except requests.Timeout:
            logger.error(f"Timeout getting player {player_id} stats vs team {opponent_team_abbr}")
            return None
        except Exception as e:
            logger.error(f"Failed to fetch player vs team stats: {e}")
            return None

    def get_defensive_coordinator(self, team_abbr, season=2024):
        """
        Get defensive coordinator for a team.
        Attempts to fetch from API, falls back to cached data if unavailable.
        """
        try:
            # Try to fetch from coaching staff API endpoint
            response = requests.get(
                f'{self.base_url}/teams/{team_abbr}/coaches',
                params={'season': season},
                headers=self._get_headers(),
                timeout=self.REQUEST_TIMEOUT
            )
            response.raise_for_status()
            coaches_data = response.json().get('data', {})
            
            # Look for defensive coordinator
            for coach in coaches_data.get('coaches', []):
                if 'defensive coordinator' in coach.get('position', '').lower():
                    return coach.get('name', 'Unknown')
                    
        except requests.Timeout:
            logger.warning(f"Timeout fetching coaching staff for {team_abbr}")
        except Exception as e:
            logger.debug(f"Could not fetch coaching staff from API for {team_abbr}: {e}")
        
        # Fallback to 2024 cached mapping (updated periodically)
        dc_mapping_2024 = {
            'SF': 'Nick Sorensen',
            'BAL': 'Zach Orr', 
            'BUF': 'Bobby Babich',
            'DAL': 'Mike Zimmer',
            'PIT': 'Teryl Austin',
            'CLE': 'Jim Schwartz',
            'NYJ': 'Jeff Ulbrich',
            'KC': 'Steve Spagnuolo',
            'PHI': 'Vic Fangio',
            'MIA': 'Anthony Weaver',
            'DET': 'Aaron Glenn',
            'GB': 'Jeff Hafley',
            'MIN': 'Brian Flores',
            'HOU': 'Matt Burke'
        }
        
        coordinator = dc_mapping_2024.get(team_abbr)
        if coordinator:
            logger.debug(f"Using cached DC for {team_abbr}: {coordinator}")
        return coordinator or 'Unknown'

    def get_key_defensive_players(self, team_abbr, position_group='ALL'):
        """
        Get key defensive players for a team.

        Args:
            team_abbr: Team abbreviation
            position_group: 'DL' (pass rush), 'LB', 'DB' (coverage), or 'ALL'

        Returns:
            List of key defensive player names
        """
        try:
            # Try to fetch from team roster API
            response = requests.get(
                f'{self.base_url}/teams/{team_abbr}/players',
                params={'position_side': 'defense'},
                headers=self._get_headers(),
                timeout=self.REQUEST_TIMEOUT
            )
            response.raise_for_status()
            roster_data = response.json().get('data', [])
            
            # Filter by position group if specified
            position_map = {
                'DL': ['DE', 'DT', 'NT'],
                'LB': ['LB', 'MLB', 'OLB', 'ILB'],
                'DB': ['CB', 'S', 'SS', 'FS', 'DB']
            }
            
            if position_group != 'ALL' and position_group in position_map:
                target_positions = position_map[position_group]
                filtered_players = [
                    p.get('name') for p in roster_data 
                    if p.get('position') in target_positions
                ]
                # Return top 3 by some metric
                return filtered_players[:3] if filtered_players else []
            else:
                # Return top defenders across all positions
                all_defenders = [p.get('name') for p in roster_data]
                return all_defenders[:5] if all_defenders else []
                
        except requests.Timeout:
            logger.warning(f"Timeout fetching roster for {team_abbr}")
        except Exception as e:
            logger.debug(f"Could not fetch roster from API for {team_abbr}: {e}")
        
        # Fallback to cached 2024 key defenders (top impact players)
        key_defenders_2024 = {
            'SF': {
                'DL': ['Nick Bosa', 'Javon Hargrave'],
                'LB': ['Fred Warner', 'Dre Greenlaw'],
                'DB': ['Charvarius Ward', 'Talanoa Hufanga']
            },
            'BAL': {
                'DL': ['Justin Madubuike'],
                'LB': ['Roquan Smith', 'Kyle Van Noy'],
                'DB': ['Marlon Humphrey', 'Kyle Hamilton']
            },
            'BUF': {
                'DL': ['Ed Oliver', 'Von Miller'],
                'LB': ['Terrel Bernard', 'Matt Milano'],
                'DB': ['Tre\'Davious White', 'Jordan Poyer']
            },
            'DAL': {
                'DL': ['Micah Parsons', 'DeMarcus Lawrence'],
                'LB': ['Leighton Vander Esch'],
                'DB': ['Trevon Diggs', 'DaRon Bland']
            },
            'PIT': {
                'DL': ['T.J. Watt', 'Cameron Heyward'],
                'LB': ['Alex Highsmith'],
                'DB': ['Minkah Fitzpatrick', 'Patrick Peterson']
            },
            'KC': {
                'DL': ['Chris Jones', 'George Karlaftis'],
                'LB': ['Nick Bolton'],
                'DB': ['Trent McDuffie', 'Justin Reid']
            }
        }

        team_defense = key_defenders_2024.get(team_abbr, {})

        if position_group == 'ALL':
            all_players = []
            for group_players in team_defense.values():
                all_players.extend(group_players)
            logger.debug(f"Using cached key defenders for {team_abbr} (all positions)")
            return all_players

        players = team_defense.get(position_group, [])
        if players:
            logger.debug(f"Using cached key defenders for {team_abbr} ({position_group})")
        return players

    def get_team_roster(self, team_abbr, season=2024):
        """
        Get complete roster for a team, focusing on top offensive players.

        Args:
            team_abbr: Team abbreviation (e.g., 'KC', 'WSH')
            season: Season year

        Returns:
            Dictionary with offensive players by position
        """
        import logging
        logger = logging.getLogger(__name__)

        try:
            # Get team_id from abbreviation
            teams_map = self._get_teams()
            abbr_to_id = {abbr: tid for tid, abbr in teams_map.items()}
            team_id = abbr_to_id.get(team_abbr)

            if not team_id:
                logger.warning(f"Team not found: {team_abbr}")
                return None

            # Fetch team roster
            response = requests.get(
                f'{self.base_url}/teams/{team_id}/players',
                params={'season': season, 'limit': 100},
                headers=self._get_headers(),
                timeout=self.REQUEST_TIMEOUT
            )
            response.raise_for_status()
            players = response.json().get('data', [])

            if not players:
                logger.warning(f"No roster data for {team_abbr}")
                return None

            # Organize by position (focus on offensive skill positions)
            roster = {
                'QB': [],
                'RB': [],
                'WR': [],
                'TE': []
            }

            for player in players:
                pos = player.get('position', '')
                name = player.get('name', '')

                if pos in roster and name:
                    roster[pos].append({
                        'name': name,
                        'position': pos,
                        'status': player.get('status', 'unknown')
                    })

            # Limit to top players per position (most relevant)
            for pos in roster:
                roster[pos] = roster[pos][:3]  # Top 3 per position

            logger.info(f"Fetched roster for {team_abbr}: {sum(len(v) for v in roster.values())} players")
            return roster

        except Exception as e:
            logger.error(f"Failed to fetch roster for {team_abbr}: {e}")
            return None

    def get_team_defensive_rankings(self, team_abbr, season=2024):
        """
        Get comprehensive defensive stats and rankings for a team.

        Args:
            team_abbr: Team abbreviation
            season: Season year

        Returns:
            Dictionary with defensive stats and rankings
        """
        import logging
        logger = logging.getLogger(__name__)

        try:
            # First, get team ID from abbreviation
            teams = self._get_teams()
            team_id = None
            for tid, abbr in teams.items():
                if abbr == team_abbr:
                    team_id = tid
                    break

            if not team_id:
                logger.warning(f"Team ID not found for {team_abbr}")
                return None

            # Try new defensive stats endpoint
            response = requests.get(
                f'{self.base_url}/teams/{team_id}/defense/stats',
                params={'season': season},
                headers=self._get_headers(),
                timeout=self.REQUEST_TIMEOUT
            )
            response.raise_for_status()
            stats_data = response.json()

            # Extract stats from response (should have 'data' wrapper)
            stats = stats_data.get('data', {})

            if not stats:
                logger.warning(f"No data in defensive stats response for {team_abbr}")
                return None

            # Extract defensive metrics using exact field names from API spec
            defensive_stats = {
                'points_allowed_per_game': stats.get('points_allowed_per_game', 0),
                'yards_allowed_per_game': stats.get('yards_allowed_per_game', 0),
                'pass_yards_allowed_per_game': stats.get('pass_yards_allowed_per_game', 0),
                'rush_yards_allowed_per_game': stats.get('rush_yards_allowed_per_game', 0),
                'sacks': stats.get('sacks', 0),
                'interceptions': stats.get('interceptions', 0),
                'forced_fumbles': stats.get('forced_fumbles', 0),
                'defensive_rank': stats.get('defensive_rank', 16),
                'pass_defense_rank': stats.get('pass_defense_rank', 16),
                'rush_defense_rank': stats.get('rush_defense_rank', 16),
                # Additional fields from API
                'points_allowed': stats.get('points_allowed', 0),
                'yards_allowed': stats.get('yards_allowed', 0),
                'interception_touchdowns': stats.get('interception_touchdowns', 0),
                'fumble_recoveries': stats.get('fumble_recoveries', 0),
                'third_down_percentage': stats.get('third_down_percentage', 0),
                'red_zone_percentage': stats.get('red_zone_percentage', 0)
            }

            logger.info(f"Fetched defensive stats for {team_abbr} from API: {defensive_stats}")
            return defensive_stats

        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                logger.warning(f"Defensive stats endpoint not found for {team_abbr} (404)")
            else:
                logger.error(f"HTTP error fetching defensive rankings for {team_abbr}: {e}")
            return None
        except Exception as e:
            logger.error(f"Failed to fetch defensive rankings for {team_abbr}: {e}")
            return None

    def get_player_injury_history(self, player_id):
        """
        Get injury history for a player.

        Args:
            player_id: Player ID

        Returns:
            List of injury records with dates and descriptions
        """
        import logging
        logger = logging.getLogger(__name__)

        try:
            response = requests.get(
                f'{self.base_url}/players/{player_id}/injuries',
                headers=self._get_headers(),
                timeout=self.REQUEST_TIMEOUT
            )
            response.raise_for_status()
            injuries = response.json().get('data', [])
            logger.info(f"Fetched {len(injuries)} injury records for player {player_id}")
            return injuries
        except Exception as e:
            logger.error(f"Failed to fetch injury history for player {player_id}: {e}")
            return []

    def get_weather_forecast(self, location, date=None):
        """
        Get weather forecast for upcoming games.

        Args:
            location: Stadium location or team abbreviation
            date: Optional date for forecast (YYYY-MM-DD)

        Returns:
            Weather forecast data
        """
        import logging
        logger = logging.getLogger(__name__)

        try:
            params = {'location': location}
            if date:
                params['date'] = date

            response = requests.get(
                f'{self.base_url}/weather/forecast',
                params=params,
                headers=self._get_headers(),
                timeout=self.REQUEST_TIMEOUT
            )
            response.raise_for_status()
            forecast = response.json().get('data', {})
            logger.info(f"Fetched weather forecast for {location}")
            return forecast
        except Exception as e:
            logger.error(f"Failed to fetch weather forecast for {location}: {e}")
            return None

    def get_game_stats(self, game_id):
        """
        Get detailed statistics for a specific game.

        Args:
            game_id: Game ID

        Returns:
            Comprehensive game statistics
        """
        import logging
        logger = logging.getLogger(__name__)

        try:
            response = requests.get(
                f'{self.base_url}/stats/game/{game_id}',
                headers=self._get_headers(),
                timeout=self.REQUEST_TIMEOUT
            )
            response.raise_for_status()
            stats = response.json().get('data', {})
            logger.info(f"Fetched stats for game {game_id}")
            return stats
        except Exception as e:
            logger.error(f"Failed to fetch stats for game {game_id}: {e}")
            return None

    def get_stat_leaders(self, category='passing_yards', season=2024, limit=10):
        """
        Get statistical leaders across categories.

        Args:
            category: Stat category (passing_yards, rushing_yards, receiving_yards, etc.)
            season: Season year
            limit: Number of leaders to return

        Returns:
            List of top players in the category
        """
        import logging
        logger = logging.getLogger(__name__)

        try:
            response = requests.get(
                f'{self.base_url}/stats/leaders',
                params={'category': category, 'season': season, 'limit': limit},
                headers=self._get_headers(),
                timeout=self.REQUEST_TIMEOUT
            )
            response.raise_for_status()
            leaders = response.json().get('data', [])
            logger.info(f"Fetched {len(leaders)} leaders for {category}")
            return leaders
        except Exception as e:
            logger.error(f"Failed to fetch stat leaders for {category}: {e}")
            return []

    def ai_garden_query(self, query):
        """
        Natural language query to AI Garden for data insights.

        Args:
            query: Natural language question

        Returns:
            AI-generated response with data insights
        """
        import logging
        logger = logging.getLogger(__name__)

        try:
            response = requests.post(
                f'{self.base_url}/garden/query',
                json={'query': query},
                headers=self._get_headers(include_api_key=True),
                timeout=self.REQUEST_TIMEOUT
            )
            response.raise_for_status()
            result = response.json().get('data', {})
            logger.info(f"AI Garden query successful: {query[:50]}...")
            return result
        except Exception as e:
            logger.error(f"AI Garden query failed: {e}")
            return None

    def ai_garden_enrich_player(self, player_id):
        """
        Use AI to enrich player data with advanced insights.

        Args:
            player_id: Player ID

        Returns:
            AI-enriched player data
        """
        import logging
        logger = logging.getLogger(__name__)

        try:
            response = requests.post(
                f'{self.base_url}/garden/enrich/player/{player_id}',
                headers=self._get_headers(include_api_key=True),
                timeout=self.REQUEST_TIMEOUT
            )
            response.raise_for_status()
            enriched = response.json().get('data', {})
            logger.info(f"AI enrichment successful for player {player_id}")
            return enriched
        except Exception as e:
            logger.error(f"AI enrichment failed for player {player_id}: {e}")
            return None

    # ========================================
    # API V2 - ADVANCED STATS & ANALYTICS
    # ========================================

    def get_player_advanced_stats(self, player_id, season=2024, week=None, stat_type=None):
        """
        Get advanced stats for a player (Next Gen Stats, EPA, CPOE).
        
        API v2 endpoint: GET /api/v2/players/:id/advanced-stats
        
        Args:
            player_id: Player ID
            season: Season year (default: 2024)
            week: Optional specific week number
            stat_type: Optional filter by stat type (nextgen, epa, cpoe, air_yards, yac)
        
        Returns:
            Advanced statistics including:
            - Next Gen Stats (air yards, completion above expectation, etc.)
            - EPA (Expected Points Added)
            - CPOE (Completion Percentage Over Expected)
            - Rushing/receiving yards after catch
            - Route running metrics
        """
        import logging
        logger = logging.getLogger(__name__)
        
        try:
            params = {'season': season}
            if week:
                params['week'] = week
            if stat_type:
                params['stat_type'] = stat_type
            
            response = requests.get(
                f'{self.base_url}/players/{player_id}/advanced-stats',
                params=params,
                headers=self._get_headers(),
                timeout=self.REQUEST_TIMEOUT
            )
            response.raise_for_status()
            stats = response.json().get('data', {})
            logger.info(f"Fetched advanced stats for player {player_id} (season: {season}, week: {week})")
            return stats
        except Exception as e:
            logger.error(f"Failed to fetch advanced stats for player {player_id}: {e}")
            return None

    def get_game_play_by_play(self, game_id):
        """
        Get detailed play-by-play data for a game.
        
        API v2 endpoint: GET /api/v2/games/:id/play-by-play
        
        Args:
            game_id: Game ID
        
        Returns:
            Complete play-by-play data including:
            - Drive information
            - Down and distance
            - Play outcomes
            - Player involvement
            - Time remaining
            - Field position
        """
        import logging
        logger = logging.getLogger(__name__)
        
        try:
            response = requests.get(
                f'{self.base_url}/games/{game_id}/play-by-play',
                headers=self._get_headers(),
                timeout=self.REQUEST_TIMEOUT
            )
            response.raise_for_status()
            plays = response.json().get('data', [])
            logger.info(f"Fetched {len(plays)} plays for game {game_id}")
            return plays
        except Exception as e:
            logger.error(f"Failed to fetch play-by-play for game {game_id}: {e}")
            return []

    def get_game_scoring_plays(self, game_id):
        """
        Get all scoring plays from a game.
        
        API v2 endpoint: GET /api/v2/games/:id/scoring-plays
        
        Args:
            game_id: Game ID
        
        Returns:
            List of scoring plays with details:
            - Play description
            - Players involved
            - Score change
            - Time
            - Quarter
        """
        import logging
        logger = logging.getLogger(__name__)
        
        try:
            response = requests.get(
                f'{self.base_url}/games/{game_id}/scoring-plays',
                headers=self._get_headers(),
                timeout=self.REQUEST_TIMEOUT
            )
            response.raise_for_status()
            scoring = response.json().get('data', [])
            logger.info(f"Fetched {len(scoring)} scoring plays for game {game_id}")
            return scoring
        except Exception as e:
            logger.error(f"Failed to fetch scoring plays for game {game_id}: {e}")
            return []

    def get_team_injuries_v2(self, team_id):
        """
        Get current injury report for a team (enhanced v2 endpoint).
        
        API v2 endpoint: GET /api/v2/teams/:id/injuries
        
        Args:
            team_id: Team ID or abbreviation
        
        Returns:
            Detailed injury report with:
            - Player name and position
            - Injury type and body part
            - Status (Out, Doubtful, Questionable, Probable)
            - Last update timestamp
            - Expected return date (if available)
        """
        import logging
        logger = logging.getLogger(__name__)
        
        try:
            response = requests.get(
                f'{self.base_url}/teams/{team_id}/injuries',
                headers=self._get_headers(),
                timeout=self.REQUEST_TIMEOUT
            )
            response.raise_for_status()
            injuries = response.json().get('data', [])
            logger.info(f"Fetched {len(injuries)} injury reports for team {team_id}")
            return injuries
        except Exception as e:
            logger.error(f"Failed to fetch injuries for team {team_id}: {e}")
            return []

    def get_player_injuries_v2(self, player_id):
        """
        Get injury history and current status for a player (enhanced v2 endpoint).
        
        API v2 endpoint: GET /api/v2/players/:id/injuries
        
        Args:
            player_id: Player ID
        
        Returns:
            Comprehensive injury data:
            - Current injury status
            - Historical injuries
            - Recovery timeline
            - Practice participation
        """
        import logging
        logger = logging.getLogger(__name__)
        
        try:
            response = requests.get(
                f'{self.base_url}/players/{player_id}/injuries',
                headers=self._get_headers(),
                timeout=self.REQUEST_TIMEOUT
            )
            response.raise_for_status()
            injuries = response.json().get('data', [])
            logger.info(f"Fetched {len(injuries)} injury records for player {player_id}")
            return injuries
        except Exception as e:
            logger.error(f"Failed to fetch injuries for player {player_id}: {e}")
            return []

    def get_team_schedule_v2(self, team_id, season=2024):
        """
        Get complete season schedule for a team (enhanced v2 endpoint).
        
        API v2 endpoint: GET /api/v2/teams/:id/schedule
        
        Args:
            team_id: Team ID or abbreviation
            season: Season year
        
        Returns:
            Complete schedule with:
            - Game dates and times
            - Opponents
            - Home/away status
            - Game results (if completed)
            - Bye weeks
        """
        import logging
        logger = logging.getLogger(__name__)
        
        try:
            response = requests.get(
                f'{self.base_url}/teams/{team_id}/schedule',
                params={'season': season},
                headers=self._get_headers(),
                timeout=self.REQUEST_TIMEOUT
            )
            response.raise_for_status()
            schedule = response.json().get('data', [])
            logger.info(f"Fetched schedule for team {team_id} ({season}): {len(schedule)} games")
            return schedule
        except Exception as e:
            logger.error(f"Failed to fetch schedule for team {team_id}: {e}")
            return []

    def get_defense_rankings_v2(self, category='overall', season=2024):
        """
        Get defensive rankings across the league (enhanced v2 endpoint).
        
        API v2 endpoint: GET /api/v2/defense/rankings
        
        Args:
            category: Ranking category (overall, pass, rush, scoring, etc.)
            season: Season year
        
        Returns:
            League-wide defensive rankings with:
            - Team rankings
            - Statistical breakdowns
            - Strength of schedule adjustments
            - Advanced metrics (EPA allowed, success rate, etc.)
        """
        import logging
        logger = logging.getLogger(__name__)
        
        try:
            response = requests.get(
                f'{self.base_url}/defense/rankings',
                params={'category': category, 'season': season},
                headers=self._get_headers(),
                timeout=self.REQUEST_TIMEOUT
            )
            response.raise_for_status()
            rankings = response.json().get('data', [])
            logger.info(f"Fetched defensive rankings for {category} ({season}): {len(rankings)} teams")
            return rankings
        except Exception as e:
            logger.error(f"Failed to fetch defense rankings ({category}): {e}")
            return []

    def get_standings_v2(self, season=2024, division=None):
        """
        Get league standings (enhanced v2 endpoint).
        
        API v2 endpoint: GET /api/v2/standings
        
        Args:
            season: Season year
            division: Optional division filter (AFC East, NFC West, etc.)
        
        Returns:
            Current standings with:
            - Win/loss records
            - Division/conference standings
            - Playoff positioning
            - Strength of victory/schedule
            - Tiebreaker info
        """
        import logging
        logger = logging.getLogger(__name__)
        
        try:
            params = {'season': season}
            if division:
                params['division'] = division
            
            response = requests.get(
                f'{self.base_url}/standings',
                params=params,
                headers=self._get_headers(),
                timeout=self.REQUEST_TIMEOUT
            )
            response.raise_for_status()
            standings = response.json().get('data', [])
            logger.info(f"Fetched standings for {season} (division: {division})")
            return standings
        except Exception as e:
            logger.error(f"Failed to fetch standings ({season}): {e}")
            return []

    def ai_predict_game_v2(self, game_id):
        """
        Get AI-powered game prediction (enhanced v2 endpoint with Claude).
        
        API v2 endpoint: GET /api/v2/ai/predict/game/:id
        
        Args:
            game_id: Game ID
        
        Returns:
            Comprehensive AI prediction:
            - Win probabilities for each team
            - Predicted final score
            - Confidence level
            - Key factors analysis
            - Player impact projections
            - Claude-powered insights
        """
        import logging
        logger = logging.getLogger(__name__)
        
        try:
            response = requests.get(
                f'{self.base_url}/ai/predict/game/{game_id}',
                headers=self._get_headers(include_api_key=True),
                timeout=30  # AI endpoints may take longer
            )
            response.raise_for_status()
            prediction = response.json().get('data', {})
            logger.info(f"Fetched AI game prediction for game {game_id}")
            return prediction
        except Exception as e:
            logger.error(f"Failed to fetch AI game prediction for {game_id}: {e}")
            return None

    def ai_predict_player_v2(self, player_id, game_context=None):
        """
        Get AI-powered player performance prediction (enhanced v2 endpoint with Claude).
        
        API v2 endpoint: GET /api/v2/ai/predict/player/:id
        
        Args:
            player_id: Player ID
            game_context: Optional dict with game context (opponent, weather, etc.)
        
        Returns:
            AI-powered prediction:
            - Projected fantasy points
            - Statistical projections (yards, TDs, receptions, etc.)
            - Confidence score
            - Risk factors
            - Opportunity analysis
            - Claude-powered narrative insights
        """
        import logging
        logger = logging.getLogger(__name__)
        
        try:
            params = game_context if game_context else {}
            
            response = requests.get(
                f'{self.base_url}/ai/predict/player/{player_id}',
                params=params,
                headers=self._get_headers(include_api_key=True),
                timeout=30  # AI endpoints may take longer
            )
            response.raise_for_status()
            prediction = response.json().get('data', {})
            logger.info(f"Fetched AI player prediction for player {player_id}")
            return prediction
        except Exception as e:
            logger.error(f"Failed to fetch AI player prediction for {player_id}: {e}")
            return None

    def ai_player_insights_v2(self, player_id):
        """
        Get comprehensive AI insights for a player (enhanced v2 endpoint with Claude).
        
        API v2 endpoint: GET /api/v2/ai/insights/player/:id
        
        Args:
            player_id: Player ID
        
        Returns:
            Deep AI analysis:
            - Performance trends
            - Strengths and weaknesses
            - Matchup advantages
            - Season outlook
            - Trade value assessment
            - Claude-powered narrative analysis
        """
        import logging
        logger = logging.getLogger(__name__)
        
        try:
            response = requests.get(
                f'{self.base_url}/ai/insights/player/{player_id}',
                headers=self._get_headers(include_api_key=True),
                timeout=30  # AI endpoints may take longer
            )
            response.raise_for_status()
            insights = response.json().get('data', {})
            logger.info(f"Fetched AI insights for player {player_id}")
            return insights
        except Exception as e:
            logger.error(f"Failed to fetch AI insights for player {player_id}: {e}")
            return None

    def ai_query_v2(self, query):
        """
        Natural language query to AI (enhanced v2 endpoint with Claude).
        
        API v2 endpoint: POST /api/v2/ai/query
        
        Args:
            query: Natural language question about NFL data
        
        Returns:
            AI-generated response with:
            - Direct answer to query
            - Supporting data and statistics
            - Relevant insights
            - Data visualizations (if applicable)
            - Claude-powered natural language response
        
        Examples:
            - "Who are the top 5 rushing leaders this season?"
            - "Compare Patrick Mahomes vs Josh Allen passing stats"
            - "Which defenses are best against tight ends?"
        """
        import logging
        logger = logging.getLogger(__name__)
        
        try:
            response = requests.post(
                f'{self.base_url}/ai/query',
                json={'query': query},
                headers=self._get_headers(include_api_key=True),
                timeout=30  # AI endpoints may take longer
            )
            response.raise_for_status()
            result = response.json().get('data', {})
            logger.info(f"AI query successful: {query[:50]}...")
            return result
        except Exception as e:
            logger.error(f"AI query failed ({query[:30]}...): {e}")
            return None

    def get_games_v2(self, season=None, week=None, team=None, status=None, limit=50):
        """
        Get games with enhanced filtering (v2 endpoint).
        
        API v2 endpoint: GET /api/v2/games
        
        Args:
            season: Filter by season year
            week: Filter by week number
            team: Filter by team ID or abbreviation
            status: Filter by game status (scheduled, live, final)
            limit: Max number of results
        
        Returns:
            List of games with enhanced metadata
        """
        import logging
        logger = logging.getLogger(__name__)
        
        try:
            params = {'limit': limit}
            if season:
                params['season'] = season
            if week:
                params['week'] = week
            if team:
                params['team'] = team
            if status:
                params['status'] = status
            
            response = requests.get(
                f'{self.base_url}/games',
                params=params,
                headers=self._get_headers(),
                timeout=self.REQUEST_TIMEOUT
            )
            response.raise_for_status()
            data = response.json()
            games = data.get('data', [])
            meta = data.get('meta', {})
            
            logger.info(f"Fetched {len(games)} games (total: {meta.get('total', 'unknown')})")
            return games
        except Exception as e:
            logger.error(f"Failed to fetch games: {e}")
            return []

    def get_game_details_v2(self, game_id):
        """
        Get comprehensive game details (v2 endpoint).
        
        API v2 endpoint: GET /api/v2/games/:id
        
        Args:
            game_id: Game ID
        
        Returns:
            Detailed game information including:
            - Teams and rosters
            - Score and quarter
            - Time remaining
            - Possession
            - Weather conditions
            - Stadium info
            - Betting lines (if available)
        """
        import logging
        logger = logging.getLogger(__name__)
        
        try:
            response = requests.get(
                f'{self.base_url}/games/{game_id}',
                headers=self._get_headers(),
                timeout=self.REQUEST_TIMEOUT
            )
            response.raise_for_status()
            game = response.json().get('data', {})
            logger.info(f"Fetched details for game {game_id}")
            return game
        except Exception as e:
            logger.error(f"Failed to fetch game details for {game_id}: {e}")
            return None

    def get_team_roster_v2(self, team_id, season=2024):
        """
        Get complete team roster (enhanced v2 endpoint).
        
        API v2 endpoint: GET /api/v2/teams/:id/roster
        
        Args:
            team_id: Team ID or abbreviation
            season: Season year
        
        Returns:
            Complete roster with enhanced player info:
            - Player details
            - Position depth chart
            - Contract info (if available)
            - Jersey numbers
            - Status
        """
        import logging
        logger = logging.getLogger(__name__)
        
        try:
            response = requests.get(
                f'{self.base_url}/teams/{team_id}/roster',
                params={'season': season},
                headers=self._get_headers(),
                timeout=self.REQUEST_TIMEOUT
            )
            response.raise_for_status()
            roster = response.json().get('data', [])
            logger.info(f"Fetched roster for team {team_id} ({season}): {len(roster)} players")
            return roster
        except Exception as e:
            logger.error(f"Failed to fetch roster for team {team_id}: {e}")
            return []

    # ========================================================================
    # Additional API v2 Methods - Complete Coverage
    # Added: October 2, 2025
    # ========================================================================

    def get_players_list_v2(self, position=None, status=None, team=None, limit=50, offset=0):
        """
        List players with flexible filtering (API v2).
        
        API v2 endpoint: GET /api/v2/players
        
        Args:
            position: Filter by position (QB, RB, WR, TE, etc.)
            status: Filter by status (active, injured, etc.)
            team: Filter by team UUID
            limit: Results per page (default: 50)
            offset: Pagination offset (default: 0)
        
        Returns:
            Paginated list of players matching filters
        """
        try:
            params = {'limit': limit, 'offset': offset}
            if position:
                params['position'] = position
            if status:
                params['status'] = status
            if team:
                params['team'] = team
            
            response = requests.get(
                f'{self.base_url}/players',
                params=params,
                headers=self._get_headers(),
                timeout=self.REQUEST_TIMEOUT
            )
            response.raise_for_status()
            data = response.json().get('data', [])
            logger.info(f"Fetched {len(data)} players (position={position}, status={status})")
            return data
        except Exception as e:
            logger.error(f"Failed to fetch players list: {e}")
            return []

    def get_teams_list_v2(self):
        """
        Get all 32 NFL teams (API v2).
        
        API v2 endpoint: GET /api/v2/teams
        
        Returns:
            List of all NFL teams with complete details:
            - Team ID
            - Name and abbreviation
            - City and stadium
            - Conference and division
            - Colors, logos
        """
        try:
            response = requests.get(
                f'{self.base_url}/teams',
                headers=self._get_headers(),
                timeout=self.REQUEST_TIMEOUT
            )
            response.raise_for_status()
            teams = response.json().get('data', [])
            logger.info(f"Fetched {len(teams)} NFL teams")
            return teams
        except Exception as e:
            logger.error(f"Failed to fetch teams list: {e}")
            return []

    def get_team_by_id_v2(self, team_id):
        """
        Get detailed team information (API v2).
        
        API v2 endpoint: GET /api/v2/teams/:id
        
        Args:
            team_id: Team UUID or abbreviation
        
        Returns:
            Detailed team information:
            - Basic info (name, city, abbreviation)
            - Stadium details
            - Colors and branding
            - Historical data
            - Current season record
        """
        try:
            response = requests.get(
                f'{self.base_url}/teams/{team_id}',
                headers=self._get_headers(),
                timeout=self.REQUEST_TIMEOUT
            )
            response.raise_for_status()
            team = response.json().get('data', {})
            logger.info(f"Fetched details for team {team_id}")
            return team
        except Exception as e:
            logger.error(f"Failed to fetch team details for {team_id}: {e}")
            return None

    def get_player_team_history_v2(self, player_id):
        """
        Get player's team history (API v2).
        
        API v2 endpoint: GET /api/v2/players/:id/history
        
        Args:
            player_id: Player UUID
        
        Returns:
            List of teams player has been on:
            - Team name and ID
            - Seasons played
            - Position(s) played
            - Notable achievements
        """
        try:
            response = requests.get(
                f'{self.base_url}/players/{player_id}/history',
                headers=self._get_headers(),
                timeout=self.REQUEST_TIMEOUT
            )
            response.raise_for_status()
            history = response.json().get('data', [])
            logger.info(f"Fetched team history for player {player_id}: {len(history)} teams")
            return history
        except Exception as e:
            logger.error(f"Failed to fetch player team history for {player_id}: {e}")
            return []

    def get_player_vs_defense_v2(self, player_id, defense_team_id, season=None, limit=10):
        """
        Get player's performance vs specific defense (API v2).
        
        API v2 endpoint: GET /api/v2/players/:id/vs-defense/:teamId
        
        Args:
            player_id: Player UUID
            defense_team_id: Defending team UUID
            season: Optional season filter
            limit: Max games to return
        
        Returns:
            Historical performance data:
            - Game-by-game stats vs this defense
            - Success rate
            - Fantasy points
            - Trends
        """
        try:
            params = {'limit': limit}
            if season:
                params['season'] = season
            
            response = requests.get(
                f'{self.base_url}/players/{player_id}/vs-defense/{defense_team_id}',
                params=params,
                headers=self._get_headers(),
                timeout=self.REQUEST_TIMEOUT
            )
            response.raise_for_status()
            performance = response.json().get('data', [])
            logger.info(f"Fetched vs defense stats for player {player_id} vs {defense_team_id}")
            return performance
        except Exception as e:
            logger.error(f"Failed to fetch player vs defense: {e}")
            return []

    def get_game_team_stats_v2(self, game_id):
        """
        Get team statistics for a specific game (API v2).
        
        API v2 endpoint: GET /api/v2/games/:id/stats
        
        Args:
            game_id: Game UUID
        
        Returns:
            Team-level statistics for the game:
            - Total yards
            - First downs
            - Time of possession
            - Turnovers
            - Red zone efficiency
            - Third down conversions
        """
        try:
            response = requests.get(
                f'{self.base_url}/games/{game_id}/stats',
                headers=self._get_headers(),
                timeout=self.REQUEST_TIMEOUT
            )
            response.raise_for_status()
            stats = response.json().get('data', {})
            logger.info(f"Fetched team stats for game {game_id}")
            return stats
        except Exception as e:
            logger.error(f"Failed to fetch game team stats for {game_id}: {e}")
            return None

    def get_player_by_id_v2(self, player_id):
        """
        Get detailed player information by ID (API v2).
        
        API v2 endpoint: GET /api/v2/players/:id
        
        This is an alias/wrapper for get_player_data that ensures v2 endpoint usage.
        
        Args:
            player_id: Player UUID
        
        Returns:
            Detailed player information
        """
        return self.get_player_data(player_id)

    def get_game_by_id_v2(self, game_id):
        """
        Get detailed game information by ID (API v2).
        
        API v2 endpoint: GET /api/v2/games/:id
        
        This is an alias/wrapper for get_game_details_v2.
        
        Args:
            game_id: Game UUID
        
        Returns:
            Detailed game information
        """
        return self.get_game_details_v2(game_id)

    def get_team_schedule_detailed_v2(self, team_id, season=2024):
        """
        Get detailed team schedule with game results (API v2).
        
        API v2 endpoint: GET /api/v2/teams/:id/schedule
        
        Args:
            team_id: Team UUID or abbreviation
            season: Season year
        
        Returns:
            Complete schedule with:
            - All games for the season
            - Results (if completed)
            - Opponent details
            - Game locations
        """
        try:
            response = requests.get(
                f'{self.base_url}/teams/{team_id}/schedule',
                params={'season': season},
                headers=self._get_headers(),
                timeout=self.REQUEST_TIMEOUT
            )
            response.raise_for_status()
            schedule = response.json().get('data', [])
            logger.info(f"Fetched schedule for team {team_id} ({season}): {len(schedule)} games")
            return schedule
        except Exception as e:
            logger.error(f"Failed to fetch schedule for team {team_id}: {e}")
            return []
