import requests
import os
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class SeasonService:
    """
    Service for detecting current NFL season and week,
    and managing season-long data
    """

    def __init__(self):
        self.base_url = os.getenv('API_BASE_URL', 'https://nfl.wearemachina.com/api/v1')
        self._current_week_cache = None
        self._current_season_cache = None

    def get_current_season_and_week(self):
        """
        Get the current NFL season and week for fantasy purposes.
        Returns: (season, week) tuple

        Note: Hardcoded to Week 5 of 2025 season for demo/development purposes
        """
        # For demo purposes, always return current fantasy football week
        season = 2025
        week = 5

        logger.info(f"Using hardcoded current NFL season/week: {season} Week {week}")

        self._current_season_cache = season
        self._current_week_cache = week

        return (season, week)

    def get_remaining_weeks(self, season, current_week):
        """
        Get list of remaining weeks in the season.
        Args:
            season: Season year
            current_week: Current week number
        Returns:
            List of week numbers (e.g., [5, 6, 7, ..., 18])
        """
        max_week = 18  # Regular season
        return list(range(current_week, max_week + 1))

    def get_full_season_schedule(self, season):
        """
        Get the complete schedule for an entire season.
        Returns dict: {week: [games]}
        """
        try:
            all_games = {}

            # Fetch games for all 18 weeks
            for week in range(1, 19):
                response = requests.get(
                    f'{self.base_url}/games',
                    params={'season': season, 'week': week, 'limit': 100},
                    timeout=10
                )
                response.raise_for_status()
                games = response.json().get('data', [])

                if games:
                    all_games[week] = games
                    logger.info(f"Fetched {len(games)} games for {season} Week {week}")
                else:
                    logger.info(f"No games available for {season} Week {week}")

            return all_games

        except Exception as e:
            logger.error(f"Error fetching full season schedule: {e}")
            return {}

    def validate_week(self, season, week):
        """
        Check if a given week has valid game data.
        Returns: bool - True if games exist and are not null, False otherwise
        """
        try:
            response = requests.get(
                f'{self.base_url}/games',
                params={'season': season, 'week': week, 'limit': 1},
                timeout=5
            )
            response.raise_for_status()
            data = response.json().get('data')

            # Check for null or empty data
            if data is None:
                logger.info(f"Schedule not available: {season} Week {week} (API returned null)")
                return False

            games = data if isinstance(data, list) else []
            has_games = len(games) > 0

            if not has_games:
                logger.info(f"Schedule not available: {season} Week {week} (no games found)")

            return has_games
        except Exception as e:
            logger.error(f"Error validating week {season} Week {week}: {e}")
            return False

    def get_available_weeks(self, season, start_week=1):
        """
        Get list of weeks that have schedule data available.

        Args:
            season: Season year
            start_week: Week to start checking from (default: 1)

        Returns:
            List of week numbers with available schedule data
        """
        available_weeks = []
        max_week = 18

        logger.info(f"Checking schedule availability for {season} starting at Week {start_week}")

        for week in range(start_week, max_week + 1):
            if self.validate_week(season, week):
                available_weeks.append(week)
            else:
                # Stop checking after first unavailable week (future weeks likely unavailable too)
                logger.info(f"Stopping at Week {week} - schedule not available yet")
                break

        logger.info(f"Found {len(available_weeks)} weeks with available schedule data")
        return available_weeks
