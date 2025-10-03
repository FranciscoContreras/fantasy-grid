"""
Search API endpoints.
Provides full-text search, autocomplete, and index management.
"""
from flask import Blueprint, request, jsonify
from app.services.search import get_search_engine, get_indexer
from app.routes.auth import require_auth
from app.utils.cache import cached_route, invalidate_cache
import logging

logger = logging.getLogger(__name__)

bp = Blueprint('search', __name__, url_prefix='/api/search')


@bp.route('/query', methods=['GET'])
@cached_route(expiry=300, key_prefix='search')
def search():
    """
    Full-text search across players and teams.

    Query Parameters:
        q: Search query string (required)
        type: Document type filter ('player', 'team', or omit for all)
        position: Filter by position (QB, RB, WR, TE, K, DEF)
        team: Filter by team abbreviation
        limit: Max results to return (default: 50, max: 100)

    Returns:
        200: Search results with relevance scores
        400: Invalid query
        500: Server error
    """
    try:
        # Get query parameters
        query = request.args.get('q', '').strip()
        doc_type = request.args.get('type', '').strip()
        limit = min(int(request.args.get('limit', 50)), 100)

        if not query:
            return jsonify({'error': 'Query parameter "q" is required'}), 400

        # Build filters
        filters = {}
        if request.args.get('position'):
            filters['position'] = request.args.get('position').upper()
        if request.args.get('team'):
            filters['team'] = request.args.get('team').upper()

        # Execute search
        search_engine = get_search_engine()
        results = search_engine.search(
            query=query,
            doc_type=doc_type if doc_type in ['player', 'team'] else None,
            filters=filters if filters else None,
            limit=limit
        )

        return jsonify({
            'query': query,
            'count': len(results),
            'results': results
        })

    except ValueError as e:
        return jsonify({'error': f'Invalid parameter: {str(e)}'}), 400
    except Exception as e:
        logger.error(f"Search error: {e}", exc_info=True)
        return jsonify({'error': 'Search failed'}), 500


@bp.route('/autocomplete', methods=['GET'])
@cached_route(expiry=600, key_prefix='autocomplete')
def autocomplete():
    """
    Get autocomplete suggestions based on prefix.

    Query Parameters:
        q: Search prefix (minimum 2 characters)
        type: Document type filter ('player', 'team')
        limit: Max suggestions (default: 10, max: 20)

    Returns:
        200: Autocomplete suggestions
        400: Invalid query
        500: Server error
    """
    try:
        prefix = request.args.get('q', '').strip()
        doc_type = request.args.get('type', '').strip()
        limit = min(int(request.args.get('limit', 10)), 20)

        if not prefix or len(prefix) < 2:
            return jsonify({'error': 'Prefix must be at least 2 characters'}), 400

        # Get suggestions
        search_engine = get_search_engine()
        suggestions = search_engine.autocomplete(
            prefix=prefix,
            doc_type=doc_type if doc_type in ['player', 'team'] else None,
            limit=limit
        )

        return jsonify({
            'prefix': prefix,
            'count': len(suggestions),
            'suggestions': suggestions
        })

    except Exception as e:
        logger.error(f"Autocomplete error: {e}", exc_info=True)
        return jsonify({'error': 'Autocomplete failed'}), 500


@bp.route('/stats', methods=['GET'])
def get_stats():
    """
    Get search index statistics.

    Returns:
        200: Index statistics
        500: Server error
    """
    try:
        search_engine = get_search_engine()
        stats = search_engine.get_index_stats()

        return jsonify({
            'stats': stats
        })

    except Exception as e:
        logger.error(f"Error getting stats: {e}", exc_info=True)
        return jsonify({'error': 'Failed to get stats'}), 500


@bp.route('/popular', methods=['GET'])
def get_popular_searches():
    """
    Get most popular search queries.

    Query Parameters:
        limit: Number of results (default: 10, max: 50)

    Returns:
        200: Popular search queries
        500: Server error
    """
    try:
        limit = min(int(request.args.get('limit', 10)), 50)

        search_engine = get_search_engine()
        popular = search_engine.get_popular_searches(limit=limit)

        return jsonify({
            'count': len(popular),
            'queries': popular
        })

    except Exception as e:
        logger.error(f"Error getting popular searches: {e}", exc_info=True)
        return jsonify({'error': 'Failed to get popular searches'}), 500


@bp.route('/index/rebuild', methods=['POST'])
@require_auth
def rebuild_index(current_user):
    """
    Rebuild the search index (requires authentication).

    Request body (optional):
        {
            "type": "player|team"  // Optional: rebuild only specific type
        }

    Returns:
        200: Rebuild statistics
        401: Unauthorized
        500: Server error
    """
    try:
        data = request.get_json() or {}
        doc_type = data.get('type')

        if doc_type and doc_type not in ['player', 'team']:
            return jsonify({'error': 'Invalid type. Must be "player" or "team"'}), 400

        # Rebuild index
        indexer = get_indexer()
        stats = indexer.rebuild_index(doc_type=doc_type)

        # Invalidate search cache
        invalidate_cache('search:*')
        invalidate_cache('autocomplete:*')

        logger.info(f"Index rebuilt by user {current_user['id']}: {stats}")

        return jsonify({
            'message': 'Index rebuild complete',
            'stats': stats
        })

    except Exception as e:
        logger.error(f"Error rebuilding index: {e}", exc_info=True)
        return jsonify({'error': 'Failed to rebuild index'}), 500


@bp.route('/index/update/player/<player_id>', methods=['POST'])
@require_auth
def update_player_index(current_user, player_id):
    """
    Update the index for a specific player (requires authentication).

    Returns:
        200: Update successful
        401: Unauthorized
        404: Player not found
        500: Server error
    """
    try:
        indexer = get_indexer()
        success = indexer.update_player_index(player_id)

        if not success:
            return jsonify({'error': 'Failed to update player index'}), 404

        # Invalidate search cache
        invalidate_cache(f'search:*player*{player_id}*')

        return jsonify({
            'message': 'Player index updated',
            'player_id': player_id
        })

    except Exception as e:
        logger.error(f"Error updating player index: {e}", exc_info=True)
        return jsonify({'error': 'Failed to update player index'}), 500


@bp.route('/index/clear', methods=['POST'])
@require_auth
def clear_index(current_user):
    """
    Clear the entire search index (requires authentication).

    Request body (optional):
        {
            "type": "player|team"  // Optional: clear only specific type
        }

    Returns:
        200: Clear successful
        401: Unauthorized
        500: Server error
    """
    try:
        data = request.get_json() or {}
        doc_type = data.get('type')

        if doc_type and doc_type not in ['player', 'team']:
            return jsonify({'error': 'Invalid type. Must be "player" or "team"'}), 400

        search_engine = get_search_engine()
        success = search_engine.clear_index(doc_type=doc_type)

        if not success:
            return jsonify({'error': 'Failed to clear index'}), 500

        # Invalidate search cache
        invalidate_cache('search:*')
        invalidate_cache('autocomplete:*')

        logger.warning(f"Index cleared by user {current_user['id']}")

        return jsonify({
            'message': 'Index cleared successfully'
        })

    except Exception as e:
        logger.error(f"Error clearing index: {e}", exc_info=True)
        return jsonify({'error': 'Failed to clear index'}), 500
