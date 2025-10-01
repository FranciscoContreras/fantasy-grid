import logging
from typing import Dict, List, Optional, Tuple
from app.services.season_service import SeasonService
from app.services.api_client import FantasyAPIClient

logger = logging.getLogger(__name__)


class MatchupDataService:
    """
    Service for mapping roster players to their NFL opponents
    and gathering comprehensive matchup data for analysis
    """

    def __init__(self):
        self.season_service = SeasonService()
        self.api_client = FantasyAPIClient()

    def get_player_opponent_mapping(self, roster_players, season, week):
        """
        For each player in roster, determine their NFL opponent for the week.

        Args:
            roster_players: List of player dicts from roster
            season: Season year
            week: Week number

        Returns:
            List of dicts with player and opponent info:
            [{
                'player': player_data,
                'opponent_team': 'KC',
                'has_game': True,
                ...
            }, ...]
        """
        mappings = []

        for player in roster_players:
            player_team = player.get('team')

            if not player_team:
                logger.warning(f"Player {player.get('player_name')} has no team")
                mappings.append({
                    'player': player,
                    'opponent_team': None,
                    'has_game': True,  # Still allow analysis
                    'error': 'No team assigned'
                })
                continue

            # Get opponent for this player's team
            opponent = self.api_client.get_team_opponent(player_team, season, week)

            if opponent:
                mappings.append({
                    'player': player,
                    'opponent_team': opponent,
                    'has_game': True
                })
                logger.debug(f"{player.get('player_name')} ({player_team}) vs {opponent}")
            else:
                # No opponent data - could be missing schedule data or actual bye
                # Default to has_game=True to allow analysis, just without opponent info
                mappings.append({
                    'player': player,
                    'opponent_team': None,
                    'has_game': True,  # Changed from False - assume game exists
                    'error': 'Opponent unknown - schedule data unavailable'
                })
                logger.info(f"{player.get('player_name')} ({player_team}) opponent unknown for Week {week}")

        return mappings

    def get_season_matchups(self, roster_id, roster_players, start_week=None):
        """
        Get all matchups for remaining weeks of season.

        Args:
            roster_id: ID of the roster
            roster_players: List of players in roster
            start_week: Optional starting week (defaults to current week)

        Returns:
            Dict mapping weeks to player matchups:
            {
                5: [player_matchup_data, ...],
                6: [player_matchup_data, ...],
                ...
            }
        """
        try:
            # Detect current season/week
            season, current_week = self.season_service.get_current_season_and_week()

            # Use provided start_week or current_week
            start = start_week if start_week else current_week

            # Get remaining weeks
            remaining_weeks = self.season_service.get_remaining_weeks(season, start)

            logger.info(f"Building season matchups for roster {roster_id}: Weeks {remaining_weeks}")

            season_matchups = {}

            for week in remaining_weeks:
                # Validate week has data
                if not self.season_service.validate_week(season, week):
                    logger.info(f"Week {week} has no game data yet, skipping")
                    continue

                # Get player-opponent mappings for this week
                week_mappings = self.get_player_opponent_mapping(roster_players, season, week)

                season_matchups[week] = week_mappings
                logger.info(f"Mapped {len(week_mappings)} players for Week {week}")

            return {
                'season': season,
                'matchups': season_matchups,
                'total_weeks': len(season_matchups)
            }

        except Exception as e:
            logger.error(f"Error building season matchups: {e}")
            return {
                'season': None,
                'matchups': {},
                'total_weeks': 0,
                'error': str(e)
            }

    def get_comprehensive_matchup_data(self, player, opponent_team, season, week):
        """
        Fetch all necessary data for a single player matchup analysis.

        Args:
            player: Player dict
            opponent_team: Opponent team abbreviation
            season: Season year
            week: Week number

        Returns:
            Dict with all analysis data:
            {
                'player': player_data,
                'opponent': opponent_team,
                'opponent_roster': {...},
                'defensive_stats': {...},
                'historical_performance': {...},
                'defensive_coordinator': 'Name',
                'key_defenders': ['Player1', 'Player2'],
                'injury_status': 'HEALTHY',
                ...
            }
        """
        data = {
            'player': player,
            'opponent': opponent_team,
            'season': season,
            'week': week
        }

        if not opponent_team:
            return data

        try:
            player_id = player.get('player_id')
            player_position = player.get('position')

            # Get opponent roster (offensive players)
            opponent_roster = self.api_client.get_team_roster(opponent_team, season)
            data['opponent_roster'] = opponent_roster
            logger.debug(f"Fetched opponent roster for {opponent_team}")

            # Get opponent defensive rankings
            defensive_stats = self.api_client.get_team_defensive_rankings(opponent_team, season)
            data['defensive_stats'] = defensive_stats
            logger.debug(f"Fetched defensive stats for {opponent_team}")

            # Get defensive coordinator
            dc = self.api_client.get_defensive_coordinator(opponent_team, season)
            data['defensive_coordinator'] = dc

            # Get key defensive players based on position
            key_defenders = []
            if player_position == 'QB':
                key_defenders = self.api_client.get_key_defensive_players(opponent_team, 'DL') or []
            elif player_position in ['WR', 'TE']:
                key_defenders = self.api_client.get_key_defensive_players(opponent_team, 'DB') or []
            elif player_position == 'RB':
                dl = self.api_client.get_key_defensive_players(opponent_team, 'DL') or []
                lb = self.api_client.get_key_defensive_players(opponent_team, 'LB') or []
                key_defenders = dl + lb

            data['key_defenders'] = key_defenders

            # Get player's historical performance vs this opponent
            if player_id:
                vs_stats = self.api_client.get_player_stats_vs_team(player_id, opponent_team)
                data['historical_performance'] = vs_stats

            # Get injury status from player data
            injury_status = player.get('injury_status', 'HEALTHY')
            data['injury_status'] = injury_status

            logger.debug(f"Fetched comprehensive data for {player.get('player_name')} vs {opponent_team}")

        except Exception as e:
            logger.error(f"Error fetching comprehensive matchup data: {e}")
            data['error'] = str(e)

        return data

    def prepare_bulk_analysis_data(self, roster_id, roster_players, season, week):
        """
        Prepare all data needed for analyzing an entire roster for a given week.

        Args:
            roster_id: Roster ID
            roster_players: List of players
            season: Season year
            week: Week number

        Returns:
            List of comprehensive matchup data for each player
        """
        logger.info(f"Preparing bulk analysis data for roster {roster_id}, {season} Week {week}")

        # First, map players to opponents
        player_mappings = self.get_player_opponent_mapping(roster_players, season, week)

        # Then fetch comprehensive data for each matchup
        analysis_data = []
        for mapping in player_mappings:
            player = mapping['player']
            opponent = mapping.get('opponent_team')

            if mapping.get('has_game'):
                # Fetch full data
                comprehensive = self.get_comprehensive_matchup_data(player, opponent, season, week)
                analysis_data.append(comprehensive)
            else:
                # Player has no game (bye week)
                analysis_data.append({
                    'player': player,
                    'opponent': None,
                    'season': season,
                    'week': week,
                    'has_game': False,
                    'error': mapping.get('error', 'No game')
                })

        logger.info(f"Prepared analysis data for {len(analysis_data)} players")
        return analysis_data
