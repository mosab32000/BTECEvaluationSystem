"""
حزمة مسارات نظام تقييم BTEC
"""

import logging
from flask import Blueprint

logger = logging.getLogger(__name__)

# إنشاء Blueprints للمسارات المختلفة
main_bp = Blueprint('main', __name__)
auth_bp = Blueprint('auth', __name__, url_prefix='/auth')
evaluation_bp = Blueprint('evaluation', __name__, url_prefix='/evaluation')
admin_bp = Blueprint('admin', __name__, url_prefix='/admin')
api_bp = Blueprint('api', __name__, url_prefix='/api')

def register_blueprints(app):
    """
    تسجيل جميع Blueprints في تطبيق Flask
    
    Args:
        app (Flask): تطبيق Flask
    """
    # استيراد مسارات المستويات المختلفة
    from app.routes import main
    from app.routes import auth
    from app.routes import evaluation
    from app.routes import admin
    from app.routes import api
    from app.routes import classroom
    from app.routes import session
    
    # تسجيل Blueprints
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(evaluation_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(api_bp)
    
    logger.info("تم تسجيل مسارات التطبيق بنجاح")