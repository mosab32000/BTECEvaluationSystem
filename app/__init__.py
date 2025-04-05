"""
حزمة تطبيق نظام تقييم BTEC
"""

import os
import logging
from datetime import datetime
from flask import Flask, render_template
from dotenv import load_dotenv
from whitenoise import WhiteNoise

from app.extensions import (
    db, migrate, login_manager, 
    jwt, cors, limiter, talisman, cache
)

# تحميل متغيرات البيئة
load_dotenv()


def create_app(config_object='app.config'):
    """
    إنشاء وتهيئة تطبيق Flask
    
    Args:
        config_object (str): مسار ملف الإعدادات
    
    Returns:
        Flask: تطبيق Flask مهيأ
    """
    app = Flask(__name__)
    
    # تحميل الإعدادات من ملف التكوين
    app.config.from_object(config_object)
    
    # إعداد WhiteNoise لخدمة الملفات الثابتة
    app.wsgi_app = WhiteNoise(app.wsgi_app)
    app.wsgi_app.add_files(app.config.get('STATIC_FOLDER', 'static'))
    if os.path.exists(app.config.get('STATIC_ROOT', 'staticfiles')):
        app.wsgi_app.add_files(app.config.get('STATIC_ROOT', 'staticfiles'))
    
    # تهيئة الامتدادات
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    jwt.init_app(app)
    cors.init_app(app)
    limiter.init_app(app)
    cache.init_app(app)
    
    # تهيئة Talisman مع الإعدادات المناسبة
    csp = {
        'default-src': [
            '\'self\'', 
            '\'unsafe-inline\'',
            '*.googleapis.com',
            '*.gstatic.com',
            '*.fontawesome.com',
            'cdnjs.cloudflare.com'
        ],
        'img-src': ['\'self\'', 'data:', 'blob:'],
        'script-src': [
            '\'self\'', 
            '\'unsafe-inline\'', 
            '\'unsafe-eval\'',
            'cdnjs.cloudflare.com'
        ],
        'style-src': [
            '\'self\'', 
            '\'unsafe-inline\'',
            '*.googleapis.com',
            'cdnjs.cloudflare.com'
        ],
        'font-src': [
            '\'self\'',
            'fonts.gstatic.com',
            '*.fontawesome.com'
        ]
    }
    
    talisman.init_app(
        app,
        content_security_policy=csp,
        content_security_policy_nonce_in=['script-src', 'style-src'],
        force_https=False,  # تعطيل في بيئة التطوير
    )
    
    # تعيين المستخدم الحالي
    from app.models.user import User
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    # تسجيل المسارات
    from app.routes.main import main_blueprint
    app.register_blueprint(main_blueprint)
    
    from app.routes.auth import auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/auth')
    
    from app.routes.api import api_blueprint
    app.register_blueprint(api_blueprint, url_prefix='/api')
    
    from app.routes.dashboard import dashboard_blueprint
    app.register_blueprint(dashboard_blueprint, url_prefix='/dashboard')
    
    from app.routes.evaluations import evaluations_blueprint
    app.register_blueprint(evaluations_blueprint, url_prefix='/evaluations')
    
    from app.routes.rubrics import rubrics_blueprint
    app.register_blueprint(rubrics_blueprint, url_prefix='/rubrics')
    
    from app.routes.classes import classes_blueprint
    app.register_blueprint(classes_blueprint, url_prefix='/classes')
    
    from app.routes.admin import admin_blueprint
    app.register_blueprint(admin_blueprint, url_prefix='/admin')
    
    from app.routes.profile import profile_blueprint
    app.register_blueprint(profile_blueprint, url_prefix='/profile')
    
    # إضافة متغيرات سياق عامة
    @app.context_processor
    def inject_now():
        return {'now': datetime.utcnow()}
    
    # تسجيل معالجي الأخطاء
    @app.errorhandler(404)
    def page_not_found(e):
        """معالجة خطأ 404 - الصفحة غير موجودة"""
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(500)
    def server_error(e):
        """معالجة خطأ 500 - خطأ في الخادم"""
        return render_template('errors/500.html'), 500
    
    # إنشاء الجداول في قاعدة البيانات
    with app.app_context():
        db.create_all()
    
    return app