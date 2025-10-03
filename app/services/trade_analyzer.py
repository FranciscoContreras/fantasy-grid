"""
Trade Analyzer Service
Evaluates trade proposals and suggests fair trades
"""

from typing import List, Dict, Optional
from app.services.api_client import FantasyAPIClient
from app.services.analyzer import PlayerAnalyzer
import logging

logger = logging.getLogger(__name__)


class TradeAnalyzer:
    """
    Service for analyzing trade proposals and finding trade targets
    """

    def __init__(self):
        self.api_client = FantasyAPIClient()
        self.analyzer = PlayerAnalyzer()

    def evaluate_trade(
        self,
        team_a_gives: List[str],
        team_b_gives: List[str],
        season: int = 2024
    ) -> Dict:
        """
        Evaluate a trade proposal between two teams

        Args:
            team_a_gives: List of player IDs team A is giving up
            team_b_gives: List of player IDs team B is giving up
            season: NFL season year

        Returns:
            Dict with trade evaluation and recommendations
        """
        try:
            logger.info(f"Evaluating trade: Team A gives {team_a_gives}, Team B gives {team_b_gives}")

            # Get player data for both sides
            team_a_players = self._get_players_data(team_a_gives)
            team_b_players = self._get_players_data(team_b_gives)

            if not team_a_players or not team_b_players:
                return {'error': 'Unable to fetch player data'}

            # Calculate value for each side
            team_a_value = self._calculate_trade_value(team_a_players)
            team_b_value = self._calculate_trade_value(team_b_players)

            # Calculate fairness
            value_diff = abs(team_a_value - team_b_value)
            fairness_score = max(0, 100 - (value_diff * 2))  # Penalty for large differences

            # Determine winner
            winner = None
            if value_diff > 10:
                winner = 'Team A' if team_b_value > team_a_value else 'Team B'

            # Position analysis
            team_a_positions = self._analyze_positions(team_a_players)
            team_b_positions = self._analyze_positions(team_b_players)

            # Generate recommendation
            recommendation = self._generate_trade_recommendation(
                fairness_score,
                team_a_value,
                team_b_value,
                winner
            )

            return {
                'team_a': {
                    'players': team_a_players,
                    'total_value': round(team_a_value, 1),
                    'positions': team_a_positions,
                    'receiving': team_b_players
                },
                'team_b': {
                    'players': team_b_players,
                    'total_value': round(team_b_value, 1),
                    'positions': team_b_positions,
                    'receiving': team_a_players
                },
                'analysis': {
                    'fairness_score': round(fairness_score, 1),
                    'value_difference': round(value_diff, 1),
                    'winner': winner,
                    'recommendation': recommendation,
                    'trade_type': self._classify_trade_type(team_a_players, team_b_players)
                }
            }

        except Exception as e:
            logger.error(f"Error evaluating trade: {str(e)}")
            return {'error': str(e)}

    def suggest_trades(
        self,
        player_id: str,
        target_positions: Optional[List[str]] = None,
        season: int = 2024
    ) -> Dict:
        """
        Suggest fair trades for a given player

        Args:
            player_id: Player ID to trade away
            target_positions: Desired positions to receive (e.g., ['RB', 'WR'])
            season: NFL season year

        Returns:
            Dict with trade suggestions
        """
        try:
            logger.info(f"Finding trade targets for player {player_id}")

            # Get player data
            player_response = self.api_client.get_player_by_id_v2(player_id)
            if not player_response or 'data' not in player_response:
                return {'error': 'Player not found'}

            player_data = player_response['data']
            player_value = self._calculate_player_value(player_data)

            # Get potential trade targets
            potential_targets = self._find_similar_value_players(
                player_value,
                target_positions=target_positions,
                exclude_player_id=player_id
            )

            # Rank by value match
            suggestions = []
            for target in potential_targets[:10]:  # Top 10
                value_diff = abs(target['value'] - player_value)
                fairness = max(0, 100 - (value_diff * 2))

                suggestions.append({
                    'player': target['player'],
                    'value': target['value'],
                    'value_difference': round(value_diff, 1),
                    'fairness_score': round(fairness, 1),
                    'trade_type': '1-for-1',
                    'recommendation': self._get_suggestion_recommendation(fairness)
                })

            return {
                'trading_away': {
                    'player': player_data,
                    'value': round(player_value, 1)
                },
                'suggestions': suggestions,
                'total_suggestions': len(suggestions)
            }

        except Exception as e:
            logger.error(f"Error suggesting trades: {str(e)}")
            return {'error': str(e)}

    def _get_players_data(self, player_ids: List[str]) -> List[Dict]:
        """Fetch data for multiple players"""
        players = []
        for player_id in player_ids:
            try:
                response = self.api_client.get_player_by_id_v2(player_id)
                if response and 'data' in response:
                    player_data = response['data']
                    player_data['trade_value'] = self._calculate_player_value(player_data)
                    players.append(player_data)
            except Exception as e:
                logger.error(f"Error fetching player {player_id}: {e}")
                continue
        return players

    def _calculate_player_value(self, player: Dict) -> float:
        """
        Calculate trade value for a single player

        Factors:
        - Position scarcity (QB < RB > WR > TE)
        - Recent performance
        - Injury status
        - Age/experience
        """
        base_value = 50.0

        # Position multipliers
        position = player.get('position', '')
        position_multipliers = {
            'QB': 1.0,
            'RB': 1.3,  # RBs more valuable due to scarcity
            'WR': 1.1,
            'TE': 0.9,
            'K': 0.3,
            'DEF': 0.4
        }
        base_value *= position_multipliers.get(position, 1.0)

        # Status adjustments
        status = player.get('status', '').lower()
        if 'injured' in status or 'out' in status:
            base_value *= 0.5
        elif 'questionable' in status or 'doubtful' in status:
            base_value *= 0.8

        # Experience bonus (veteran players more reliable)
        experience = player.get('years_pro', 0)
        if experience > 5:
            base_value *= 1.1
        elif experience < 2:
            base_value *= 0.9

        # Mock stat adjustment (in real app, use actual season stats)
        # For now, add some variance based on player ID
        variance = hash(player.get('id', '')) % 30 - 15  # -15 to +15
        base_value += variance

        return max(10, min(100, base_value))  # Keep between 10-100

    def _calculate_trade_value(self, players: List[Dict]) -> float:
        """Calculate total trade value for a group of players"""
        total_value = sum(p.get('trade_value', 0) for p in players)

        # Diminishing returns for multiple players
        # 2-for-1 trades: second player worth less
        # 3-for-1 trades: even more penalty
        if len(players) > 1:
            penalty = 0.9 ** (len(players) - 1)
            total_value *= penalty

        return total_value

    def _analyze_positions(self, players: List[Dict]) -> Dict:
        """Analyze positions in trade"""
        positions = {}
        for player in players:
            pos = player.get('position', 'UNKNOWN')
            if pos not in positions:
                positions[pos] = 0
            positions[pos] += 1
        return positions

    def _classify_trade_type(self, team_a_players: List[Dict], team_b_players: List[Dict]) -> str:
        """Classify the type of trade"""
        a_count = len(team_a_players)
        b_count = len(team_b_players)

        if a_count == 1 and b_count == 1:
            return '1-for-1'
        elif a_count == 2 and b_count == 1:
            return '2-for-1'
        elif a_count == 1 and b_count == 2:
            return '1-for-2'
        elif a_count == 2 and b_count == 2:
            return '2-for-2'
        elif a_count == 3 and b_count == 1:
            return '3-for-1'
        elif a_count == 1 and b_count == 3:
            return '1-for-3'
        else:
            return f'{a_count}-for-{b_count}'

    def _generate_trade_recommendation(
        self,
        fairness_score: float,
        team_a_value: float,
        team_b_value: float,
        winner: Optional[str]
    ) -> str:
        """Generate recommendation text"""
        if fairness_score >= 85:
            return 'FAIR TRADE - Both sides receive good value'
        elif fairness_score >= 70:
            return f'SLIGHTLY FAVORS {winner} - Close to fair, acceptable trade'
        elif fairness_score >= 50:
            return f'FAVORS {winner} - Unbalanced but not terrible'
        else:
            return f'HEAVILY FAVORS {winner} - Very lopsided trade, not recommended'

    def _get_suggestion_recommendation(self, fairness: float) -> str:
        """Get recommendation for trade suggestion"""
        if fairness >= 90:
            return 'EXCELLENT MATCH'
        elif fairness >= 75:
            return 'GOOD MATCH'
        elif fairness >= 60:
            return 'FAIR MATCH'
        else:
            return 'NEEDS SWEETENER'

    def _find_similar_value_players(
        self,
        target_value: float,
        target_positions: Optional[List[str]] = None,
        exclude_player_id: Optional[str] = None
    ) -> List[Dict]:
        """
        Find players with similar trade value

        In production, this would query a database or API
        For now, returns mock data
        """
        # Mock implementation - in real app, query players by value range
        # This would be: SELECT * FROM players WHERE trade_value BETWEEN (target_value - 10) AND (target_value + 10)

        # For now, return empty list (would need actual player database)
        # The frontend will handle this gracefully
        logger.info(f"Finding players with value near {target_value}")

        # Mock some similar players
        mock_players = [
            {
                'player': {
                    'id': 'mock_1',
                    'name': 'Similar Player 1',
                    'position': target_positions[0] if target_positions else 'RB',
                    'team': 'Mock Team 1'
                },
                'value': target_value + 5
            },
            {
                'player': {
                    'id': 'mock_2',
                    'name': 'Similar Player 2',
                    'position': target_positions[0] if target_positions else 'WR',
                    'team': 'Mock Team 2'
                },
                'value': target_value - 3
            },
            {
                'player': {
                    'id': 'mock_3',
                    'name': 'Similar Player 3',
                    'position': target_positions[0] if target_positions else 'RB',
                    'team': 'Mock Team 3'
                },
                'value': target_value + 2
            }
        ]

        return mock_players
