"""
Task management and status endpoints
"""
from flask import Blueprint, jsonify, request
from app.tasks import celery_app
from app.tasks.analysis_tasks import analyze_player_matchup, compare_players_task

bp = Blueprint('tasks', __name__, url_prefix='/api/tasks')


@bp.route('/status/<task_id>', methods=['GET'])
def get_task_status(task_id):
    """
    Get the status of a background task

    Args:
        task_id: The Celery task ID

    Returns:
        JSON with task status, result, or error
    """
    task = celery_app.AsyncResult(task_id)

    response = {
        'task_id': task_id,
        'status': task.state,
        'ready': task.ready(),
        'successful': task.successful() if task.ready() else None,
    }

    if task.ready():
        if task.successful():
            response['result'] = task.result
        else:
            response['error'] = str(task.info)

    return jsonify(response)


@bp.route('/analyze-player', methods=['POST'])
def queue_player_analysis():
    """
    Queue a player analysis task

    Request body:
        {
            "player_id": "12345",
            "opponent_id": "SF",
            "location": "Santa Clara, CA"  // optional
        }

    Returns:
        JSON with task_id to check status
    """
    data = request.json
    player_id = data.get('player_id')
    opponent_id = data.get('opponent_id')
    location = data.get('location')

    if not player_id or not opponent_id:
        return jsonify({'error': 'player_id and opponent_id are required'}), 400

    # Queue the task
    task = analyze_player_matchup.delay(player_id, opponent_id, location)

    return jsonify({
        'task_id': task.id,
        'status': 'queued',
        'message': 'Analysis task queued successfully'
    }), 202


@bp.route('/compare-players', methods=['POST'])
def queue_player_comparison():
    """
    Queue a player comparison task

    Request body:
        {
            "player_ids": ["123", "456", "789"],
            "opponent_ids": ["SF", "LAR", "SEA"]  // optional
        }

    Returns:
        JSON with task_id to check status
    """
    data = request.json
    player_ids = data.get('player_ids', [])
    opponent_ids = data.get('opponent_ids')

    if not player_ids or len(player_ids) < 2:
        return jsonify({'error': 'At least 2 player IDs required'}), 400

    # Queue the task
    task = compare_players_task.delay(player_ids, opponent_ids)

    return jsonify({
        'task_id': task.id,
        'status': 'queued',
        'message': 'Comparison task queued successfully'
    }), 202
