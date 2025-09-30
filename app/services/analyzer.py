import numpy as np
from sklearn.preprocessing import StandardScaler

class PlayerAnalyzer:
    def __init__(self):
        self.scaler = StandardScaler()

    def calculate_matchup_score(self, player_stats, defense_stats):
        """
        Calculate matchup score (0-100) based on player stats vs defense
        Higher score = better matchup
        """
        matchup_factors = {
            'yards_allowed': defense_stats.get('yards_allowed', 0),
            'tds_allowed': defense_stats.get('tds_allowed', 0),
            'rank': defense_stats.get('rank', 16)
        }

        score = self._compute_score(matchup_factors)
        return min(100, max(0, score))

    def calculate_weather_impact(self, weather_data, player_position):
        """
        Calculate weather impact on player performance (0-100)
        100 = ideal conditions, 0 = worst conditions
        """
        if not weather_data:
            return 100

        wind_speed = weather_data.get('wind_speed', 0)
        precipitation = weather_data.get('precipitation', 0)
        temperature = weather_data.get('temperature', 70)

        impact_score = 100

        # QBs and WRs affected by wind
        if player_position in ['QB', 'WR']:
            if wind_speed > 15:
                impact_score -= (wind_speed - 15) * 2

        # All positions affected by heavy rain/snow
        if precipitation > 0.5:
            impact_score -= precipitation * 20

        # Extreme temperatures affect all players
        if temperature < 20 or temperature > 95:
            impact_score -= 10

        return max(0, min(100, impact_score))

    def _compute_score(self, factors):
        """Compute matchup score from defense factors"""
        rank = factors.get('rank', 16)

        # Higher rank (worse defense) = better matchup
        # Rank 1 (best defense) = lower score
        # Rank 32 (worst defense) = higher score
        base_score = ((32 - rank) / 32) * 100

        return round(base_score, 2)
