from flask import Blueprint, request, jsonify
from app.database import execute_query
from app.services.ai_service import AIService
from app.services.weather_service import WeatherService
from app.services.api_client import FantasyAPIClient
import logging
from datetime import datetime
import random

bp = Blueprint('matchups', __name__, url_prefix='/api/matchups')
logger = logging.getLogger(__name__)

# Initialize services
ai_service = AIService()
weather_service = WeatherService()
api_client = FantasyAPIClient()


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

        # Convert DECIMAL fields to float for JSON serialization
        if analysis:
            for item in analysis:
                if 'matchup_score' in item and item['matchup_score'] is not None:
                    item['matchup_score'] = float(item['matchup_score'])
                if 'projected_points' in item and item['projected_points'] is not None:
                    item['projected_points'] = float(item['projected_points'])
                if 'confidence_score' in item and item['confidence_score'] is not None:
                    item['confidence_score'] = float(item['confidence_score'])

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
        logger.info(f"Analyzing matchup {matchup_id}: Week {matchup_data.get('week')}, Season {matchup_data.get('season')}")

        # Get user roster players
        user_players_query = """
            SELECT rp.id, rp.player_id, rp.player_name, rp.position, rp.team,
                   rp.roster_slot, rp.is_starter, rp.injury_status
            FROM roster_players rp
            WHERE rp.roster_id = %s AND rp.is_starter = true
        """
        user_players = execute_query(user_players_query, (matchup_data['user_roster_id'],))
        if user_players is None:
            user_players = []
        logger.info(f"Found {len(user_players)} user players")

        # Get opponent roster players
        opponent_players = execute_query(user_players_query, (matchup_data['opponent_roster_id'],))
        if opponent_players is None:
            opponent_players = []
        logger.info(f"Found {len(opponent_players)} opponent players")

        # Clear existing analysis
        delete_query = "DELETE FROM matchup_analysis WHERE matchup_id = %s"
        execute_query(delete_query, (matchup_id,))

        analysis_results = []

        # Analyze user's players
        for player in user_players:
            try:
                logger.info(f"Analyzing user player: {player.get('player_name')}")
                analysis = _analyze_player_for_matchup(
                    player,
                    is_user_player=True,
                    week=matchup_data['week'],
                    season=matchup_data.get('season', 2024)
                )
                analysis_results.append(analysis)

                # Save to database
                _save_matchup_analysis(matchup_id, analysis, is_user_player=True)
            except Exception as e:
                logger.error(f"Error analyzing user player {player.get('player_name')}: {str(e)}")
                raise

        # Analyze opponent's players
        for player in opponent_players:
            try:
                logger.info(f"Analyzing opponent player: {player.get('player_name')}")
                analysis = _analyze_player_for_matchup(
                    player,
                    is_user_player=False,
                    week=matchup_data['week'],
                    season=matchup_data.get('season', 2024)
                )
                analysis_results.append(analysis)

                # Save to database
                _save_matchup_analysis(matchup_id, analysis, is_user_player=False)
            except Exception as e:
                logger.error(f"Error analyzing opponent player {player.get('player_name')}: {str(e)}")
                raise

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


def _analyze_player_for_matchup(player, is_user_player, week, season=2024):
    """Analyze a single player for the matchup"""
    player_team = player.get('team')

    # Get real opponent defense from NFL schedule
    opponent_team = api_client.get_team_opponent(player_team, season, week)

    # Get historical performance vs this opponent
    historical_stats = None
    if opponent_team and player.get('player_id'):
        historical_stats = api_client.get_player_stats_vs_team(
            player.get('player_id'),
            opponent_team
        )

    # Calculate matchup score based on position and opponent
    matchup_score = _calculate_matchup_score(player['position'], player_team, opponent_team)

    # Get weather data for player's team location
    weather_data = weather_service.get_game_weather(player_team)

    # Evaluate injury impact
    injury_impact = _evaluate_injury_impact(player.get('injury_status', 'HEALTHY'))

    # Calculate projected points with weather adjustment
    projected_points = _calculate_projected_points(
        player['position'],
        matchup_score,
        injury_impact,
        weather_data
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

    # Generate reasoning with historical context
    reasoning = _generate_reasoning(
        player,
        matchup_score,
        injury_impact,
        recommendation,
        weather_data,
        opponent_team,
        historical_stats
    )

    # Prepare weather info for response
    weather_info = None
    if weather_data:
        weather_info = {
            'condition': weather_data.get('condition'),
            'temperature': weather_data.get('temperature'),
            'wind_speed': weather_data.get('wind_speed'),
            'impact': weather_data.get('impact')
        }

    # Prepare historical stats for response
    historical_info = None
    if historical_stats:
        historical_info = {
            'games_played': historical_stats.get('games_played'),
            'avg_fantasy_points': historical_stats.get('avg_fantasy_points')
        }

    return {
        'player_id': player.get('player_id'),
        'player_name': player['player_name'],
        'position': player['position'],
        'team': player['team'],
        'is_user_player': is_user_player,
        'opponent_team': opponent_team or 'N/A',
        'matchup_score': round(matchup_score, 2),
        'projected_points': round(projected_points, 2),
        'ai_grade': ai_grade,
        'recommendation': recommendation,
        'injury_status': player.get('injury_status', 'HEALTHY'),
        'injury_impact': injury_impact,
        'confidence_score': round(confidence_score, 2),
        'reasoning': reasoning,
        'weather': weather_info,
        'historical_vs_opponent': historical_info
    }


def _calculate_matchup_score(position, team, opponent_team=None):
    """Calculate matchup difficulty score (0-100)"""
    # Base score by position
    base_scores = {
        'QB': 75,
        'RB': 70,
        'WR': 72,
        'TE': 68,
        'K': 65,
        'DEF': 70
    }

    base = base_scores.get(position, 70)

    # If we have opponent data, adjust based on known tough/easy defenses
    # This is simplified - in production would fetch real defensive rankings
    if opponent_team:
        # Tough defenses against pass (lower score = tougher matchup)
        tough_vs_pass = ['SF', 'BAL', 'BUF', 'DAL', 'PIT']
        # Tough defenses against run
        tough_vs_run = ['SF', 'BAL', 'CLE', 'NYJ']
        # Weak defenses (favorable matchups)
        weak_defenses = ['ARI', 'CAR', 'DEN', 'LV', 'WAS']

        if position in ['QB', 'WR', 'TE'] and opponent_team in tough_vs_pass:
            base -= 12
        elif position == 'RB' and opponent_team in tough_vs_run:
            base -= 12
        elif opponent_team in weak_defenses:
            base += 12

    # Add some variance (+/- 8 points) for variability
    variance = random.uniform(-8, 8)

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


def _calculate_projected_points(position, matchup_score, injury_impact, weather_data=None):
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

    # Adjust for weather
    weather_mult = 1.0
    if weather_data:
        weather_mult = weather_service.get_weather_adjustment_factor(position, weather_data)

    return base * matchup_multiplier * injury_mult * weather_mult


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


def _generate_reasoning(player, matchup_score, injury_impact, recommendation, weather_data=None, opponent_team=None, historical_stats=None):
    """Generate AI-powered reasoning using Groq (free tier)"""
    try:
        # Build weather context for AI
        weather_context = None
        if weather_data and not weather_data.get('dome'):
            weather_context = f"{weather_data.get('condition')} ({weather_data.get('temperature')}°F, {weather_data.get('wind_speed')} mph winds)"

        # Build historical context
        historical_context = None
        if historical_stats and historical_stats.get('games_played', 0) > 0:
            historical_context = f"Averages {historical_stats['avg_fantasy_points']} pts vs {opponent_team} in {historical_stats['games_played']} games"

        # Use AI service for intelligent reasoning
        reasoning = ai_service.generate_matchup_reasoning(
            player_name=player['player_name'],
            position=player['position'],
            matchup_score=matchup_score,
            injury_status=player.get('injury_status', 'HEALTHY'),
            opponent_defense=opponent_team,
            weather=weather_context,
            historical_performance=historical_context
        )
        return reasoning
    except Exception as e:
        logger.error(f"AI reasoning failed, using fallback: {e}")
        # Fallback to rule-based concise snippet
        reasoning_parts = []

        # START recommendation - focus on why to start them
        if recommendation == 'START':
            if historical_stats and historical_stats.get('avg_fantasy_points', 0) > 12:
                reasoning_parts.append(f"Strong history vs {opponent_team} ({historical_stats['avg_fantasy_points']} pts/game)")
            elif matchup_score >= 75:
                reasoning_parts.append(f"Favorable matchup vs {opponent_team if opponent_team else 'opponent'}")
            else:
                reasoning_parts.append(f"Solid play with {player['position']} upside")

            if weather_data and not weather_data.get('dome'):
                if player['position'] == 'RB' and ('rain' in weather_data.get('condition', '').lower() or 'snow' in weather_data.get('condition', '').lower()):
                    reasoning_parts.append("Weather favors run game")

        # SIT recommendation - focus on why to bench them
        elif recommendation == 'SIT':
            if 'Cannot play' in injury_impact or 'unlikely to play' in injury_impact:
                return f"Do not start - {injury_impact.lower()}"
            elif matchup_score < 50:
                reasoning_parts.append(f"Tough matchup vs {opponent_team if opponent_team else 'opponent'} defense")
            if historical_stats and historical_stats.get('avg_fantasy_points', 0) < 8:
                reasoning_parts.append(f"Struggles vs {opponent_team} historically")

        # CONSIDER recommendation - provide key factors
        else:
            reasoning_parts.append(f"Monitor status vs {opponent_team if opponent_team else 'opponent'}")
            if 'game-time decision' in injury_impact.lower():
                reasoning_parts.append("Check injury report before kickoff")
            if historical_stats:
                reasoning_parts.append(f"Averages {historical_stats['avg_fantasy_points']} pts vs this defense")

        return '. '.join(reasoning_parts) + '.' if reasoning_parts else f"{recommendation} - Standard matchup expected."


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
