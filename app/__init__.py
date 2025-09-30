from flask import Flask, send_from_directory, jsonify
from flask_cors import CORS
import os
import logging
from logging.handlers import RotatingFileHandler

def create_app():
    app = Flask(__name__, static_folder='static', static_url_path='')
    CORS(app)

    # Configure logging
    if not app.debug:
        # Production logging
        handler = RotatingFileHandler('app.log', maxBytes=10000, backupCount=3)
        handler.setLevel(logging.INFO)
        formatter = logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        )
        handler.setFormatter(formatter)
        app.logger.addHandler(handler)
        app.logger.setLevel(logging.INFO)
        app.logger.info('Fantasy Grid startup')

    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-key')
    app.config['DATABASE_URL'] = os.getenv('DATABASE_URL')

    # Health check endpoint
    @app.route('/health')
    def health():
        return {'status': 'healthy', 'service': 'Fantasy Grid API', 'version': '1.0.0'}

    # Cache stats endpoint
    @app.route('/api/cache/stats')
    def cache_stats():
        from app.utils.cache import get_cache_stats
        return jsonify(get_cache_stats())

    # Register blueprints
    from app.routes import players, analysis, predictions
    app.register_blueprint(players.bp)
    app.register_blueprint(analysis.bp)
    app.register_blueprint(predictions.bp)

    # Serve frontend static files
    @app.route('/', defaults={'path': ''})
    @app.route('/<path:path>')
    def serve(path):
        if path != "" and os.path.exists(os.path.join(app.static_folder, path)):
            return send_from_directory(app.static_folder, path)
        else:
            return send_from_directory(app.static_folder, 'index.html')

    return app
