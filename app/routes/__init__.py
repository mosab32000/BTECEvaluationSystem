"""
تهيئة مسارات نظام تقييم BTEC
"""

from app.routes.main import main_bp
from app.routes.auth import auth_bp
from app.routes.api import api_bp
from app.routes.health import health_bp

def register_blueprints(app):
    """
    تسجيل مخططات المسارات في التطبيق
    
    Args:
        app: تطبيق Flask
    """
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(api_bp, url_prefix='/api')
    app.register_blueprint(health_bp)
