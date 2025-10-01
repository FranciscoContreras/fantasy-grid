from flask import Blueprint, request, jsonify
from app.database import execute_query
import logging
from datetime import datetime
import random

bp = Blueprint('matchups', __name__, url_prefix='/api/matchups')
logger = logging.getLogger(__name__)


@bp.route('', methods=['POST'])
def create_matchup():
    """Create a new weekly matchup between two rosters"""
    data = request.json
    week = data.get('week')
    season = data.get('season')
    user_roster_id = data.get('user_roster_id')
    opponent_roster_id = data.get('opponent_roster_id')

    if not all([week, season, user_roster_id, opponent_roster_id]):
        return jsonify({'error': 'week, season, user_roster_id, and opponent_roster_id are required'}), 400

    try:
        query = """
            INSERT INTO matchups (week, season, user_roster_id, opponent_roster_id)
            VALUES (%s, %s, %s, %s)
            RETURNING id, week, season, user_roster_id, opponent_roster_id, analyzed, created_at
        """
        result = execute_query(query, (week, season, user_roster_id, opponent_roster_id))

        if result:
            return jsonify({'data': result[0]}), 201
        else:
            return jsonify({'error': 'Failed to create matchup'}), 500
    except Exception as e:
        logger.error(f"Error creating matchup: {str(e)}")
        return jsonify({'error': 'Failed to create matchup'}), 500


@bp.route('/<int:matchup_id>', methods=['GET'])
def get_matchup(matchup_id):
    """Get matchup details with analysis"""
    try:
        # Get matchup info
        matchup_query = """
            SELECT m.id, m.week, m.season, m.user_roster_id, m.opponent_roster_id,
                   m.analyzed, m.analyzed_at, m.created_at,
                   ur.name as user_roster_name, or_table.name as opponent_roster_name
            FROM matchups m
            JOIN rosters ur ON m.user_roster_id = ur.id
            JOIN rosters or_table ON m.opponent_roster_id = or_table.id
            WHERE m.id = %s
        """
        matchup = execute_query(matchup_query, (matchup_id,))

        if not matchup:
            return jsonify({'error': 'Matchup not found'}), 404

        # Get analysis results if available
        analysis_query = """
            SELECT id, player_id, player_name, position, is_user_player,
                   opponent_team, matchup_score, projected_points, ai_grade,
                   recommendation, injury_impact, confidence_score, reasoning, analyzed_at
            FROM matchup_analysis
            WHERE matchup_id = %s
            ORDER BY is_user_player DESC, matchup_score DESC
        """
        analysis = execute_query(analysis_query, (matchup_id,))

        matchup_data = matchup[0]
        matchup_data['analysis'] = analysis if analysis else []

        return jsonify({'data': matchup_data})
    except Exception as e:
        logger.error(f"Error fetching matchup {matchup_id}: {str(e)}")
        return jsonify({'error': 'Failed to fetch matchup'}), 500


@bp.route('/<int:matchup_id>/analyze', methods=['POST'])
def analyze_matchup(matchup_id):
    """Analyze a matchup and generate start/sit recommendations"""
    try:
        # Get matchup details
        matchup_query = """
            SELECT m.id, m.week, m.season, m.user_roster_id, m.opponent_roster_id
            FROM matchups m
            WHERE m.id = %s
        """
        matchup = execute_query(matchup_query, (matchup_id,))

        if not matchup:
            return jsonify({'error': 'Matchup not found'}), 404

        matchup_data = matchup[0]

        # Get user roster players
        user_players_query = """
            SELECT rp.id, rp.player_id, rp.player_name, rp.position, rp.team,
                   rp.roster_slot, rp.is_starter, rp.injury_status
            FROM roster_players rp
            WHERE rp.roster_id = %s AND rp.is_starter = true
        """
        user_players = execute_query(user_players_query, (matchup_data['user_roster_id'],))

        # Get opponent roster players
        opponent_players = execute_query(user_players_query, (matchup_data['opponent_roster_id'],))

        # Clear existing analysis
        delete_query = "DELETE FROM matchup_analysis WHERE matchup_id = %s"
        execute_query(delete_query, (matchup_id,))

        analysis_results = []

        # Analyze user's players
        for player in user_players:
            analysis = _analyze_player_for_matchup(
                player,
                is_user_player=True,
                week=matchup_data['week']
            )
            analysis_results.append(analysis)

            # Save to database
            _save_matchup_analysis(matchup_id, analysis, is_user_player=True)

        # Analyze opponent's players
        for player in opponent_players:
            analysis = _analyze_player_for_matchup(
                player,
                is_user_player=False,
                week=matchup_data['week']
            )
            analysis_results.append(analysis)

            # Save to database
            _save_matchup_analysis(matchup_id, analysis, is_user_player=False)

        # Mark matchup as analyzed
        update_query = """
            UPDATE matchups
            SET analyzed = true, analyzed_at = CURRENT_TIMESTAMP
            WHERE id = %s
        """
        execute_query(update_query, (matchup_id,))

        # Generate recommendations
        recommendations = _generate_recommendations(user_players, analysis_results)

        return jsonify({
            'data': {
                'matchup_id': matchup_id,
                'analysis': analysis_results,
                'recommendations': recommendations
            }
        })

    except Exception as e:
        logger.error(f"Error analyzing matchup {matchup_id}: {str(e)}")
        return jsonify({'error': f'Failed to analyze matchup: {str(e)}'}), 500


def _analyze_player_for_matchup(player, is_user_player, week):
    """Analyze a single player for the matchup"""
    # Calculate matchup score based on position and opponent
    matchup_score = _calculate_matchup_score(player['position'], player.get('team'))

    # Evaluate injury impact
    injury_impact = _evaluate_injury_impact(player.get('injury_status', 'HEALTHY'))

    # Calculate projected points
    projected_points = _calculate_projected_points(
        player['position'],
        matchup_score,
        injury_impact
    )

    # Assign AI grade
    ai_grade = _assign_grade(matchup_score, injury_impact)

    # Generate recommendation
    recommendation = _generate_recommendation(
        matchup_score,
        injury_impact,
        player.get('injury_status', 'HEALTHY')
    )

    # Calculate confidence score
    confidence_score = _calculate_confidence(matchup_score, injury_impact)

    # Generate reasoning
    reasoning = _generate_reasoning(
        player,
        matchup_score,
        injury_impact,
        recommendation
    )

    return {
        'player_id': player.get('player_id'),
        'player_name': player['player_name'],
        'position': player['position'],
        'team': player['team'],
        'is_user_player': is_user_player,
        'opponent_team': 'N/A',  # Would get from schedule API
        'matchup_score': round(matchup_score, 2),
        'projected_points': round(projected_points, 2),
        'ai_grade': ai_grade,
        'recommendation': recommendation,
        'injury_status': player.get('injury_status', 'HEALTHY'),
        'injury_impact': injury_impact,
        'confidence_score': round(confidence_score, 2),
        'reasoning': reasoning
    }


def _calculate_matchup_score(position, team):
    """Calculate matchup difficulty score (0-100)"""
    # Base score by position (simplified - would use real opponent defense data)
    base_scores = {
        'QB': 75,
        'RB': 70,
        'WR': 72,
        'TE': 68,
        'K': 65,
        'DEF': 70
    }

    base = base_scores.get(position, 70)
    # Add some variance (+/- 15 points)
    variance = random.uniform(-15, 15)

    return max(0, min(100, base + variance))


def _evaluate_injury_impact(injury_status):
    """Evaluate impact of injury status"""
    impact_map = {
        'HEALTHY': 'No impact',
        'PROBABLE': 'Minimal impact - expected to play',
        'QUESTIONABLE': 'Moderate impact - game-time decision',
        'DOUBTFUL': 'High impact - unlikely to play',
        'OUT': 'Cannot play - seek replacement'
    }
    return impact_map.get(injury_status, 'Unknown status')


def _calculate_projected_points(position, matchup_score, injury_impact):
    """Calculate projected fantasy points"""
    # Base projection by position
    base_projections = {
        'QB': 18,
        'RB': 12,
        'WR': 11,
        'TE': 9,
        'K': 8,
        'DEF': 7
    }

    base = base_projections.get(position, 10)

    # Adjust for matchup (matchup_score affects projection)
    matchup_multiplier = matchup_score / 75  # 75 is average

    # Adjust for injury
    injury_multipliers = {
        'No impact': 1.0,
        'Minimal impact - expected to play': 0.95,
        'Moderate impact - game-time decision': 0.75,
        'High impact - unlikely to play': 0.3,
        'Cannot play - seek replacement': 0.0
    }
    injury_mult = injury_multipliers.get(injury_impact, 0.8)

    return base * matchup_multiplier * injury_mult


def _assign_grade(matchup_score, injury_impact):
    """Assign letter grade A+ to F"""
    if 'Cannot play' in injury_impact:
        return 'F'
    if 'unlikely to play' in injury_impact:
        return 'D'

    if matchup_score >= 85:
        return 'A+'
    elif matchup_score >= 75:
        return 'A'
    elif matchup_score >= 65:
        return 'B'
    elif matchup_score >= 55:
        return 'C'
    elif matchup_score >= 45:
        return 'D'
    else:
        return 'F'


def _generate_recommendation(matchup_score, injury_impact, injury_status):
    """Generate START/SIT/CONSIDER recommendation"""
    if injury_status == 'OUT':
        return 'SIT'
    if injury_status == 'DOUBTFUL':
        return 'SIT'

    if injury_status == 'QUESTIONABLE':
        if matchup_score >= 75:
            return 'CONSIDER'
        else:
            return 'SIT'

    # Healthy or Probable
    if matchup_score >= 70:
        return 'START'
    elif matchup_score >= 50:
        return 'CONSIDER'
    else:
        return 'SIT'


def _calculate_confidence(matchup_score, injury_impact):
    """Calculate confidence in recommendation (0-100)"""
    base_confidence = 70

    # High matchup scores increase confidence
    if matchup_score >= 80:
        base_confidence += 20
    elif matchup_score >= 60:
        base_confidence += 10

    # Injury uncertainty decreases confidence
    if 'game-time decision' in injury_impact:
        base_confidence -= 25
    elif 'unlikely to play' in injury_impact:
        base_confidence -= 15

    return max(0, min(100, base_confidence))


def _generate_reasoning(player, matchup_score, injury_impact, recommendation):
    """Generate human-readable reasoning"""
    reasoning_parts = []

    # Matchup analysis
    if matchup_score >= 75:
        reasoning_parts.append(f"{player['player_name']} has a favorable matchup (score: {matchup_score:.1f})")
    elif matchup_score >= 50:
        reasoning_parts.append(f"{player['player_name']} has an average matchup (score: {matchup_score:.1f})")
    else:
        reasoning_parts.append(f"{player['player_name']} faces a tough matchup (score: {matchup_score:.1f})")

    # Injury consideration
    if 'No impact' not in injury_impact:
        reasoning_parts.append(f"Injury concern: {injury_impact}")

    # Final recommendation
    rec_text = {
        'START': 'Strong start candidate',
        'CONSIDER': 'Monitor closely before game time',
        'SIT': 'Consider benching or finding alternative'
    }
    reasoning_parts.append(rec_text.get(recommendation, ''))

    return '. '.join(reasoning_parts) + '.'


def _save_matchup_analysis(matchup_id, analysis, is_user_player):
    """Save analysis to database"""
    query = """
        INSERT INTO matchup_analysis
        (matchup_id, player_id, player_name, position, is_user_player, opponent_team,
         matchup_score, projected_points, ai_grade, recommendation, injury_impact,
         confidence_score, reasoning)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    execute_query(query, (
        matchup_id,
        analysis['player_id'],
        analysis['player_name'],
        analysis['position'],
        is_user_player,
        analysis['opponent_team'],
        analysis['matchup_score'],
        analysis['projected_points'],
        analysis['ai_grade'],
        analysis['recommendation'],
        analysis['injury_impact'],
        analysis['confidence_score'],
        analysis['reasoning']
    ))


def _generate_recommendations(user_players, analysis_results):
    """Generate overall recommendations for the matchup"""
    user_analysis = [a for a in analysis_results if a.get('is_user_player')]

    start_players = [a for a in user_analysis if a['recommendation'] == 'START']
    sit_players = [a for a in user_analysis if a['recommendation'] == 'SIT']
    consider_players = [a for a in user_analysis if a['recommendation'] == 'CONSIDER']

    return {
        'summary': f"{len(start_players)} players to START, {len(consider_players)} to CONSIDER, {len(sit_players)} to SIT",
        'start_count': len(start_players),
        'sit_count': len(sit_players),
        'consider_count': len(consider_players),
        'avg_projected_points': round(sum(a['projected_points'] for a in user_analysis) / len(user_analysis), 2) if user_analysis else 0,
        'high_confidence_starts': [a['player_name'] for a in start_players if a['confidence_score'] >= 80]
    }


@bp.route('', methods=['GET'])
def get_matchups():
    """Get all matchups, optionally filtered by week/season"""
    week = request.args.get('week')
    season = request.args.get('season')

    try:
        if week and season:
            query = """
                SELECT m.id, m.week, m.season, m.user_roster_id, m.opponent_roster_id,
                       m.analyzed, m.analyzed_at, m.created_at,
                       ur.name as user_roster_name, or_table.name as opponent_roster_name
                FROM matchups m
                JOIN rosters ur ON m.user_roster_id = ur.id
                JOIN rosters or_table ON m.opponent_roster_id = or_table.id
                WHERE m.week = %s AND m.season = %s
                ORDER BY m.created_at DESC
            """
            matchups = execute_query(query, (week, season))
        else:
            query = """
                SELECT m.id, m.week, m.season, m.user_roster_id, m.opponent_roster_id,
                       m.analyzed, m.analyzed_at, m.created_at,
                       ur.name as user_roster_name, or_table.name as opponent_roster_name
                FROM matchups m
                JOIN rosters ur ON m.user_roster_id = ur.id
                JOIN rosters or_table ON m.opponent_roster_id = or_table.id
                ORDER BY m.created_at DESC
            """
            matchups = execute_query(query)

        return jsonify({
            'data': matchups,
            'count': len(matchups)
        })
    except Exception as e:
        logger.error(f"Error fetching matchups: {str(e)}")
        return jsonify({'error': 'Failed to fetch matchups'}), 500
