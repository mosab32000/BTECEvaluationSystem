"""
وحدات واجهة برمجة التطبيقات لنظام تقييم BTEC
"""

from flask import Blueprint

def register_routes(app):
    """تسجيل جميع وحدات API مع تطبيق Flask"""
    from backend.app.routes.auth import auth_bp
    from backend.app.routes.evaluation import evaluation_bp
    from backend.app.routes.admin import admin_bp
    from backend.app.routes.sessions import sessions_bp
    from backend.app.routes.attendance import attendance_bp
    
    # تسجيل ال blueprints
    app.register_blueprint(auth_bp, url_prefix='/api')
    app.register_blueprint(evaluation_bp, url_prefix='/api')
    app.register_blueprint(admin_bp, url_prefix='/api/admin')
    app.register_blueprint(sessions_bp, url_prefix='/api')
    app.register_blueprint(attendance_bp, url_prefix='/api')
    
    # إضافة نقطة نهاية للتحقق من صحة النظام
    @app.route('/health')
    def health():
        """التحقق من صحة النظام"""
        return {'status': 'ok'}