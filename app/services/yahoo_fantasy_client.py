"""
Yahoo Fantasy Sports API Client

Fetches fantasy football data from Yahoo Fantasy Sports API:
- User's fantasy leagues
- Team rosters
- Player information
"""

import logging
import requests
from typing import List, Dict, Optional
import xml.etree.ElementTree as ET

logger = logging.getLogger(__name__)

YAHOO_FANTASY_BASE_URL = "https://fantasysports.yahooapis.com/fantasy/v2"


class YahooFantasyClient:
    """Client for Yahoo Fantasy Sports API"""

    def __init__(self, access_token: str):
        """
        Initialize Yahoo Fantasy API client

        Args:
            access_token: Valid Yahoo OAuth access token
        """
        self.access_token = access_token
        self.headers = {
            'Authorization': f'Bearer {access_token}',
            'Accept': 'application/json'
        }

    def get_user_leagues(self, season: int = 2024) -> List[Dict]:
        """
        Fetch all NFL fantasy leagues for the authenticated user

        Args:
            season: NFL season year (default: 2024)

        Returns:
            List of league dicts with keys: league_key, league_id, name, num_teams, scoring_type
        """
        try:
            # Yahoo API endpoint for user's leagues
            url = f"{YAHOO_FANTASY_BASE_URL}/users;use_login=1/games;game_keys=nfl/leagues"

            response = requests.get(
                url,
                headers=self.headers,
                timeout=10  # Required: 10 second timeout
            )

            response.raise_for_status()
            data = response.json()

            # Parse Yahoo's nested JSON structure
            leagues = []
            try:
                fantasy_content = data.get('fantasy_content', {})
                users = fantasy_content.get('users', {})

                # Yahoo returns users as dict with numeric keys
                for user_key in users:
                    if user_key == 'count':
                        continue

                    user_data = users[user_key]
                    games = user_data.get('games', {})

                    for game_key in games:
                        if game_key == 'count':
                            continue

                        game_data = games[game_key]
                        game_leagues = game_data.get('leagues', {})

                        for league_key in game_leagues:
                            if league_key == 'count':
                                continue

                            league = game_leagues[league_key]
                            league_info = league.get('league', league)

                            # Extract team key for this user
                            teams = league_info.get('teams', {})
                            team_key = None
                            team_name = None

                            for tk in teams:
                                if tk == 'count':
                                    continue
                                team = teams[tk].get('team', {})
                                team_key = team.get('team_key')
                                team_name = team.get('name')
                                break

                            leagues.append({
                                'league_key': league_info.get('league_key'),
                                'league_id': league_info.get('league_id'),
                                'name': league_info.get('name'),
                                'season': league_info.get('season'),
                                'num_teams': int(league_info.get('num_teams', 0)),
                                'scoring_type': league_info.get('scoring_type', 'standard'),
                                'team_key': team_key,
                                'team_name': team_name
                            })

            except (KeyError, AttributeError) as e:
                logger.error(f"Error parsing Yahoo leagues response: {e}")
                logger.debug(f"Response data: {data}")

            logger.info(f"Fetched {len(leagues)} Yahoo fantasy leagues")
            return leagues

        except requests.exceptions.Timeout:
            logger.error("Yahoo leagues API timed out")
            return []
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to fetch Yahoo leagues: {e}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error fetching leagues: {e}")
            return []

    def get_team_roster(self, team_key: str) -> Optional[Dict]:
        """
        Fetch roster for a specific Yahoo fantasy team

        Args:
            team_key: Yahoo team key (e.g., 'nfl.l.12345.t.1')

        Returns:
            Dict with team info and players list, or None on failure
        """
        try:
            url = f"{YAHOO_FANTASY_BASE_URL}/team/{team_key}/roster"

            response = requests.get(
                url,
                headers=self.headers,
                timeout=10
            )

            response.raise_for_status()
            data = response.json()

            # Parse roster data
            roster = {
                'team_key': team_key,
                'team_name': None,
                'league_name': None,
                'players': []
            }

            try:
                fantasy_content = data.get('fantasy_content', {})
                team_data = fantasy_content.get('team', {})

                # Extract team info
                if isinstance(team_data, list):
                    for item in team_data:
                        if isinstance(item, dict):
                            if 'name' in item:
                                roster['team_name'] = item['name']
                            if 'roster' in item:
                                roster_data = item['roster']
                                break
                else:
                    roster['team_name'] = team_data.get('name')
                    roster_data = team_data.get('roster', {})

                # Extract players from roster
                if '0' in roster_data:
                    roster_data = roster_data['0']

                players_data = roster_data.get('players', {})

                for player_key in players_data:
                    if player_key == 'count':
                        continue

                    player_obj = players_data[player_key]
                    player_info = player_obj.get('player', player_obj)

                    # Handle both list and dict player formats
                    if isinstance(player_info, list):
                        player_details = {}
                        for item in player_info:
                            if isinstance(item, dict):
                                player_details.update(item)
                        player_info = player_details

                    # Extract player data
                    player = {
                        'player_key': player_info.get('player_key'),
                        'player_id': player_info.get('player_id'),
                        'name': self._extract_player_name(player_info),
                        'position': self._extract_position(player_info),
                        'team': self._extract_team_abbr(player_info),
                        'selected_position': self._extract_selected_position(player_obj)
                    }

                    roster['players'].append(player)

            except (KeyError, AttributeError) as e:
                logger.error(f"Error parsing Yahoo roster response: {e}")
                logger.debug(f"Response data: {data}")

            logger.info(f"Fetched roster for team {team_key} with {len(roster['players'])} players")
            return roster

        except requests.exceptions.Timeout:
            logger.error(f"Yahoo roster API timed out for team {team_key}")
            return None
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to fetch Yahoo roster for team {team_key}: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error fetching roster: {e}")
            return None

    def _extract_player_name(self, player_info: Dict) -> str:
        """Extract player name from various Yahoo API formats"""
        if 'name' in player_info:
            name_obj = player_info['name']
            if isinstance(name_obj, dict):
                full = name_obj.get('full')
                if full:
                    return full
                first = name_obj.get('first', '')
                last = name_obj.get('last', '')
                return f"{first} {last}".strip()
            return str(name_obj)
        return "Unknown Player"

    def _extract_position(self, player_info: Dict) -> str:
        """Extract player position"""
        if 'display_position' in player_info:
            return player_info['display_position']
        if 'position' in player_info:
            return player_info['position']
        if 'eligible_positions' in player_info:
            positions = player_info['eligible_positions']
            if isinstance(positions, list) and positions:
                return positions[0]
            if isinstance(positions, dict):
                return positions.get('position', 'UNKNOWN')
        return 'UNKNOWN'

    def _extract_team_abbr(self, player_info: Dict) -> str:
        """Extract team abbreviation"""
        if 'editorial_team_abbr' in player_info:
            return player_info['editorial_team_abbr']
        if 'team_abbr' in player_info:
            return player_info['team_abbr']
        return 'FA'  # Free Agent

    def _extract_selected_position(self, player_obj: Dict) -> str:
        """Extract selected position (QB, RB1, WR2, FLEX, BN, etc.)"""
        if 'selected_position' in player_obj:
            sel_pos = player_obj['selected_position']
            if isinstance(sel_pos, dict):
                return sel_pos.get('position', 'BN')
            return str(sel_pos)
        return 'BN'  # Default to Bench

    def get_league_settings(self, league_key: str) -> Optional[Dict]:
        """
        Fetch league settings (roster positions, scoring rules)

        Args:
            league_key: Yahoo league key (e.g., 'nfl.l.12345')

        Returns:
            Dict with league settings or None
        """
        try:
            url = f"{YAHOO_FANTASY_BASE_URL}/league/{league_key}/settings"

            response = requests.get(
                url,
                headers=self.headers,
                timeout=10
            )

            response.raise_for_status()
            data = response.json()

            # Parse settings (simplified)
            settings = {
                'roster_positions': [],
                'scoring_type': 'standard'
            }

            try:
                fantasy_content = data.get('fantasy_content', {})
                league_data = fantasy_content.get('league', {})

                if isinstance(league_data, list):
                    for item in league_data:
                        if isinstance(item, dict) and 'settings' in item:
                            settings_data = item['settings']
                            break
                else:
                    settings_data = league_data.get('settings', {})

                # Extract roster positions
                roster_positions = settings_data.get('roster_positions', {})
                for pos_key in roster_positions:
                    if pos_key == 'count':
                        continue
                    pos_data = roster_positions[pos_key].get('roster_position', {})
                    settings['roster_positions'].append({
                        'position': pos_data.get('position'),
                        'count': int(pos_data.get('count', 1))
                    })

            except (KeyError, AttributeError) as e:
                logger.error(f"Error parsing league settings: {e}")

            return settings

        except Exception as e:
            logger.error(f"Failed to fetch league settings for {league_key}: {e}")
            return None
