from flask import Flask
from flask_cors import CORS
from flask_wtf.csrf import CSRFProtect
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import os

def create_app():
    app = Flask(__name__)

    # Security configuration
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-key-change-in-production')
    app.config['DATABASE_URL'] = os.getenv('DATABASE_URL')

    # CSRF Protection - only for POST/PUT/DELETE/PATCH
    app.config['WTF_CSRF_ENABLED'] = os.getenv('CSRF_ENABLED', 'True') == 'True'
    app.config['WTF_CSRF_TIME_LIMIT'] = None  # No timeout for CSRF tokens
    app.config['WTF_CSRF_METHODS'] = ['POST', 'PUT', 'PATCH', 'DELETE']  # Exempt GET/HEAD/OPTIONS
    csrf = CSRFProtect(app)

    # CORS Configuration - more restrictive in production
    CORS(app,
         origins=os.getenv('CORS_ORIGINS', 'http://localhost:5173,http://localhost:3000').split(','),
         supports_credentials=True,
         allow_headers=['Content-Type', 'Authorization', 'X-CSRF-Token'])

    # Rate Limiting
    limiter = Limiter(
        app=app,
        key_func=get_remote_address,
        default_limits=["200 per day", "50 per hour"],
        storage_uri=os.getenv('REDIS_URL', 'memory://'),
        strategy="fixed-window"
    )

    # Health check endpoint (no rate limit, no CSRF)
    @app.route('/health')
    @csrf.exempt
    @limiter.exempt
    def health():
        return {'status': 'healthy', 'service': 'Fantasy Grid API', 'version': '1.1.0'}

    # Register blueprints
    from app.routes import players, analysis, predictions, security, tasks, billing
    app.register_blueprint(players.bp)
    app.register_blueprint(analysis.bp)
    app.register_blueprint(predictions.bp)
    app.register_blueprint(security.bp)
    app.register_blueprint(tasks.bp)
    app.register_blueprint(billing.bp)

    # Exempt Stripe webhook from CSRF (Stripe signs requests)
    csrf.exempt(billing.bp)

    return app

# Create app instance for gunicorn
app = create_app()
