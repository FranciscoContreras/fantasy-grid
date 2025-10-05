"""
Yahoo Roster Import Service

Handles importing Yahoo Fantasy rosters into the application:
- Matches Yahoo players to Grid Iron Mind players
- Creates roster records
- Handles fuzzy name matching
- Provides import status and statistics
"""

import logging
from typing import Dict, List, Optional, Tuple
from difflib import SequenceMatcher
from app.services.api_client import FantasyAPIClient
from app.services.yahoo_fantasy_client import YahooFantasyClient
from app.database import execute_query

logger = logging.getLogger(__name__)


class YahooRosterImportService:
    """Service for importing Yahoo Fantasy rosters"""

    def __init__(self):
        self.api_client = FantasyAPIClient()

    def import_roster(
        self,
        user_id: int,
        yahoo_client: YahooFantasyClient,
        team_key: str,
        roster_name: Optional[str] = None
    ) -> Dict:
        """
        Import a Yahoo Fantasy roster

        Args:
            user_id: User ID
            yahoo_client: Authenticated Yahoo Fantasy API client
            team_key: Yahoo team key (e.g., 'nfl.l.12345.t.1')
            roster_name: Optional custom roster name

        Returns:
            Dict with import results:
            {
                'roster_id': int,
                'roster_name': str,
                'total_players': int,
                'matched_players': int,
                'unmatched_players': List[str],
                'players': List[Dict]
            }
        """
        try:
            # Fetch roster from Yahoo
            yahoo_roster = yahoo_client.get_team_roster(team_key)
            if not yahoo_roster:
                return {
                    'success': False,
                    'error': 'Failed to fetch roster from Yahoo'
                }

            # Extract league key from team key (e.g., nfl.l.12345.t.1 -> nfl.l.12345)
            league_key = '.'.join(team_key.split('.')[:3])

            # Use provided name or Yahoo team name
            final_roster_name = roster_name or yahoo_roster.get('team_name', 'Yahoo Import')

            # Create roster record
            roster_id = self._create_roster(
                user_id=user_id,
                roster_name=final_roster_name,
                league_name=yahoo_roster.get('league_name', 'Yahoo Fantasy'),
                yahoo_team_key=team_key,
                yahoo_league_key=league_key
            )

            if not roster_id:
                return {
                    'success': False,
                    'error': 'Failed to create roster record'
                }

            # Match and import players
            matched_players = []
            unmatched_players = []

            for yahoo_player in yahoo_roster.get('players', []):
                match_result = self._match_and_add_player(
                    roster_id=roster_id,
                    yahoo_player=yahoo_player
                )

                if match_result['matched']:
                    matched_players.append(match_result['player'])
                else:
                    unmatched_players.append(yahoo_player['name'])

            # Update roster sync timestamp
            execute_query(
                "UPDATE rosters SET last_synced_at = CURRENT_TIMESTAMP WHERE id = %s",
                (roster_id,)
            )

            logger.info(
                f"Imported Yahoo roster for user {user_id}: "
                f"{len(matched_players)}/{len(yahoo_roster.get('players', []))} players matched"
            )

            return {
                'success': True,
                'roster_id': roster_id,
                'roster_name': final_roster_name,
                'total_players': len(yahoo_roster.get('players', [])),
                'matched_players': len(matched_players),
                'unmatched_players': unmatched_players,
                'players': matched_players
            }

        except Exception as e:
            logger.error(f"Error importing Yahoo roster: {e}", exc_info=True)
            return {
                'success': False,
                'error': str(e)
            }

    def _create_roster(
        self,
        user_id: int,
        roster_name: str,
        league_name: str,
        yahoo_team_key: str,
        yahoo_league_key: str
    ) -> Optional[int]:
        """Create roster record in database"""
        try:
            result = execute_query(
                """
                INSERT INTO rosters
                    (user_id, name, league_name, yahoo_team_key, yahoo_league_key,
                     import_source, is_active)
                VALUES (%s, %s, %s, %s, %s, 'yahoo', true)
                RETURNING id
                """,
                (user_id, roster_name, league_name, yahoo_team_key, yahoo_league_key),
                fetch_one=True
            )

            if result and len(result) > 0:
                return result[0]['id']

            return None

        except Exception as e:
            logger.error(f"Failed to create roster: {e}")
            return None

    def _match_and_add_player(
        self,
        roster_id: int,
        yahoo_player: Dict
    ) -> Dict:
        """
        Match Yahoo player to Grid Iron Mind player and add to roster

        Args:
            roster_id: Roster ID
            yahoo_player: Yahoo player dict

        Returns:
            Dict with match result
        """
        yahoo_name = yahoo_player.get('name', '')
        yahoo_position = yahoo_player.get('position', '')
        yahoo_team = yahoo_player.get('team', '')
        selected_position = yahoo_player.get('selected_position', 'BN')

        # Try to match player
        matched_player = self._match_player(yahoo_name, yahoo_position, yahoo_team)

        if matched_player:
            # Add to roster_players table
            try:
                # Map Yahoo selected position to roster slot
                roster_slot = self._map_roster_slot(selected_position)

                # Determine if starter based on selected position
                is_starter = selected_position not in ['BN', 'IR']

                execute_query(
                    """
                    INSERT INTO roster_players
                        (roster_id, player_id, player_name, position, team,
                         roster_slot, is_starter)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """,
                    (
                        roster_id,
                        matched_player['player_id'],
                        matched_player['name'],
                        matched_player['position'],
                        matched_player['team'],
                        roster_slot,
                        is_starter
                    )
                )

                return {
                    'matched': True,
                    'player': matched_player
                }

            except Exception as e:
                logger.error(f"Failed to add player {yahoo_name} to roster: {e}")
                return {'matched': False}

        else:
            logger.warning(f"Could not match Yahoo player: {yahoo_name} ({yahoo_position}, {yahoo_team})")
            return {'matched': False}

    def _match_player(
        self,
        yahoo_name: str,
        yahoo_position: str,
        yahoo_team: str
    ) -> Optional[Dict]:
        """
        Match Yahoo player to Grid Iron Mind player using multiple strategies

        Strategy:
        1. Exact name + position match
        2. Exact name match (any position)
        3. Last name + position match
        4. Fuzzy name match with similarity threshold

        Args:
            yahoo_name: Player name from Yahoo
            yahoo_position: Player position from Yahoo
            yahoo_team: Team abbreviation from Yahoo

        Returns:
            Matched player dict or None
        """
        # Strategy 1: Exact name + position match
        players = self.api_client.search_players(yahoo_name, position=yahoo_position)
        if players:
            for player in players:
                if self._normalize_name(player.get('name', '')) == self._normalize_name(yahoo_name):
                    if player.get('position') == yahoo_position or yahoo_position in ['FLEX', 'BN', 'IR']:
                        return self._format_player(player)

        # Strategy 2: Exact name match (ignore position for FLEX/BN/IR)
        players = self.api_client.search_players(yahoo_name)
        if players:
            for player in players:
                if self._normalize_name(player.get('name', '')) == self._normalize_name(yahoo_name):
                    return self._format_player(player)

        # Strategy 3: Last name + position match
        last_name = yahoo_name.split()[-1] if ' ' in yahoo_name else yahoo_name
        players = self.api_client.search_players(last_name, position=yahoo_position)
        if players:
            # Find best match by similarity
            best_match = self._find_best_fuzzy_match(yahoo_name, players)
            if best_match:
                return self._format_player(best_match)

        # Strategy 4: Fuzzy match on full name (no position filter)
        players = self.api_client.search_players(yahoo_name)
        if players:
            best_match = self._find_best_fuzzy_match(yahoo_name, players, threshold=0.8)
            if best_match:
                return self._format_player(best_match)

        # No match found
        return None

    def _find_best_fuzzy_match(
        self,
        yahoo_name: str,
        candidates: List[Dict],
        threshold: float = 0.85
    ) -> Optional[Dict]:
        """
        Find best fuzzy match from candidate players

        Args:
            yahoo_name: Yahoo player name
            candidates: List of candidate players
            threshold: Minimum similarity ratio (0-1)

        Returns:
            Best matching player or None
        """
        best_match = None
        best_ratio = threshold

        yahoo_normalized = self._normalize_name(yahoo_name)

        for player in candidates:
            player_normalized = self._normalize_name(player.get('name', ''))
            ratio = SequenceMatcher(None, yahoo_normalized, player_normalized).ratio()

            if ratio > best_ratio:
                best_ratio = ratio
                best_match = player

        return best_match

    def _normalize_name(self, name: str) -> str:
        """Normalize player name for comparison"""
        # Remove Jr., Sr., III, etc.
        suffixes = [' Jr.', ' Sr.', ' III', ' II', ' IV']
        normalized = name
        for suffix in suffixes:
            normalized = normalized.replace(suffix, '')

        # Lowercase and strip
        normalized = normalized.lower().strip()

        # Remove periods and special characters
        normalized = normalized.replace('.', '').replace("'", '')

        return normalized

    def _format_player(self, player: Dict) -> Dict:
        """Format player data for return"""
        return {
            'player_id': player.get('id') or player.get('player_id'),
            'name': player.get('name'),
            'position': player.get('position'),
            'team': player.get('team', 'FA')
        }

    def _map_roster_slot(self, yahoo_position: str) -> str:
        """
        Map Yahoo selected position to roster slot

        Yahoo positions: QB, RB, WR, TE, W/R/T (FLEX), K, DEF, BN, IR
        Our slots: QB, RB1, RB2, WR1, WR2, WR3, TE, FLEX, K, DEF, BENCH
        """
        # Direct mappings
        if yahoo_position in ['QB', 'TE', 'K', 'DEF']:
            return yahoo_position

        # Yahoo's FLEX variants
        if yahoo_position in ['W/R', 'W/R/T', 'W/T', 'FLEX', 'OP']:
            return 'FLEX'

        # Bench and IR
        if yahoo_position in ['BN', 'IR']:
            return 'BENCH'

        # RB/WR - default to slot (will need to count existing)
        if yahoo_position == 'RB':
            return 'RB1'  # Simplification - caller should handle numbering
        if yahoo_position == 'WR':
            return 'WR1'  # Simplification - caller should handle numbering

        # Fallback
        return 'BENCH'

    def sync_roster(self, roster_id: int, yahoo_client: YahooFantasyClient) -> Dict:
        """
        Sync existing Yahoo-imported roster with latest data

        Args:
            roster_id: Roster ID
            yahoo_client: Authenticated Yahoo Fantasy API client

        Returns:
            Dict with sync results
        """
        try:
            # Get roster details
            roster = execute_query(
                """
                SELECT yahoo_team_key, user_id, name
                FROM rosters
                WHERE id = %s AND import_source = 'yahoo'
                """,
                (roster_id,),
                fetch_one=True
            )

            if not roster or len(roster) == 0:
                return {
                    'success': False,
                    'error': 'Roster not found or not imported from Yahoo'
                }

            roster = roster[0]
            yahoo_team_key = roster['yahoo_team_key']

            # Fetch current Yahoo roster
            yahoo_roster = yahoo_client.get_team_roster(yahoo_team_key)
            if not yahoo_roster:
                return {
                    'success': False,
                    'error': 'Failed to fetch roster from Yahoo'
                }

            # Get current roster players
            current_players = execute_query(
                "SELECT player_id FROM roster_players WHERE roster_id = %s",
                (roster_id,)
            )
            current_player_ids = {p['player_id'] for p in current_players}

            # Process Yahoo players
            added_count = 0
            removed_count = 0
            yahoo_player_ids = set()

            for yahoo_player in yahoo_roster.get('players', []):
                matched_player = self._match_player(
                    yahoo_player['name'],
                    yahoo_player['position'],
                    yahoo_player['team']
                )

                if matched_player:
                    player_id = matched_player['player_id']
                    yahoo_player_ids.add(player_id)

                    if player_id not in current_player_ids:
                        # Add new player
                        self._match_and_add_player(roster_id, yahoo_player)
                        added_count += 1

            # Remove players no longer on Yahoo roster
            for player_id in current_player_ids:
                if player_id not in yahoo_player_ids:
                    execute_query(
                        "DELETE FROM roster_players WHERE roster_id = %s AND player_id = %s",
                        (roster_id, player_id)
                    )
                    removed_count += 1

            # Update sync timestamp
            execute_query(
                "UPDATE rosters SET last_synced_at = CURRENT_TIMESTAMP WHERE id = %s",
                (roster_id,)
            )

            logger.info(f"Synced roster {roster_id}: +{added_count} -{removed_count}")

            return {
                'success': True,
                'added': added_count,
                'removed': removed_count,
                'total': len(yahoo_player_ids)
            }

        except Exception as e:
            logger.error(f"Error syncing roster {roster_id}: {e}", exc_info=True)
            return {
                'success': False,
                'error': str(e)
            }
