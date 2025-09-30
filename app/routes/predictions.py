from flask import Blueprint, jsonify, request
from app.services.api_client import FantasyAPIClient
from app.services.analyzer import PlayerAnalyzer
from app.services.ai_grader import AIGrader

bp = Blueprint('predictions', __name__, url_prefix='/api/predictions')

api_client = FantasyAPIClient()
analyzer = PlayerAnalyzer()
grader = AIGrader()


@bp.route('/player/<player_id>', methods=['POST'])
def predict_player_performance(player_id):
    """
    Predict a player's fantasy performance
    Request body:
        {
            "opponent": "team_id",
            "location": "city" (optional),
            "week": 1 (optional)
        }
    """
    data = request.json or {}
    opponent = data.get('opponent')
    location = data.get('location')
    week = data.get('week')

    if not opponent:
        return jsonify({'error': 'Opponent team ID is required'}), 400

    try:
        # Get player data
        player = api_client.get_player_data(player_id)

        # Get historical performance
        try:
            career_stats = api_client.get_player_career_stats(player_id)
            recent_stats = career_stats.get('data', [{}])[0] if career_stats.get('data') else {}
            avg_points = recent_stats.get('fantasy_points', 10)
        except:
            avg_points = 10

        # Get defense stats
        defense_stats = api_client.get_defense_stats(opponent)

        # Get weather if location provided
        weather = {}
        if location:
            try:
                weather = api_client.get_weather_data(location)
            except:
                pass

        # Calculate factors
        matchup_score = analyzer.calculate_matchup_score(player, defense_stats)

        player_position = player.get('data', {}).get('position', 'RB') if isinstance(player, dict) and 'data' in player else player.get('position', 'RB')
        weather_impact = analyzer.calculate_weather_impact(
            weather.get('data', {}) if weather else {},
            player_position
        )

        # AI prediction
        features = [avg_points, matchup_score, weather_impact, 75]
        ai_prediction = grader.grade_player(features)

        # Calculate prediction ranges
        predicted_points = ai_prediction['predicted_points']
        confidence = ai_prediction['confidence']

        # Confidence interval (wider range = lower confidence)
        range_modifier = 1 - (confidence / 100)
        point_range = {
            'low': max(0, round(predicted_points * (1 - range_modifier * 0.3), 1)),
            'mid': round(predicted_points, 1),
            'high': round(predicted_points * (1 + range_modifier * 0.3), 1)
        }

        return jsonify({
            'data': {
                'player': player.get('data', player) if isinstance(player, dict) and 'data' in player else player,
                'prediction': {
                    'projected_points': predicted_points,
                    'grade': ai_prediction['grade'],
                    'confidence': confidence,
                    'point_range': point_range
                },
                'factors': {
                    'matchup_score': matchup_score,
                    'weather_impact': weather_impact,
                    'average_points': avg_points
                },
                'week': week
            }
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/game/<game_id>', methods=['POST'])
def predict_game_outcome(game_id):
    """
    Predict game outcome and player performances
    """
    try:
        # This would integrate with the Grid Iron Mind AI endpoints
        # For now, return a placeholder
        return jsonify({
            'data': {
                'game_id': game_id,
                'message': 'Game prediction feature requires Grid Iron Mind AI API key',
                'note': 'Configure API_KEY environment variable and use /api/v1/ai/predict/game endpoint'
            }
        }), 501

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/weekly-lineup', methods=['POST'])
def predict_weekly_lineup():
    """
    Predict optimal weekly lineup from a roster
    Request body:
        {
            "roster": ["player_id1", "player_id2", ...],
            "opponents": {
                "player_id1": "opponent_team_id",
                "player_id2": "opponent_team_id"
            },
            "week": 1
        }
    """
    data = request.json or {}
    roster = data.get('roster', [])
    opponents = data.get('opponents', {})
    week = data.get('week')

    if not roster or len(roster) == 0:
        return jsonify({'error': 'Roster is required'}), 400

    try:
        predictions = []

        for player_id in roster:
            opponent = opponents.get(player_id)
            if not opponent:
                continue

            # Get player data
            try:
                player = api_client.get_player_data(player_id)
                defense_stats = api_client.get_defense_stats(opponent)

                # Quick prediction
                matchup_score = analyzer.calculate_matchup_score(player, defense_stats)

                features = [12, matchup_score, 100, 75]  # Simplified
                ai_prediction = grader.grade_player(features)

                predictions.append({
                    'player_id': player_id,
                    'player': player.get('data', player) if isinstance(player, dict) and 'data' in player else player,
                    'projected_points': ai_prediction['predicted_points'],
                    'grade': ai_prediction['grade'],
                    'matchup_score': matchup_score,
                    'opponent': opponent
                })
            except:
                continue

        # Sort by projected points
        predictions.sort(key=lambda x: x['projected_points'], reverse=True)

        # Categorize by position
        lineup_by_position = {}
        for pred in predictions:
            position = pred['player'].get('position', 'FLEX')
            if position not in lineup_by_position:
                lineup_by_position[position] = []
            lineup_by_position[position].append(pred)

        return jsonify({
            'data': {
                'week': week,
                'predictions': predictions,
                'by_position': lineup_by_position,
                'top_performers': predictions[:5] if len(predictions) >= 5 else predictions
            }
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/trends/<player_id>', methods=['GET'])
def analyze_player_trends(player_id):
    """
    Analyze player performance trends
    """
    try:
        career_stats = api_client.get_player_career_stats(player_id)

        if not career_stats.get('data'):
            return jsonify({'error': 'No career statistics available'}), 404

        stats = career_stats['data']

        # Calculate trends
        trend_analysis = {
            'consistency': 'stable',  # Would calculate variance in real implementation
            'trajectory': 'improving',  # Would analyze season-over-season growth
            'recent_form': 'good'  # Would analyze last 4-6 games
        }

        return jsonify({
            'data': {
                'player_id': player_id,
                'seasons_analyzed': len(stats),
                'trends': trend_analysis,
                'career_stats': stats
            }
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500
