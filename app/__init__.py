"""
حزمة تطبيق نظام تقييم BTEC
"""

import os
import logging
from flask import Flask
from flask_cors import CORS

logger = logging.getLogger(__name__)

def create_app():
    """
    إنشاء وتهيئة تطبيق Flask
    
    Returns:
        Flask: تطبيق Flask مهيأ
    """
    # إنشاء تطبيق Flask
    app = Flask(
        __name__,
        template_folder='templates',
        static_folder='static'
    )
    
    # إعداد الإعدادات من متغيرات البيئة
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'btec_secure_key_placeholder')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        'pool_recycle': 300,
        'pool_pre_ping': True,
    }
    
    # إعداد CORS للسماح بطلبات واجهة المستخدم
    CORS(app)
    
    # تهيئة قاعدة البيانات
    from flask_sqlalchemy import SQLAlchemy
    db = SQLAlchemy(app)
    
    from app.database import init_app
    init_app(app)
    
    # تسجيل النماذج
    from app.models.user import User
    from app.models.rubric import Rubric
    from app.models.evaluation import Evaluation
    
    with app.app_context():
        db.create_all()
    
    # تسجيل المسارات (Blueprints)
    from app.routes import register_blueprints
    register_blueprints(app)
    
    # إعداد معالجات الأخطاء
    @app.errorhandler(404)
    def page_not_found(e):
        """معالجة خطأ 404 - الصفحة غير موجودة"""
        from flask import render_template
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(500)
    def server_error(e):
        """معالجة خطأ 500 - خطأ في الخادم"""
        from flask import render_template
        logger.error(f"حدث خطأ في الخادم: {str(e)}")
        return render_template('errors/500.html'), 500
    
    # إرجاع التطبيق المهيأ
    return app