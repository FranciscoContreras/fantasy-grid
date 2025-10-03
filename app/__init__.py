from flask import Flask, send_from_directory, jsonify, request, g
from flask_cors import CORS
import os
import logging
from logging.handlers import RotatingFileHandler
import uuid

def create_app():
    app = Flask(__name__, static_folder='static', static_url_path='')
    CORS(app)
    
    # Request ID middleware for log tracing
    @app.before_request
    def add_request_id():
        """Add unique request ID to each request for log tracing"""
        g.request_id = request.headers.get('X-Request-ID', str(uuid.uuid4()))
    
    @app.after_request
    def add_request_id_header(response):
        """Add request ID to response headers"""
        if hasattr(g, 'request_id'):
            response.headers['X-Request-ID'] = g.request_id
        return response
    
    # Initialize database connection pool
    from app.database import init_connection_pool
    init_connection_pool(minconn=2, maxconn=10)

    # Configure logging
    log_level = logging.INFO if not app.debug else logging.DEBUG
    
    # Custom formatter with request ID
    class RequestFormatter(logging.Formatter):
        def format(self, record):
            record.request_id = getattr(g, 'request_id', 'N/A') if request else 'N/A'
            return super().format(record)
    
    if not app.debug:
        # Production logging with rotation
        handler = RotatingFileHandler('app.log', maxBytes=10000000, backupCount=5)
        handler.setLevel(log_level)
        formatter = RequestFormatter(
            '%(asctime)s [%(request_id)s] %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        )
        handler.setFormatter(formatter)
        app.logger.addHandler(handler)
        app.logger.setLevel(log_level)
        app.logger.info('Fantasy Grid startup')
    else:
        # Development logging to console
        console_handler = logging.StreamHandler()
        console_handler.setLevel(log_level)
        formatter = RequestFormatter(
            '%(asctime)s [%(request_id)s] %(levelname)s: %(message)s'
        )
        console_handler.setFormatter(formatter)
        app.logger.addHandler(console_handler)
        app.logger.setLevel(log_level)

    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-key')
    app.config['DATABASE_URL'] = os.getenv('DATABASE_URL')

    # Health check endpoint
    @app.route('/health')
    def health():
        """
        Comprehensive health check endpoint
        Returns service status, dependencies, and system info
        """
        import time
        from datetime import datetime
        
        start_time = time.time()
        health_status = {
            'status': 'healthy',
            'service': 'Fantasy Grid API',
            'version': '1.0.0',
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'checks': {}
        }
        
        # Check database connection
        try:
            from app.database import execute_query
            execute_query("SELECT 1")
            health_status['checks']['database'] = {'status': 'up', 'message': 'Connected'}
        except Exception as e:
            health_status['status'] = 'degraded'
            health_status['checks']['database'] = {'status': 'down', 'error': str(e)}
        
        # Check Redis cache
        try:
            from app.utils.cache import cache
            if hasattr(cache, 'redis_client') and cache.redis_client:
                cache.redis_client.ping()
                health_status['checks']['redis'] = {'status': 'up', 'message': 'Connected'}
            else:
                health_status['checks']['redis'] = {'status': 'disabled', 'message': 'Using in-memory cache'}
        except Exception as e:
            health_status['status'] = 'degraded'
            health_status['checks']['redis'] = {'status': 'down', 'error': str(e)}
        
        # Response time
        health_status['response_time_ms'] = round((time.time() - start_time) * 1000, 2)
        
        # Return 200 if healthy, 503 if any critical service is down
        status_code = 200 if health_status['status'] in ['healthy', 'degraded'] else 503
        
        return health_status, status_code

    # Cache stats endpoint
    @app.route('/api/cache/stats')
    def cache_stats():
        from app.utils.cache import get_cache_stats
        return jsonify(get_cache_stats())
    
    # Cache invalidation endpoints
    @app.route('/api/cache/invalidate/player/<player_id>', methods=['POST'])
    def invalidate_player(player_id):
        """Invalidate cache for a specific player"""
        from app.utils.cache import invalidate_player_cache
        try:
            invalidate_player_cache(player_id)
            return jsonify({'message': f'Cache invalidated for player {player_id}', 'success': True})
        except Exception as e:
            logger.error(f"Failed to invalidate player cache: {e}")
            return jsonify({'error': str(e), 'success': False}), 500
    
    @app.route('/api/cache/invalidate/matchup', methods=['POST'])
    def invalidate_matchup():
        """Invalidate matchup cache (supports query params: matchup_id, week, season)"""
        from app.utils.cache import invalidate_matchup_cache
        from flask import request
        
        try:
            matchup_id = request.args.get('matchup_id')
            week = request.args.get('week', type=int)
            season = request.args.get('season', type=int)
            
            invalidate_matchup_cache(matchup_id=matchup_id, week=week, season=season)
            return jsonify({'message': 'Matchup cache invalidated', 'success': True})
        except Exception as e:
            logger.error(f"Failed to invalidate matchup cache: {e}")
            return jsonify({'error': str(e), 'success': False}), 500
    
    @app.route('/api/cache/invalidate/analysis', methods=['POST'])
    def invalidate_analysis():
        """Invalidate analysis cache (supports query params: player_id, week, season)"""
        from app.utils.cache import invalidate_analysis_cache
        from flask import request
        
        try:
            player_id = request.args.get('player_id')
            week = request.args.get('week', type=int)
            season = request.args.get('season', type=int)
            
            invalidate_analysis_cache(player_id=player_id, week=week, season=season)
            return jsonify({'message': 'Analysis cache invalidated', 'success': True})
        except Exception as e:
            logger.error(f"Failed to invalidate analysis cache: {e}")
            return jsonify({'error': str(e), 'success': False}), 500
    
    @app.route('/api/cache/cleanup', methods=['POST'])
    def cleanup_cache():
        """Cleanup old cache entries from PostgreSQL"""
        from app.utils.cache import schedule_cache_cleanup
        from flask import request
        
        try:
            max_age_days = request.args.get('max_age_days', 7, type=int)
            schedule_cache_cleanup(max_age_days=max_age_days)
            return jsonify({'message': f'Cache cleanup completed (max age: {max_age_days} days)', 'success': True})
        except Exception as e:
            logger.error(f"Failed to cleanup cache: {e}")
            return jsonify({'error': str(e), 'success': False}), 500

    # Register cleanup handler for graceful shutdown
    import atexit
    from app.database import close_all_connections
    atexit.register(close_all_connections)
    
    # Initialize Flask-Bcrypt for password hashing
    from app.services.auth_service import bcrypt
    bcrypt.init_app(app)
    
    # Register blueprints
    from app.routes import players, analysis, predictions, rosters, matchups, auth, advanced_stats, trades
    app.register_blueprint(auth.bp)
    app.register_blueprint(players.bp)
    app.register_blueprint(analysis.bp)
    app.register_blueprint(predictions.bp)
    app.register_blueprint(rosters.bp)
    app.register_blueprint(matchups.bp)
    app.register_blueprint(advanced_stats.bp)  # API v2 advanced stats
    app.register_blueprint(trades.bp)  # Trade analyzer

    # Serve frontend static files
    @app.route('/', defaults={'path': ''})
    @app.route('/<path:path>')
    def serve(path):
        if path != "" and os.path.exists(os.path.join(app.static_folder, path)):
            return send_from_directory(app.static_folder, path)
        else:
            return send_from_directory(app.static_folder, 'index.html')

    return app
