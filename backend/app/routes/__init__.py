"""
وحدات واجهة برمجة التطبيقات لنظام تقييم BTEC
"""

from flask import Blueprint

# تعريف البلوبرنت
auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')
evaluation_bp = Blueprint('evaluation', __name__, url_prefix='/api/evaluation')
admin_bp = Blueprint('admin', __name__, url_prefix='/api/admin')
sessions_bp = Blueprint('sessions', __name__, url_prefix='/api/sessions')
attendance_bp = Blueprint('attendance', __name__, url_prefix='/api/attendance')

# استيراد وحدات المسارات لتسجيل المسارات على البلوبرنت
from . import auth, evaluation, admin, sessions, attendance

def register_routes(app):
    """تسجيل جميع وحدات API مع تطبيق Flask"""
    
    # تسجيل البلوبرنت
    app.register_blueprint(auth_bp)
    app.register_blueprint(evaluation_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(sessions_bp)
    app.register_blueprint(attendance_bp)
    
    # إضافة نقطة نهاية للتحقق من صحة النظام
    @app.route('/health')
    def health():
        """التحقق من صحة النظام"""
        return {'status': 'ok'}