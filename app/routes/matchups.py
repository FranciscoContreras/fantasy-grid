from flask import Blueprint, request, jsonify
from app.database import execute_query
from app.services.ai_service import AIService
from app.services.weather_service import WeatherService
from app.services.api_client import FantasyAPIClient
from app.services.matchup_data_service import MatchupDataService
from app.services.season_service import SeasonService
import logging
from datetime import datetime
import random

bp = Blueprint('matchups', __name__, url_prefix='/api/matchups')
logger = logging.getLogger(__name__)

# Initialize services
ai_service = AIService()
weather_service = WeatherService()
api_client = FantasyAPIClient()
matchup_data_service = MatchupDataService()
season_service = SeasonService()


@bp.route('', methods=['POST'])
def create_matchup():
    """Create a weekly roster analysis

    Workflow:
    1. Build your roster (assign players as starters)
    2. Create matchup with roster_id + week
    3. System determines which NFL defense each player faces
    4. Analyzes matchup quality, defensive players, coordinator, weather, history
    5. Returns start rankings and recommendations
    """
    data = request.json
    week = data.get('week')
    season = data.get('season', 2024)
    user_roster_id = data.get('user_roster_id')
    opponent_roster_id = data.get('opponent_roster_id')  # Legacy support

    if not all([week, user_roster_id]):
        return jsonify({'error': 'week and user_roster_id are required'}), 400

    # Default to current season if not provided
    if not season:
        season = 2024

    # Opponent roster not needed but keep for backward compatibility
    if not opponent_roster_id:
        opponent_roster_id = user_roster_id

    # Validate schedule availability before creating matchup
    if not season_service.validate_week(season, week):
        logger.warning(f"Attempted to create matchup for unavailable week: {season} Week {week}")
        return jsonify({
            'error': f'Schedule not available for {season} Week {week} yet. Please select a different week.'
        }), 400

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


@bp.route('/current-week', methods=['GET'])
def get_current_week():
    """Get the current NFL season and week"""
    try:
        season, week = season_service.get_current_season_and_week()
        return jsonify({
            'data': {
                'season': season,
                'week': week
            }
        })
    except Exception as e:
        logger.error(f"Error getting current week: {str(e)}")
        return jsonify({'error': 'Failed to get current week'}), 500


@bp.route('/available-weeks', methods=['GET'])
def get_available_weeks():
    """Get list of weeks with available schedule data"""
    try:
        season = request.args.get('season', type=int)
        start_week = request.args.get('start_week', type=int, default=1)

        # Default to current season if not provided
        if not season:
            season, _ = season_service.get_current_season_and_week()

        available_weeks = season_service.get_available_weeks(season, start_week)

        return jsonify({
            'data': {
                'season': season,
                'available_weeks': available_weeks,
                'count': len(available_weeks)
            }
        })
    except Exception as e:
        logger.error(f"Error getting available weeks: {str(e)}")
        return jsonify({'error': 'Failed to get available weeks'}), 500


@bp.route('/season/<int:roster_id>', methods=['GET'])
def get_season_matchups(roster_id):
    """Get comprehensive season-long matchup analysis for a roster"""
    try:
        # Get roster info
        roster_query = "SELECT id, name FROM rosters WHERE id = %s"
        roster = execute_query(roster_query, (roster_id,))

        if not roster:
            return jsonify({'error': 'Roster not found'}), 404

        roster_data = roster[0]

        # Get roster players
        players_query = """
            SELECT rp.id, rp.player_id, rp.player_name, rp.position, rp.team,
                   rp.roster_slot, rp.is_starter, rp.injury_status
            FROM roster_players rp
            WHERE rp.roster_id = %s AND rp.is_starter = true
        """
        roster_players = execute_query(players_query, (roster_id,))

        if not roster_players:
            return jsonify({'error': 'No starters found in roster'}), 404

        logger.info(f"Fetching season matchups for roster {roster_id} with {len(roster_players)} players")

        # Use matchup data service to get all future matchups
        season_data = matchup_data_service.get_season_matchups(
            roster_id,
            roster_players
        )

        return jsonify({
            'data': {
                'roster_id': roster_id,
                'roster_name': roster_data.get('name'),
                'season': season_data.get('season'),
                'total_weeks': season_data.get('total_weeks'),
                'matchups': season_data.get('matchups', {})
            }
        })

    except Exception as e:
        logger.error(f"Error fetching season matchups: {str(e)}")
        return jsonify({'error': 'Failed to fetch season matchups'}), 500


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
                   recommendation, injury_impact, confidence_score, reasoning, analyzed_at,
                   analysis_status
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


@bp.route('/player/<player_id>', methods=['GET'])
def get_player_details(player_id):
    """
    Get detailed player information including recent games and career stats.

    Returns:
        Player info, career stats, and last 20 games performance
    """
    try:
        # Get player basic info
        player_info = api_client.get_player_data(player_id)

        # Get recent games (last 20)
        recent_games = api_client.get_player_recent_games(player_id, limit=20)

        # Get career stats
        try:
            career_stats = api_client.get_player_career_stats(player_id)
        except Exception as e:
            logger.warning(f"Could not fetch career stats for {player_id}: {e}")
            career_stats = None

        return jsonify({
            'data': {
                'player': player_info,
                'recent_games': recent_games,
                'career_stats': career_stats
            }
        }), 200

    except Exception as e:
        logger.error(f"Error fetching player details for {player_id}: {str(e)}")
        return jsonify({'error': 'Failed to fetch player details'}), 500


@bp.route('/<int:matchup_id>/analyze', methods=['POST'])
def analyze_matchup(matchup_id):
    """
    Analyze a matchup and generate start/sit recommendations.
    Phase 1: Returns immediately with basic analysis (no Grok)
    Phase 2: Triggers background Grok analysis that updates progressively
    """
    import threading

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
        week = matchup_data.get('week')
        season = matchup_data.get('season', 2024)
        logger.info(f"Starting analysis for matchup {matchup_id}: Week {week}, Season {season}")

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
        logger.info(f"Found {len(user_players)} user players to analyze")

        # Prepare comprehensive analysis data (fetch all opponent data once)
        analysis_data = matchup_data_service.prepare_bulk_analysis_data(
            matchup_data['user_roster_id'],
            user_players,
            season,
            week
        )

        # Clear existing analysis
        delete_query = "DELETE FROM matchup_analysis WHERE matchup_id = %s"
        execute_query(delete_query, (matchup_id,))

        # Phase 1: Generate BASIC analysis immediately (no Grok calls yet)
        basic_results = []
        for player_data in analysis_data:
            try:
                player = player_data.get('player')

                # Generate basic analysis without Grok reasoning
                basic_analysis = _generate_basic_analysis(
                    player_data,
                    is_user_player=True,
                    week=week,
                    season=season
                )
                basic_results.append(basic_analysis)

                # Save to database with status='analyzing'
                _save_matchup_analysis(matchup_id, basic_analysis, is_user_player=True, status='analyzing')

            except Exception as e:
                logger.error(f"Error in basic analysis for {player.get('player_name')}: {str(e)}")

        # Mark matchup as analyzed (basic analysis complete)
        update_query = """
            UPDATE matchups
            SET analyzed = true, analyzed_at = CURRENT_TIMESTAMP
            WHERE id = %s
        """
        execute_query(update_query, (matchup_id,))

        # Generate basic recommendations
        recommendations = _generate_recommendations(user_players, basic_results)

        # Phase 2: Start background thread for Grok analysis
        def generate_grok_analyses_async():
            """Background task to generate Grok analyses one by one"""
            try:
                logger.info(f"Starting background Grok analysis for matchup {matchup_id}")
                for player_data in analysis_data:
                    try:
                        player = player_data.get('player')
                        player_name = player.get('player_name')

                        logger.info(f"Generating Grok analysis for {player_name}")

                        # Generate full analysis with Grok
                        full_analysis = _analyze_player_with_data(
                            player_data,
                            is_user_player=True,
                            week=week,
                            season=season
                        )

                        # Update database with completed analysis
                        _update_matchup_analysis_reasoning(
                            matchup_id,
                            player.get('player_id'),
                            player_name,
                            full_analysis.get('reasoning'),
                            status='completed'
                        )

                        logger.info(f"Completed Grok analysis for {player_name}")

                    except Exception as e:
                        logger.error(f"Error in Grok analysis for {player.get('player_name')}: {str(e)}")
                        # Mark as failed but continue with others
                        _update_analysis_status(matchup_id, player.get('player_id'), player.get('player_name'), 'failed')

                logger.info(f"Background Grok analysis completed for matchup {matchup_id}")
            except Exception as e:
                logger.error(f"Fatal error in background Grok analysis: {str(e)}")

        # Start background thread
        thread = threading.Thread(target=generate_grok_analyses_async)
        thread.daemon = True
        thread.start()

        # Return immediately with basic analysis
        return jsonify({
            'data': {
                'matchup_id': matchup_id,
                'analysis': basic_results,
                'recommendations': recommendations,
                'status': 'analyzing',
                'message': 'Basic analysis complete. AI analysis generating in background...'
            }
        })

    except Exception as e:
        logger.error(f"Error analyzing matchup {matchup_id}: {str(e)}")
        return jsonify({'error': f'Failed to analyze matchup: {str(e)}'}), 500


def _analyze_player_for_matchup(player, is_user_player, week, season=2024):
    """
    Comprehensive player analysis including:
    - Real NFL opponent defense
    - Historical performance vs that defense
    - Defensive coordinator scheme
    - Key defensive players they'll face
    - Weather conditions
    - Injury status
    - Start ranking (1-10)
    """
    player_team = player.get('team')
    player_position = player['position']

    # Get real opponent defense from NFL schedule
    opponent_team = api_client.get_team_opponent(player_team, season, week)

    # Get defensive coordinator
    def_coordinator = None
    key_defenders = []
    if opponent_team:
        def_coordinator = api_client.get_defensive_coordinator(opponent_team, season)

        # Get relevant defensive players based on offensive position
        if player_position == 'QB':
            # QBs care about pass rush and coverage
            key_defenders = api_client.get_key_defensive_players(opponent_team, 'DL') or []
        elif player_position in ['WR', 'TE']:
            # Pass catchers care about coverage
            key_defenders = api_client.get_key_defensive_players(opponent_team, 'DB') or []
        elif player_position == 'RB':
            # RBs care about front 7
            dl = api_client.get_key_defensive_players(opponent_team, 'DL') or []
            lb = api_client.get_key_defensive_players(opponent_team, 'LB') or []
            key_defenders = dl + lb

    # Get historical performance vs this opponent
    historical_stats = None
    if opponent_team and player.get('player_id'):
        historical_stats = api_client.get_player_stats_vs_team(
            player.get('player_id'),
            opponent_team
        )

    # Calculate matchup score based on position and opponent
    matchup_score = _calculate_matchup_score(player_position, player_team, opponent_team)

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

    # Calculate start ranking (1-10 scale)
    start_ranking = _calculate_start_ranking(
        matchup_score,
        projected_points,
        injury_impact,
        historical_stats,
        player_position
    )

    # Generate reasoning with all context
    reasoning = _generate_reasoning(
        player,
        matchup_score,
        injury_impact,
        recommendation,
        weather_data,
        opponent_team,
        historical_stats,
        def_coordinator,
        key_defenders
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

    # Prepare defensive matchup info
    defensive_matchup = {
        'opponent_defense': opponent_team or 'N/A',
        'defensive_coordinator': def_coordinator,
        'key_defenders': key_defenders[:3] if key_defenders else []  # Top 3 most relevant
    }

    return {
        'player_id': player.get('player_id'),
        'player_name': player['player_name'],
        'position': player['position'],
        'team': player['team'],
        'is_user_player': is_user_player,
        'opponent_team': opponent_team or 'N/A',
        'defensive_matchup': defensive_matchup,
        'matchup_score': round(matchup_score, 2),
        'projected_points': round(projected_points, 2),
        'start_ranking': start_ranking,
        'ai_grade': ai_grade,
        'recommendation': recommendation,
        'injury_status': player.get('injury_status', 'HEALTHY'),
        'injury_impact': injury_impact,
        'confidence_score': round(confidence_score, 2),
        'reasoning': reasoning,
        'weather': weather_info,
        'historical_vs_opponent': historical_info
    }


def _analyze_player_with_data(player_data, is_user_player, week, season):
    """
    Analyze player using comprehensive data from matchup_data_service.
    This replaces the old _analyze_player_for_matchup by using pre-fetched data.
    Falls back to simulated analysis if no opponent data is available.
    Uses two-tier caching (Redis + PostgreSQL) to avoid duplicate Grok calls.
    """
    from app.services.cache_service import get_cached_analysis, cache_analysis

    player = player_data.get('player')
    opponent_team = player_data.get('opponent')
    player_id = player.get('player_id')
    player_name = player.get('player_name')

    # If no opponent found but not explicitly marked as bye week,
    # treat as a regular game with unknown opponent (generate analysis anyway)
    has_game = player_data.get('has_game', True)
    if not has_game and opponent_team is None:
        # True bye week - no game scheduled
        return {
            'player_id': player_id,
            'player_name': player_name,
            'position': player.get('position'),
            'team': player.get('team'),
            'is_user_player': is_user_player,
            'opponent_team': 'BYE',
            'matchup_score': 0,
            'projected_points': 0,
            'ai_grade': 'F',
            'recommendation': 'SIT',
            'injury_status': player.get('injury_status', 'HEALTHY'),
            'injury_impact': 'Bye week - not playing',
            'confidence_score': 100,
            'reasoning': f"{player_name} is on a bye week and will not play."
        }

    # Check cache first (only if opponent is known)
    if opponent_team:
        cached = get_cached_analysis(player_id, player_name, opponent_team, week, season)
        if cached:
            logger.info(f"Using cached analysis for {player_name} vs {opponent_team} Week {week}")
            # Return cached data merged with player info
            return {
                'player_id': player_id,
                'player_name': player_name,
                'position': player.get('position'),
                'team': player.get('team'),
                'is_user_player': is_user_player,
                'opponent_team': opponent_team,
                'matchup_score': cached.get('matchup_score', 0),
                'projected_points': cached.get('projected_points', 0),
                'ai_grade': cached.get('ai_grade', 'C'),
                'recommendation': cached.get('recommendation', 'CONSIDER'),
                'injury_status': cached.get('injury_status', 'HEALTHY'),
                'injury_impact': _evaluate_injury_impact(cached.get('injury_status', 'HEALTHY')),
                'confidence_score': cached.get('confidence_score', 70),
                'reasoning': cached.get('reasoning', '')
            }

    player_position = player.get('position')

    # Extract data from comprehensive fetch (may be None/empty)
    def_coordinator = player_data.get('defensive_coordinator')
    key_defenders = player_data.get('key_defenders', [])
    historical_stats = player_data.get('historical_performance')
    injury_status = player_data.get('injury_status', 'HEALTHY')
    opponent_roster = player_data.get('opponent_roster')
    defensive_stats = player_data.get('defensive_stats')

    # Calculate matchup score (works even without opponent)
    matchup_score = _calculate_matchup_score(player_position, player.get('team'), opponent_team)

    # Get weather data
    weather_data = weather_service.get_game_weather(player.get('team'))

    # Evaluate injury impact
    injury_impact = _evaluate_injury_impact(injury_status)

    # Calculate projected points
    projected_points = _calculate_projected_points(
        player_position,
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
        injury_status
    )

    # Calculate confidence score
    confidence_score = _calculate_confidence(matchup_score, injury_impact)

    # Extract new data
    injury_history = player_data.get('injury_history')
    weather_forecast = player_data.get('weather_forecast')

    # Generate reasoning with all context
    reasoning = _generate_reasoning(
        player,
        matchup_score,
        injury_impact,
        recommendation,
        weather_data,
        opponent_team if opponent_team else 'Unknown',
        historical_stats,
        def_coordinator,
        key_defenders,
        opponent_roster,
        defensive_stats,
        injury_history,
        weather_forecast
    )

    # Cache the analysis for future use (only if opponent is known)
    if opponent_team:
        try:
            opponent_def_rank = None
            if defensive_stats:
                opponent_def_rank = defensive_stats.get('defensive_rank')

            cache_analysis(
                player_id=player_id,
                player_name=player_name,
                position=player_position,
                team=player.get('team'),
                opponent_team=opponent_team,
                week=week,
                season=season,
                matchup_score=round(matchup_score, 2),
                projected_points=round(projected_points, 2),
                recommendation=recommendation,
                ai_grade=ai_grade,
                confidence_score=round(confidence_score, 2),
                reasoning=reasoning,
                injury_status=injury_status,
                opponent_defense_rank=opponent_def_rank,
                historical_performance=historical_stats
            )
            logger.debug(f"Cached analysis for {player_name} vs {opponent_team} Week {week}")
        except Exception as e:
            logger.error(f"Error caching analysis: {e}")
            # Don't fail the analysis if caching fails

    return {
        'player_id': player_id,
        'player_name': player_name,
        'position': player_position,
        'team': player.get('team'),
        'is_user_player': is_user_player,
        'opponent_team': opponent_team or 'TBD',
        'matchup_score': round(matchup_score, 2),
        'projected_points': round(projected_points, 2),
        'ai_grade': ai_grade,
        'recommendation': recommendation,
        'injury_status': injury_status,
        'injury_impact': injury_impact,
        'confidence_score': round(confidence_score, 2),
        'reasoning': reasoning
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


def _calculate_start_ranking(matchup_score, projected_points, injury_impact, historical_stats, position):
    """
    Calculate start ranking on 1-10 scale.

    10 = Must start (elite matchup, high floor)
    7-9 = Start with confidence
    5-6 = Flex consideration / Matchup dependent
    3-4 = Risky start / Sit if you have better options
    1-2 = Avoid / Sit

    Factors:
    - Matchup quality (40%)
    - Projected points (30%)
    - Historical performance (20%)
    - Injury status (10%)
    """
    ranking = 5.0  # Start at average

    # Matchup quality (40% weight)
    if matchup_score >= 85:
        ranking += 2.0
    elif matchup_score >= 75:
        ranking += 1.5
    elif matchup_score >= 65:
        ranking += 0.5
    elif matchup_score < 50:
        ranking -= 1.5
    elif matchup_score < 40:
        ranking -= 2.0

    # Projected points relative to position (30% weight)
    position_thresholds = {
        'QB': {'elite': 22, 'good': 18, 'poor': 12},
        'RB': {'elite': 15, 'good': 12, 'poor': 8},
        'WR': {'elite': 14, 'good': 11, 'poor': 7},
        'TE': {'elite': 12, 'good': 9, 'poor': 6},
        'K': {'elite': 10, 'good': 8, 'poor': 5},
        'DEF': {'elite': 10, 'good': 7, 'poor': 4}
    }

    thresholds = position_thresholds.get(position, {'elite': 15, 'good': 10, 'poor': 5})

    if projected_points >= thresholds['elite']:
        ranking += 1.5
    elif projected_points >= thresholds['good']:
        ranking += 0.5
    elif projected_points < thresholds['poor']:
        ranking -= 1.0

    # Historical performance (20% weight)
    if historical_stats:
        avg_points = historical_stats.get('avg_fantasy_points', 0)
        if avg_points >= thresholds['elite']:
            ranking += 1.0
        elif avg_points >= thresholds['good']:
            ranking += 0.5
        elif avg_points < thresholds['poor']:
            ranking -= 0.5

    # Injury impact (10% weight)
    if 'Cannot play' in injury_impact:
        return 1  # Absolute avoid
    elif 'unlikely to play' in injury_impact:
        ranking -= 2.0
    elif 'game-time decision' in injury_impact:
        ranking -= 1.0
    elif 'Minimal impact' in injury_impact:
        ranking -= 0.3

    # Cap between 1-10
    return max(1, min(10, round(ranking)))


def _generate_reasoning(player, matchup_score, injury_impact, recommendation, weather_data=None, opponent_team=None, historical_stats=None, def_coordinator=None, key_defenders=None, opponent_roster=None, defensive_stats=None, injury_history=None, weather_forecast=None):
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

        # Build defensive context
        defensive_context = None
        if def_coordinator or key_defenders:
            parts = []
            if def_coordinator and def_coordinator != 'Unknown':
                parts.append(f"DC: {def_coordinator}")
            if key_defenders and len(key_defenders) > 0:
                defenders_str = ', '.join(key_defenders[:2])  # Top 2
                parts.append(f"Key defenders: {defenders_str}")
            if parts:
                defensive_context = '; '.join(parts)

        # Use AI service for intelligent reasoning with enhanced context
        reasoning = ai_service.generate_matchup_reasoning(
            player_name=player['player_name'],
            position=player['position'],
            team=player.get('team', 'N/A'),
            matchup_score=matchup_score,
            injury_status=player.get('injury_status', 'HEALTHY'),
            opponent_defense=opponent_team,
            opponent_roster=opponent_roster,
            defensive_stats=defensive_stats,
            weather=weather_context,
            historical_performance=historical_context,
            defensive_scheme=defensive_context,
            injury_history=injury_history,
            weather_forecast=weather_forecast
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


def _generate_basic_analysis(player_data, is_user_player, week, season):
    """
    Generate basic analysis WITHOUT calling Grok AI.
    This is fast and returns immediately.
    """
    player = player_data.get('player')
    opponent_team = player_data.get('opponent')
    player_id = player.get('player_id')
    player_name = player.get('player_name')
    player_position = player.get('position')

    # Handle bye week
    has_game = player_data.get('has_game', True)
    if not has_game and opponent_team is None:
        return {
            'player_id': player_id,
            'player_name': player_name,
            'position': player_position,
            'team': player.get('team'),
            'is_user_player': is_user_player,
            'opponent_team': 'BYE',
            'matchup_score': 0,
            'projected_points': 0,
            'ai_grade': 'F',
            'recommendation': 'SIT',
            'injury_status': player.get('injury_status', 'HEALTHY'),
            'injury_impact': 'Bye week - not playing',
            'confidence_score': 100,
            'reasoning': 'Analyzing...'
        }

    # Extract data
    injury_status = player_data.get('injury_status', 'HEALTHY')
    defensive_stats = player_data.get('defensive_stats')

    # Calculate scores (fast, no AI)
    matchup_score = _calculate_matchup_score(player_position, player.get('team'), opponent_team)
    weather_data = weather_service.get_game_weather(player.get('team'))
    injury_impact = _evaluate_injury_impact(injury_status)
    projected_points = _calculate_projected_points(player_position, matchup_score, injury_impact, weather_data)
    ai_grade = _assign_grade(matchup_score, injury_impact)
    recommendation = _generate_recommendation(matchup_score, injury_impact, injury_status)
    confidence_score = _calculate_confidence(matchup_score, injury_impact)

    return {
        'player_id': player_id,
        'player_name': player_name,
        'position': player_position,
        'team': player.get('team'),
        'is_user_player': is_user_player,
        'opponent_team': opponent_team or 'TBD',
        'matchup_score': round(matchup_score, 2),
        'projected_points': round(projected_points, 2),
        'ai_grade': ai_grade,
        'recommendation': recommendation,
        'injury_status': injury_status,
        'injury_impact': injury_impact,
        'confidence_score': round(confidence_score, 2),
        'reasoning': 'Generating AI analysis...'
    }


def _save_matchup_analysis(matchup_id, analysis, is_user_player, status='completed'):
    """Save analysis to database with status"""
    query = """
        INSERT INTO matchup_analysis
        (matchup_id, player_id, player_name, position, is_user_player, opponent_team,
         matchup_score, projected_points, ai_grade, recommendation, injury_impact,
         confidence_score, reasoning, analysis_status)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
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
        analysis['reasoning'],
        status
    ))


def _update_matchup_analysis_reasoning(matchup_id, player_id, player_name, reasoning, status='completed'):
    """Update just the reasoning field for a player"""
    query = """
        UPDATE matchup_analysis
        SET reasoning = %s, analysis_status = %s
        WHERE matchup_id = %s
          AND (player_id = %s OR player_name = %s)
    """
    execute_query(query, (reasoning, status, matchup_id, player_id, player_name))


def _update_analysis_status(matchup_id, player_id, player_name, status):
    """Update just the status field for a player"""
    query = """
        UPDATE matchup_analysis
        SET analysis_status = %s
        WHERE matchup_id = %s
          AND (player_id = %s OR player_name = %s)
    """
    execute_query(query, (status, matchup_id, player_id, player_name))


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
