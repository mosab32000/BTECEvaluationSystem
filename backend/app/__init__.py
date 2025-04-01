from flask import Flask, request
from flask_cors import CORS
from .config import config
from .database import db, migrate
from .routes import auth_bp, evaluation_bp
from .security.encryption import Vault  # Import to trigger key check on app start
import logging
from flask_limiter import Limiter
from flask_talisman import Talisman

def create_app(config_name='default'):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    app.secret_key = app.config['SECRET_KEY']

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    CORS(app, resources={r"/*": {"origins": app.config['ALLOWED_ORIGINS']}})
    Talisman(app)  # Apply security headers

    # Rate limiting
    limiter = Limiter(
        key_func=lambda: request.remote_addr,
        app=app,
        default_limits=["200 per day", "50 per hour"]
    )

    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(evaluation_bp)

    # Health check endpoint
    @app.route('/health')
    @limiter.exempt
    def health():
        return "System operational", 200

    # Initialize encryption vault on app startup to check for key
    try:
        Vault(app.config['ENCRYPTION_KEY'])
    except ValueError as e:
        logging.critical(f"Application startup failed due to encryption key issue: {e}")
        # Potentially exit the application here if encryption is critical
        # import sys
        # sys.exit(1)

    return app
