from flask import Flask, request, session, redirect, url_for
from flask_cors import CORS
from .config import config
from .database import db, migrate
from flask_limiter import Limiter
from flask_talisman import Talisman
import logging
import os

def create_app(config_name='default'):
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    CORS(app, resources={r"/*": {"origins": app.config['ALLOWED_ORIGINS']}})
    
    # Apply security headers but allow framing from same origin and enable frontend features
    talisman = Talisman(
        app,
        content_security_policy={
            'default-src': ['\'self\'', 'fonts.googleapis.com', 'fonts.gstatic.com'],
            'script-src': ['\'self\'', '\'unsafe-inline\''],
            'style-src': ['\'self\'', '\'unsafe-inline\'', 'fonts.googleapis.com'],
            'img-src': ['\'self\'', 'data:'],
        },
        force_https=False,  # ضبط على True في الإنتاج
        frame_options='SAMEORIGIN'
    )

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
    
    # Import API blueprints
    from .routes import auth_bp, evaluation_bp, admin_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(evaluation_bp)
    app.register_blueprint(admin_bp)
    
    # Import frontend blueprint
    # تأكد من أن مسار frontend مضاف إلى sys.path
    import sys
    frontend_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'frontend')
    if frontend_path not in sys.path:
        sys.path.insert(0, frontend_path)
    
    try:
        from frontend import frontend as frontend_bp
        app.register_blueprint(frontend_bp)
        
        # إعادة توجيه الصفحة الرئيسية إلى واجهة المستخدم
        @app.route('/')
        @limiter.exempt
        def home():
            return redirect(url_for('frontend.index'))
            
    except ImportError as e:
        logging.warning(f"Could not import frontend blueprint: {e}")
        
        # في حالة عدم وجود واجهة المستخدم، استخدم واجهة API الافتراضية
        @app.route('/')
        @limiter.exempt
        def home():
            return {
                "name": "BTEC Evaluation System API",
                "version": "1.0.0",
                "status": "running",
                "endpoints": [
                    "/health",
                    "/auth/register",
                    "/auth/login",
                    "/evaluation/*",
                    "/admin/*"
                ]
            }, 200

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