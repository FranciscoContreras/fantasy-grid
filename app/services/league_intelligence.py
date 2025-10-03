"""
League Intelligence Service
Analyzes opponents and simulates playoff scenarios
"""

from typing import List, Dict, Optional
import random
from app.services.api_client import FantasyAPIClient
from app.services.analyzer import PlayerAnalyzer
import logging

logger = logging.getLogger(__name__)


class LeagueIntelligence:
    """
    Service for opponent analysis and playoff simulation
    """

    def __init__(self):
        self.api_client = FantasyAPIClient()
        self.analyzer = PlayerAnalyzer()

    def analyze_opponent(
        self,
        opponent_roster: List[Dict],
        your_roster: List[Dict],
        week: Optional[int] = None,
        season: int = 2024
    ) -> Dict:
        """
        Analyze opponent's roster and suggest game plan

        Args:
            opponent_roster: List of opponent's player data
            your_roster: List of your player data
            week: Week number for matchup
            season: NFL season year

        Returns:
            Dict with opponent analysis and recommendations
        """
        try:
            logger.info(f"Analyzing opponent roster for week {week}")

            # Analyze opponent strengths and weaknesses
            opponent_analysis = self._analyze_roster_strength(opponent_roster)
            your_analysis = self._analyze_roster_strength(your_roster)

            # Calculate win probability
            win_probability = self._calculate_win_probability(
                your_analysis,
                opponent_analysis
            )

            # Find weak positions in opponent roster
            weak_positions = self._find_weak_positions(opponent_roster)

            # Determine strategy (boom/bust vs safe floor)
            strategy = self._determine_strategy(
                win_probability,
                your_analysis,
                opponent_analysis
            )

            # Generate game plan
            game_plan = self._generate_game_plan(
                weak_positions,
                strategy,
                win_probability
            )

            return {
                'opponent': {
                    'total_strength': opponent_analysis['total_strength'],
                    'position_breakdown': opponent_analysis['positions'],
                    'weak_positions': weak_positions,
                    'strengths': opponent_analysis['strengths'],
                    'projected_points': opponent_analysis['projected_points']
                },
                'your_team': {
                    'total_strength': your_analysis['total_strength'],
                    'position_breakdown': your_analysis['positions'],
                    'strengths': your_analysis['strengths'],
                    'projected_points': your_analysis['projected_points']
                },
                'matchup': {
                    'win_probability': round(win_probability, 1),
                    'strategy': strategy,
                    'game_plan': game_plan,
                    'point_differential': round(
                        your_analysis['projected_points'] - opponent_analysis['projected_points'],
                        1
                    )
                },
                'week': week,
                'season': season
            }

        except Exception as e:
            logger.error(f"Error analyzing opponent: {str(e)}")
            return {'error': str(e)}

    def simulate_playoffs(
        self,
        current_record: Dict,
        remaining_schedule: List[Dict],
        league_standings: Optional[List[Dict]] = None,
        num_simulations: int = 1000
    ) -> Dict:
        """
        Simulate playoff odds using Monte Carlo simulation

        Args:
            current_record: {'wins': int, 'losses': int}
            remaining_schedule: List of upcoming matchups with opponent strength
            league_standings: Current league standings (optional)
            num_simulations: Number of simulations to run

        Returns:
            Dict with playoff odds and must-win weeks
        """
        try:
            logger.info(f"Running {num_simulations} playoff simulations")

            # Run Monte Carlo simulation
            playoff_results = []
            final_records = []

            for _ in range(num_simulations):
                sim_record = current_record.copy()

                # Simulate each remaining game
                for game in remaining_schedule:
                    win_prob = game.get('win_probability', 50) / 100
                    won = random.random() < win_prob

                    if won:
                        sim_record['wins'] += 1
                    else:
                        sim_record['losses'] += 1

                # Determine if made playoffs (top 6 typically)
                final_wins = sim_record['wins']
                final_records.append(final_wins)

                # Simple playoff threshold: 8+ wins
                made_playoffs = final_wins >= 8
                playoff_results.append(made_playoffs)

            # Calculate statistics
            playoff_odds = (sum(playoff_results) / num_simulations) * 100
            avg_final_wins = sum(final_records) / num_simulations
            win_distribution = self._calculate_distribution(final_records)

            # Identify must-win weeks
            must_win_weeks = self._identify_must_win_weeks(
                remaining_schedule,
                playoff_odds
            )

            # Determine recommended strategy
            strategy_recommendation = self._get_playoff_strategy(playoff_odds)

            return {
                'playoff_odds': round(playoff_odds, 1),
                'current_record': current_record,
                'projected_final_wins': round(avg_final_wins, 1),
                'win_distribution': win_distribution,
                'must_win_weeks': must_win_weeks,
                'remaining_games': len(remaining_schedule),
                'strategy_recommendation': strategy_recommendation,
                'simulations_run': num_simulations
            }

        except Exception as e:
            logger.error(f"Error simulating playoffs: {str(e)}")
            return {'error': str(e)}

    def _analyze_roster_strength(self, roster: List[Dict]) -> Dict:
        """Analyze overall roster strength"""
        if not roster:
            return {
                'total_strength': 0,
                'positions': {},
                'strengths': [],
                'projected_points': 0
            }

        # Calculate position-based strength
        positions = {}
        total_strength = 0
        projected_points = 0

        for player in roster:
            pos = player.get('position', 'UNKNOWN')
            if pos not in positions:
                positions[pos] = {
                    'count': 0,
                    'strength': 0,
                    'projected_points': 0
                }

            # Mock strength calculation (in real app, use actual stats)
            player_strength = hash(player.get('id', '')) % 100
            positions[pos]['count'] += 1
            positions[pos]['strength'] += player_strength
            positions[pos]['projected_points'] += player_strength * 0.2

            total_strength += player_strength
            projected_points += player_strength * 0.2

        # Identify strengths (positions with high avg strength)
        strengths = []
        for pos, data in positions.items():
            avg_strength = data['strength'] / data['count'] if data['count'] > 0 else 0
            if avg_strength > 60:
                strengths.append(pos)

        return {
            'total_strength': round(total_strength, 1),
            'positions': positions,
            'strengths': strengths,
            'projected_points': round(projected_points, 1)
        }

    def _find_weak_positions(self, roster: List[Dict]) -> List[str]:
        """Find weak positions in roster"""
        analysis = self._analyze_roster_strength(roster)
        weak_positions = []

        for pos, data in analysis['positions'].items():
            avg_strength = data['strength'] / data['count'] if data['count'] > 0 else 0
            if avg_strength < 40:
                weak_positions.append(pos)

        return weak_positions

    def _calculate_win_probability(
        self,
        your_analysis: Dict,
        opponent_analysis: Dict
    ) -> float:
        """Calculate win probability based on roster strength"""
        your_strength = your_analysis['total_strength']
        opp_strength = opponent_analysis['total_strength']

        if your_strength + opp_strength == 0:
            return 50.0

        # Simple probability based on relative strength
        win_prob = (your_strength / (your_strength + opp_strength)) * 100

        # Add some variance (±10%)
        variance = random.uniform(-10, 10)
        win_prob = max(5, min(95, win_prob + variance))

        return win_prob

    def _determine_strategy(
        self,
        win_probability: float,
        your_analysis: Dict,
        opponent_analysis: Dict
    ) -> str:
        """Determine optimal strategy (boom/bust vs safe floor)"""
        if win_probability >= 65:
            return 'SAFE_FLOOR'  # You're favored, play it safe
        elif win_probability >= 45:
            return 'BALANCED'  # Close matchup, balanced approach
        else:
            return 'BOOM_BUST'  # You're underdog, need high ceiling players

    def _generate_game_plan(
        self,
        weak_positions: List[str],
        strategy: str,
        win_probability: float
    ) -> List[str]:
        """Generate actionable game plan"""
        plan = []

        # Strategy-based recommendations
        if strategy == 'BOOM_BUST':
            plan.append('TARGET HIGH-CEILING PLAYERS - You need big performances to win')
            plan.append('TAKE RISKS - Start players with boom potential over safe floors')
        elif strategy == 'SAFE_FLOOR':
            plan.append('PLAY IT SAFE - Start consistent, high-floor players')
            plan.append('AVOID RISKS - Don\'t get cute with boom/bust plays')
        else:
            plan.append('BALANCED APPROACH - Mix safe players with upside plays')

        # Position-specific recommendations
        if weak_positions:
            plan.append(f'EXPLOIT WEAKNESSES - Target their weak positions: {", ".join(weak_positions)}')

        # Win probability-based recommendations
        if win_probability < 40:
            plan.append('AGGRESSIVE WAIVERS - Look for high-upside pickups')
        elif win_probability > 60:
            plan.append('PROTECT LEAD - Don\'t overthink it, trust your roster')

        return plan

    def _calculate_distribution(self, records: List[int]) -> Dict[int, float]:
        """Calculate win distribution from simulation results"""
        from collections import Counter
        distribution = Counter(records)
        total = len(records)

        return {
            wins: round((count / total) * 100, 1)
            for wins, count in sorted(distribution.items())
        }

    def _identify_must_win_weeks(
        self,
        remaining_schedule: List[Dict],
        playoff_odds: float
    ) -> List[int]:
        """Identify must-win weeks for playoff push"""
        must_win = []

        # If playoff odds are low, most games are must-win
        if playoff_odds < 30:
            must_win = [game.get('week') for game in remaining_schedule[:3]]
        elif playoff_odds < 60:
            # Close games against tough opponents are must-win
            for game in remaining_schedule:
                if game.get('win_probability', 50) < 45:
                    must_win.append(game.get('week'))

        return must_win[:3]  # Top 3 most critical

    def _get_playoff_strategy(self, playoff_odds: float) -> str:
        """Get recommended strategy based on playoff odds"""
        if playoff_odds >= 80:
            return 'COAST - You\'re in great shape. Don\'t make risky moves.'
        elif playoff_odds >= 60:
            return 'MAINTAIN - Stay the course. Make minor improvements only.'
        elif playoff_odds >= 40:
            return 'PUSH - Make moves to improve. Every game matters.'
        else:
            return 'ALL-IN - Aggressive strategy needed. Trade for wins now.'
