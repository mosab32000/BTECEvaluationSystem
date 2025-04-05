"""
نظام تقييم BTEC - Bilād alShām Technical Education College
"""

import os
import logging
from logging.handlers import RotatingFileHandler
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from flask_cors import CORS
from flask_talisman import Talisman

# إنشاء مثيلات ملحقات التطبيق
db = SQLAlchemy()
login_manager = LoginManager()
csrf = CSRFProtect()
cors = CORS()
talisman = Talisman()

def create_app(config_name=None):
    """
    إنشاء تطبيق Flask
    
    Args:
        config_name (str, optional): اسم التكوين. افتراضيًا None.
    
    Returns:
        Flask: تطبيق Flask
    """
    # إنشاء تطبيق Flask
    app = Flask(__name__)
    
    # تعيين التكوين
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')
    
    # تطبيق إعدادات التكوين
    if config_name == 'production':
        app.config.from_object('app.config.ProductionConfig')
    elif config_name == 'testing':
        app.config.from_object('app.config.TestingConfig')
    else:
        app.config.from_object('app.config.DevelopmentConfig')
    
    # التأكد من وجود مجلدات التطبيق
    _ensure_app_folders(app)
    
    # تهيئة التسجيل
    _init_logging(app)
    
    # تهيئة ملحقات التطبيق
    _init_extensions(app)
    
    # تهيئة إدارة المستخدمين
    _init_user_management(app)
    
    # تسجيل مخططات المسارات
    from app.routes import register_blueprints
    register_blueprints(app)
    
    # تهيئة معالجات الأخطاء
    _init_error_handlers(app)
    
    # تهيئة وحدة التشفير
    _init_encryption(app)
    
    # جعل متغيرات معينة متاحة لجميع قوالب Jinja
    @app.context_processor
    def inject_globals():
        """
        حقن متغيرات عامة في جميع قوالب Jinja
        
        Returns:
            dict: قاموس المتغيرات العامة
        """
        from datetime import datetime
        return dict(now=datetime.utcnow())
    
    return app

def _ensure_app_folders(app):
    """
    التأكد من وجود مجلدات التطبيق
    
    Args:
        app (Flask): تطبيق Flask
    """
    for folder in ['logs', 'data', 'uploads']:
        os.makedirs(os.path.join(app.root_path, folder), exist_ok=True)

def _init_logging(app):
    """
    تهيئة التسجيل
    
    Args:
        app (Flask): تطبيق Flask
    """
    log_level = getattr(logging, os.environ.get('LOG_LEVEL', 'INFO').upper())
    log_file = os.environ.get('LOG_FILE', 'app.log')
    
    # إعداد مكتبة التسجيل
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # إعداد مقبض تدوير الملفات
    file_handler = RotatingFileHandler(
        log_file, maxBytes=1024 * 1024 * 10, backupCount=3
    )
    file_handler.setFormatter(formatter)
    file_handler.setLevel(log_level)
    
    # إضافة مقبض لتسجيل المخرجات إلى وحدة التحكم أيضًا
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(log_level)
    
    # تعيين مستوى التسجيل العام والمقابض
    app.logger.setLevel(log_level)
    app.logger.addHandler(file_handler)
    app.logger.addHandler(console_handler)
    
    # إزالة المقبض الافتراضي من Flask
    app.logger.removeHandler(logging.default_handler) if hasattr(logging, 'default_handler') else None

def _init_extensions(app):
    """
    تهيئة ملحقات التطبيق
    
    Args:
        app (Flask): تطبيق Flask
    """
    # تهيئة SQLAlchemy
    db.init_app(app)
    
    # تهيئة Flask-Login
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'يرجى تسجيل الدخول للوصول إلى هذه الصفحة.'
    login_manager.login_message_category = 'info'
    
    # تهيئة CSRF Protection
    csrf.init_app(app)
    
    # تهيئة CORS
    cors.init_app(app, resources={r"/api/*": {"origins": app.config.get('CORS_ORIGINS', '*')}})
    
    # تهيئة Talisman (HTTP Security)
    talisman.init_app(app, content_security_policy=app.config.get('CONTENT_SECURITY_POLICY', None))

def _init_user_management(app):
    """
    تهيئة إدارة المستخدمين
    
    Args:
        app (Flask): تطبيق Flask
    """
    from app.models.user import User
    
    @login_manager.user_loader
    def load_user(user_id):
        """
        تحميل المستخدم حسب المعرف
        
        Args:
            user_id (str): معرف المستخدم
        
        Returns:
            User: كائن المستخدم
        """
        return User.query.get(int(user_id))

def _init_error_handlers(app):
    """
    تهيئة معالجات الأخطاء
    
    Args:
        app (Flask): تطبيق Flask
    """
    @app.errorhandler(404)
    def page_not_found(error):
        """معالجة خطأ 404 - الصفحة غير موجودة"""
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(500)
    def server_error(error):
        """معالجة خطأ 500 - خطأ في الخادم"""
        app.logger.error(f'خطأ في الخادم: {error}')
        return render_template('errors/500.html'), 500
    
    @app.errorhandler(403)
    def forbidden(error):
        """معالجة خطأ 403 - غير مصرح به"""
        return render_template('errors/403.html'), 403
    
    @app.errorhandler(401)
    def unauthorized(error):
        """معالجة خطأ 401 - غير مصادق عليه"""
        return render_template('errors/401.html'), 401
    
    @app.errorhandler(429)
    def handle_rate_limit_exceeded(error):
        """معالجة خطأ تجاوز حد معدل الطلبات"""
        return render_template('errors/429.html'), 429

def _init_encryption(app):
    """
    تهيئة وحدة التشفير
    
    Args:
        app (Flask): تطبيق Flask
    """
    # التأكد من وجود مفتاح التشفير البيئي
    if 'ENCRYPTION_KEY' not in os.environ:
        app.logger.warning('ENCRYPTION_KEY غير محدد. سيتم استخدام مفتاح عشوائي لهذه الجلسة.')
        import secrets
        os.environ['ENCRYPTION_KEY'] = secrets.token_hex(16)
