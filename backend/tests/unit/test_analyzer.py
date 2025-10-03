"""
Unit tests for PlayerAnalyzer service
"""
import pytest
from app.services.analyzer import PlayerAnalyzer


@pytest.mark.unit
class TestPlayerAnalyzer:
    """Test suite for PlayerAnalyzer"""

    def setup_method(self):
        """Set up test fixtures"""
        self.analyzer = PlayerAnalyzer()

    def test_calculate_matchup_score_best_defense(self):
        """Test matchup score calculation against best defense (rank 1)"""
        player_stats = {'position': 'RB'}
        defense_stats = {'rank': 1, 'yards_allowed': 200, 'tds_allowed': 1}

        score = self.analyzer.calculate_matchup_score(player_stats, defense_stats)

        assert 0 <= score <= 100
        assert score > 90  # High score against best defense (good for player)

    def test_calculate_matchup_score_worst_defense(self):
        """Test matchup score calculation against worst defense (rank 32)"""
        player_stats = {'position': 'RB'}
        defense_stats = {'rank': 32, 'yards_allowed': 500, 'tds_allowed': 5}

        score = self.analyzer.calculate_matchup_score(player_stats, defense_stats)

        assert 0 <= score <= 100
        assert score < 10  # Low score against worst defense

    def test_calculate_weather_impact_ideal_conditions(self):
        """Test weather impact with ideal conditions"""
        weather_data = {
            'wind_speed': 5,
            'precipitation': 0,
            'temperature': 70
        }

        impact = self.analyzer.calculate_weather_impact(weather_data, 'QB')

        assert impact == 100  # Perfect conditions

    def test_calculate_weather_impact_high_wind_qb(self):
        """Test weather impact with high wind for QB"""
        weather_data = {
            'wind_speed': 20,
            'precipitation': 0,
            'temperature': 70
        }

        impact = self.analyzer.calculate_weather_impact(weather_data, 'QB')

        assert impact < 100  # Wind should reduce score for QB

    def test_calculate_weather_impact_no_data(self):
        """Test weather impact with no weather data"""
        impact = self.analyzer.calculate_weather_impact({}, 'RB')

        assert impact == 100  # Should assume ideal conditions
