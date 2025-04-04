"""
وحدة المسارات الرئيسية لنظام تقييم BTEC
"""

def register_routes(app):
    """
    تسجيل جميع المسارات مع التطبيق
    """
    from app.routes.auth import auth_bp
    from app.routes.health import health_bp
    
    # تسجيل Blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(health_bp)