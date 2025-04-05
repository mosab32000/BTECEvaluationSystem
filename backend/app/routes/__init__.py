"""
وحدات واجهة برمجة التطبيقات لنظام تقييم BTEC
"""


from app.routes.health import health_bp

from flask import Blueprint

# تعريف البلوبرنت
auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')
evaluation_bp = Blueprint('evaluation', __name__, url_prefix='/api/evaluation')
admin_bp = Blueprint('admin', __name__, url_prefix='/api/admin')
sessions_bp = Blueprint('sessions', __name__, url_prefix='/api/sessions')
attendance_bp = Blueprint('attendance', __name__, url_prefix='/api/attendance')
# Note: health_bp is imported from app.routes.health

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
    app.register_blueprint(health_bp)
    
    # Note: health endpoint is registered elsewhere