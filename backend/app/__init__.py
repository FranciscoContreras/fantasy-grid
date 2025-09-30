from flask import Flask
from flask_cors import CORS
import os

def create_app():
    app = Flask(__name__)
    CORS(app)

    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-key')
    app.config['DATABASE_URL'] = os.getenv('DATABASE_URL')

    # Health check endpoint
    @app.route('/health')
    def health():
        return {'status': 'healthy', 'service': 'Fantasy Grid API', 'version': '1.0.0'}

    # Register blueprints when routes are created
    # from app.routes import players, analysis, predictions
    # app.register_blueprint(players.bp)
    # app.register_blueprint(analysis.bp)
    # app.register_blueprint(predictions.bp)

    return app
