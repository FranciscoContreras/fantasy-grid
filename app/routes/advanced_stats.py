"""
Advanced Stats Routes - API v2 Integration
Exposes Next Gen Stats, EPA, CPOE, play-by-play data
"""

from flask import Blueprint, jsonify, request
import logging
from app.services.api_client import FantasyAPIClient
from app.services.ai_grader import AIGrader
from app.services.analyzer import PlayerAnalyzer

logger = logging.getLogger(__name__)

bp = Blueprint('advanced_stats', __name__, url_prefix='/api/advanced')

api_client = FantasyAPIClient()
ai_grader = AIGrader()
analyzer = PlayerAnalyzer()


@bp.route('/players', methods=['GET'])
def list_players():
    """
    List players with flexible filtering (API v2).

    Query params:
        - position (str): Filter by position (QB, RB, WR, TE, etc.)
        - status (str): Filter by status (active, injured, etc.)
        - team (str): Filter by team abbreviation or ID
        - limit (int): Results per page (default: 50)
        - offset (int): Pagination offset (default: 0)

    Returns:
        List of players matching filters with basic info
    """
    try:
        position = request.args.get('position')
        status = request.args.get('status')
        team = request.args.get('team')
        limit = request.args.get('limit', 50, type=int)
        offset = request.args.get('offset', 0, type=int)

        players = api_client.get_players_list_v2(
            position=position,
            status=status,
            team=team,
            limit=limit,
            offset=offset
        )

        return jsonify({
            'data': players,
            'meta': {
                'position': position,
                'status': status,
                'team': team,
                'limit': limit,
                'offset': offset,
                'count': len(players)
            }
        })

    except Exception as e:
        logger.error(f"Failed to list players: {e}")
        return jsonify({'error': str(e)}), 500


@bp.route('/players/<player_id>/history', methods=['GET'])
def get_player_history(player_id):
    """
    Get player's complete team history (API v2).

    Returns:
        List of all teams the player has been on with seasons
    """
    try:
        history = api_client.get_player_team_history_v2(player_id)

        return jsonify({
            'data': history,
            'meta': {
                'player_id': player_id,
                'teams_count': len(history) if history else 0
            }
        })

    except Exception as e:
        logger.error(f"Failed to fetch player history for {player_id}: {e}")
        return jsonify({'error': str(e)}), 500


@bp.route('/players/<player_id>/vs-defense/<defense_team_id>', methods=['GET'])
def get_player_vs_defense(player_id, defense_team_id):
    """
    Get player's performance vs a specific defense (API v2).

    Query params:
        - season (int): Filter by season (optional)
        - limit (int): Number of games (default: 10)

    Returns:
        Historical performance data vs the specified defense
    """
    try:
        season = request.args.get('season', type=int)
        limit = request.args.get('limit', 10, type=int)

        stats = api_client.get_player_vs_defense_v2(
            player_id=player_id,
            defense_team_id=defense_team_id,
            season=season,
            limit=limit
        )

        return jsonify({
            'data': stats,
            'meta': {
                'player_id': player_id,
                'defense_team_id': defense_team_id,
                'season': season,
                'games': len(stats) if isinstance(stats, list) else 0
            }
        })

    except Exception as e:
        logger.error(f"Failed to fetch player vs defense stats: {e}")
        return jsonify({'error': str(e)}), 500


@bp.route('/players/<player_id>/nextgen', methods=['GET'])
def get_player_nextgen_stats(player_id):
    """
    Get Next Gen Stats for a player.

    Query params:
        - season (int): Season year (default: 2024)
        - week (int): Specific week (optional)
        - stat_type (str): Filter by type (nextgen, epa, cpoe, etc.)

    Returns:
        Next Gen Stats including:
        - Air yards, separation, YAC
        - EPA, CPOE, success rate
        - Route running metrics
    """
    try:
        season = request.args.get('season', 2025, type=int)
        week = request.args.get('week', type=int)
        stat_type = request.args.get('stat_type')

        advanced_stats = api_client.get_player_advanced_stats(
            player_id=player_id,
            season=season,
            week=week,
            stat_type=stat_type
        )

        if not advanced_stats:
            return jsonify({'error': 'Advanced stats not found'}), 404

        return jsonify({
            'data': advanced_stats,
            'meta': {
                'player_id': player_id,
                'season': season,
                'week': week,
                'stat_type': stat_type
            }
        })

    except Exception as e:
        logger.error(f"Failed to fetch Next Gen Stats for player {player_id}: {e}")
        return jsonify({'error': str(e)}), 500


@bp.route('/players/<player_id>/enhanced-analysis', methods=['GET'])
def get_enhanced_player_analysis(player_id):
    """
    Get comprehensive player analysis using advanced stats.

    Query params:
        - opponent (str): Opponent team abbreviation (required)
        - season (int): Season year (default: 2024)
        - week (int): Week number (optional)

    Returns:
        Enhanced analysis with:
        - Traditional metrics
        - Next Gen Stats
        - Advanced matchup scoring
        - Trend analysis
        - AI-powered grading with insights
    """
    try:
        opponent = request.args.get('opponent')
        season = request.args.get('season', 2025, type=int)
        week = request.args.get('week', type=int)

        if not opponent:
            return jsonify({'error': 'opponent parameter required'}), 400

        # Get player data
        player_data = api_client.get_player_data(player_id)
        if not player_data:
            return jsonify({'error': 'Player not found'}), 404

        player_info = player_data.get('data', player_data)
        position = player_info.get('position')

        # Get advanced stats
        advanced_stats = api_client.get_player_advanced_stats(player_id, season=season, week=week)

        # Get defense advanced stats
        defense_stats = api_client.get_defense_rankings_v2(category='overall', season=season)
        opponent_defense = next((d for d in defense_stats if d.get('team_abbr') == opponent), None)

        # Calculate advanced matchup score
        matchup_analysis = analyzer.calculate_advanced_matchup_score(
            player_position=position,
            player_advanced_stats=advanced_stats,
            defense_advanced_stats=opponent_defense
        )

        # Get AI grading with advanced stats
        player_features = [
            player_info.get('avg_points', 10),
            matchup_analysis['score'],
            100,  # Default weather
            75  # Default consistency
        ]

        ai_features = ai_grader.extract_advanced_features(advanced_stats) if advanced_stats else None
        ai_grade = ai_grader.grade_player_with_advanced_stats(player_features, ai_features)

        # Build response
        response = {
            'player': {
                'id': player_id,
                'name': player_info.get('name'),
                'position': position,
                'team': player_info.get('team')
            },
            'opponent': opponent,
            'matchup_analysis': matchup_analysis,
            'ai_grade': ai_grade,
            'advanced_stats': advanced_stats,
            'season': season,
            'week': week
        }

        return jsonify({'data': response})

    except Exception as e:
        logger.error(f"Failed enhanced analysis for player {player_id}: {e}")
        return jsonify({'error': str(e)}), 500


@bp.route('/games/<game_id>/play-by-play', methods=['GET'])
def get_game_play_by_play(game_id):
    """
    Get detailed play-by-play data for a game.

    Returns:
        Complete play-by-play with:
        - Down and distance
        - Play outcomes
        - Player involvement
        - EPA, WPA
        - Field position
    """
    try:
        plays = api_client.get_game_play_by_play(game_id)

        if not plays:
            return jsonify({'error': 'Play-by-play data not found'}), 404

        return jsonify({
            'data': plays,
            'meta': {
                'game_id': game_id,
                'total_plays': len(plays)
            }
        })

    except Exception as e:
        logger.error(f"Failed to fetch play-by-play for game {game_id}: {e}")
        return jsonify({'error': str(e)}), 500


@bp.route('/games/<game_id>/scoring-plays', methods=['GET'])
def get_game_scoring_plays(game_id):
    """
    Get all scoring plays from a game.

    Returns:
        List of scoring plays with players involved and score changes
    """
    try:
        scoring = api_client.get_game_scoring_plays(game_id)

        if not scoring:
            return jsonify({'error': 'Scoring plays not found'}), 404

        return jsonify({
            'data': scoring,
            'meta': {
                'game_id': game_id,
                'total_scoring_plays': len(scoring)
            }
        })

    except Exception as e:
        logger.error(f"Failed to fetch scoring plays for game {game_id}: {e}")
        return jsonify({'error': str(e)}), 500


@bp.route('/defense/rankings', methods=['GET'])
def get_defense_rankings():
    """
    Get league-wide defensive rankings with advanced metrics.

    Query params:
        - category (str): overall, pass, rush, scoring (default: overall)
        - season (int): Season year (default: 2024)

    Returns:
        Defensive rankings with advanced stats:
        - EPA allowed
        - Success rate
        - Pressure rate
        - Coverage metrics
    """
    try:
        category = request.args.get('category', 'overall')
        season = request.args.get('season', 2025, type=int)

        rankings = api_client.get_defense_rankings_v2(category=category, season=season)

        if not rankings:
            return jsonify({'error': 'Defense rankings not found'}), 404

        return jsonify({
            'data': rankings,
            'meta': {
                'category': category,
                'season': season,
                'total_teams': len(rankings)
            }
        })

    except Exception as e:
        logger.error(f"Failed to fetch defense rankings: {e}")
        return jsonify({'error': str(e)}), 500


@bp.route('/players/<player_id>/injuries', methods=['GET'])
def get_player_injuries(player_id):
    """
    Get comprehensive injury history and current status for a player.

    Returns:
        Enhanced injury data:
        - Current status
        - Injury type and severity
        - Practice participation
        - Expected return timeline
        - Risk assessment
    """
    try:
        injuries = api_client.get_player_injuries_v2(player_id)

        # Add risk assessment
        risk_assessment = analyzer.calculate_injury_risk_impact(injuries)

        return jsonify({
            'data': {
                'injuries': injuries,
                'risk_assessment': risk_assessment
            },
            'meta': {
                'player_id': player_id,
                'total_injuries': len(injuries) if injuries else 0
            }
        })

    except Exception as e:
        logger.error(f"Failed to fetch injuries for player {player_id}: {e}")
        return jsonify({'error': str(e)}), 500


@bp.route('/teams/<team_id>/injuries', methods=['GET'])
def get_team_injuries(team_id):
    """
    Get current injury report for an entire team.

    Returns:
        Team injury report with practice participation and game status
    """
    try:
        injuries = api_client.get_team_injuries_v2(team_id)

        if not injuries:
            return jsonify({'data': [], 'meta': {'team_id': team_id, 'total_injuries': 0}})

        return jsonify({
            'data': injuries,
            'meta': {
                'team_id': team_id,
                'total_injuries': len(injuries)
            }
        })

    except Exception as e:
        logger.error(f"Failed to fetch team injuries for {team_id}: {e}")
        return jsonify({'error': str(e)}), 500


@bp.route('/ai/query', methods=['POST'])
def ai_natural_language_query():
    """
    Natural language query to AI for NFL data insights.

    Request body:
        {
            "query": "Who are the top 5 rushing leaders this season?"
        }

    Returns:
        AI-generated response with supporting data
    """
    try:
        data = request.get_json()
        query = data.get('query')

        if not query:
            return jsonify({'error': 'query field required'}), 400

        result = api_client.ai_query_v2(query)

        if not result:
            return jsonify({'error': 'AI query failed'}), 500

        return jsonify({
            'data': result,
            'meta': {
                'query': query
            }
        })

    except Exception as e:
        logger.error(f"AI query failed: {e}")
        return jsonify({'error': str(e)}), 500


@bp.route('/ai/predict/game/<game_id>', methods=['GET'])
def ai_predict_game(game_id):
    """
    Get AI-powered game prediction using Claude.

    Returns:
        Comprehensive prediction with:
        - Win probabilities
        - Predicted score
        - Key factors
        - Player impacts
    """
    try:
        prediction = api_client.ai_predict_game_v2(game_id)

        if not prediction:
            return jsonify({'error': 'Game prediction not available'}), 404

        return jsonify({
            'data': prediction,
            'meta': {
                'game_id': game_id,
                'provider': 'Claude (API v2)'
            }
        })

    except Exception as e:
        logger.error(f"AI game prediction failed for {game_id}: {e}")
        return jsonify({'error': str(e)}), 500


@bp.route('/ai/predict/player/<player_id>', methods=['GET'])
def ai_predict_player(player_id):
    """
    Get AI-powered player performance prediction using Claude.

    Query params:
        - opponent (str): Opponent team
        - weather (str): Weather conditions

    Returns:
        AI prediction with:
        - Projected fantasy points
        - Statistical projections
        - Risk factors
        - Opportunity analysis
    """
    try:
        game_context = {
            'opponent': request.args.get('opponent'),
            'weather': request.args.get('weather')
        }

        prediction = api_client.ai_predict_player_v2(player_id, game_context)

        if not prediction:
            return jsonify({'error': 'Player prediction not available'}), 404

        return jsonify({
            'data': prediction,
            'meta': {
                'player_id': player_id,
                'context': game_context,
                'provider': 'Claude (API v2)'
            }
        })

    except Exception as e:
        logger.error(f"AI player prediction failed for {player_id}: {e}")
        return jsonify({'error': str(e)}), 500


@bp.route('/ai/insights/player/<player_id>', methods=['GET'])
def ai_player_insights(player_id):
    """
    Get comprehensive AI insights for a player using Claude.

    Returns:
        Deep analysis including:
        - Performance trends
        - Strengths/weaknesses
        - Matchup advantages
        - Season outlook
        - Trade value
    """
    try:
        insights = api_client.ai_player_insights_v2(player_id)

        if not insights:
            return jsonify({'error': 'Player insights not available'}), 404

        return jsonify({
            'data': insights,
            'meta': {
                'player_id': player_id,
                'provider': 'Claude (API v2)'
            }
        })

    except Exception as e:
        logger.error(f"AI player insights failed for {player_id}: {e}")
        return jsonify({'error': str(e)}), 500


@bp.route('/standings', methods=['GET'])
def get_standings():
    """
    Get current NFL standings.

    Query params:
        - season (int): Season year (default: 2024)
        - division (str): Filter by division (optional)

    Returns:
        Standings with playoff positioning and tiebreakers
    """
    try:
        season = request.args.get('season', 2025, type=int)
        division = request.args.get('division')

        standings = api_client.get_standings_v2(season=season, division=division)

        if not standings:
            return jsonify({'error': 'Standings not found'}), 404

        return jsonify({
            'data': standings,
            'meta': {
                'season': season,
                'division': division
            }
        })

    except Exception as e:
        logger.error(f"Failed to fetch standings: {e}")
        return jsonify({'error': str(e)}), 500


@bp.route('/teams', methods=['GET'])
def list_teams():
    """
    Get all 32 NFL teams (API v2).

    Returns:
        Complete list of NFL teams with details:
        - Team names and abbreviations
        - Locations and stadiums
        - Conference and division
        - Colors and logos
    """
    try:
        teams = api_client.get_teams_list_v2()

        return jsonify({
            'data': teams,
            'meta': {
                'count': len(teams)
            }
        })

    except Exception as e:
        logger.error(f"Failed to list teams: {e}")
        return jsonify({'error': str(e)}), 500


@bp.route('/teams/<team_id>', methods=['GET'])
def get_team_details(team_id):
    """
    Get detailed team information (API v2).

    Returns:
        Complete team profile:
        - Stadium and capacity
        - Conference and division
        - Team colors
        - Historical data
        - Current season record
    """
    try:
        team = api_client.get_team_by_id_v2(team_id)

        if not team:
            return jsonify({'error': 'Team not found'}), 404

        return jsonify({
            'data': team,
            'meta': {
                'team_id': team_id
            }
        })

    except Exception as e:
        logger.error(f"Failed to fetch team details for {team_id}: {e}")
        return jsonify({'error': str(e)}), 500


@bp.route('/teams/<team_id>/schedule', methods=['GET'])
def get_team_schedule(team_id):
    """
    Get detailed team schedule with game results (API v2).

    Query params:
        - season (int): Season year (default: 2024)

    Returns:
        Complete schedule with:
        - Game dates and opponents
        - Results (if played)
        - Home/away status
        - Venue information
    """
    try:
        season = request.args.get('season', 2025, type=int)

        schedule = api_client.get_team_schedule_detailed_v2(team_id, season=season)

        return jsonify({
            'data': schedule,
            'meta': {
                'team_id': team_id,
                'season': season,
                'games': len(schedule) if schedule else 0
            }
        })

    except Exception as e:
        logger.error(f"Failed to fetch team schedule for {team_id}: {e}")
        return jsonify({'error': str(e)}), 500


@bp.route('/games/<game_id>/stats', methods=['GET'])
def get_game_stats(game_id):
    """
    Get team statistics for a specific game (API v2).

    Returns:
        Team-level statistics:
        - Total yards (passing/rushing)
        - First downs
        - Time of possession
        - Turnovers
        - Third down efficiency
        - Red zone performance
    """
    try:
        stats = api_client.get_game_team_stats_v2(game_id)

        if not stats:
            return jsonify({'error': 'Game stats not found'}), 404

        return jsonify({
            'data': stats,
            'meta': {
                'game_id': game_id
            }
        })

    except Exception as e:
        logger.error(f"Failed to fetch game stats for {game_id}: {e}")
        return jsonify({'error': str(e)}), 500


@bp.route('/games', methods=['GET'])
def list_games():
    """
    List games with filtering (API v2).

    Query params:
        - season (int): Season year (required)
        - week (int): Week number (optional)
        - team (str): Filter by team abbreviation (optional)
        - status (str): Filter by status (scheduled, live, final) (optional)
        - limit (int): Results per page (default: 20)

    Returns:
        List of games matching filters
    """
    try:
        season = request.args.get('season', 2025, type=int)
        week = request.args.get('week', type=int)
        team = request.args.get('team')
        status = request.args.get('status')
        limit = request.args.get('limit', 20, type=int)

        games = api_client.get_games_v2(
            season=season,
            week=week,
            team=team,
            limit=limit
        )

        return jsonify({
            'data': games,
            'meta': {
                'season': season,
                'week': week,
                'team': team,
                'status': status,
                'limit': limit,
                'count': len(games) if games else 0
            }
        })

    except Exception as e:
        logger.error(f"Failed to list games: {e}")
        return jsonify({'error': str(e)}), 500


@bp.route('/games/<game_id>', methods=['GET'])
def get_game_details(game_id):
    """
    Get detailed game information (API v2).

    Returns:
        Complete game details:
        - Teams and scores
        - Date and venue
        - Weather conditions
        - Game status
        - Broadcast info
    """
    try:
        game = api_client.get_game_by_id_v2(game_id)

        if not game:
            return jsonify({'error': 'Game not found'}), 404

        return jsonify({
            'data': game,
            'meta': {
                'game_id': game_id
            }
        })

    except Exception as e:
        logger.error(f"Failed to fetch game details for {game_id}: {e}")
        return jsonify({'error': str(e)}), 500
