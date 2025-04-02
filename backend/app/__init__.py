from flask import Flask, request
from flask_cors import CORS
from .config import config
from .database import db, migrate
from flask_limiter import Limiter
from flask_talisman import Talisman
import logging

def create_app(config_name='default'):
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    CORS(app, resources={r"/*": {"origins": app.config['ALLOWED_ORIGINS']}})
    Talisman(app) # Apply security headers

    # Rate limiting
    limiter = Limiter(
        app=app,
        key_func=lambda: request.remote_addr,
        default_limits=["200 per day", "50 per hour"]
    )
    
    # Health check endpoint with exemption from rate limiting
    @app.route('/health')
    @limiter.exempt
    def health():
        return "System operational", 200

    # Import and register blueprints
    from .routes import auth_bp, evaluation_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(evaluation_bp)

    # Initialize encryption vault on app startup to check for key
    try:
        from .security.encryption import Vault
        Vault(app.config['ENCRYPTION_KEY'])
    except ValueError as e:
        logging.critical(f"Application startup failed due to encryption key issue: {e}")
        # Potentially exit the application here if encryption is critical
        # import sys
        # sys.exit(1)

    return app