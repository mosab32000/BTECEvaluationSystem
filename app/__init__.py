"""
حزمة تطبيق نظام تقييم BTEC

هذا الملف يقوم بتهيئة التطبيق وتكوين الإعدادات الأساسية.
"""
import os
import logging
from logging.handlers import RotatingFileHandler
import json

from flask import Flask, request, g, jsonify, render_template
from flask import redirect, url_for, session, flash
from flask_jwt_extended import JWTManager
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_login import LoginManager, current_user
from flask_talisman import Talisman
from flask_caching import Cache
from werkzeug.security import generate_password_hash
from dotenv import load_dotenv

from app.database import init_db, close_db, check_database_connection

# تهيئة السجل
logger = logging.getLogger(__name__)

def create_app(config_name=None):
    """
    إنشاء وتهيئة تطبيق Flask.
    
    Args:
        config_name (str): اسم الإعدادات
        
    Returns:
        Flask: تطبيق Flask المُهيأ
    """
    # تحميل متغيرات البيئة
    load_dotenv()
    
    # إنشاء تطبيق Flask
    app = Flask(__name__)
    
    # تحديد الإعدادات
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')
    
    # تحميل الإعدادات
    if config_name == 'production':
        app.config.from_object('app.config.ProductionConfig')
    elif config_name == 'testing':
        app.config.from_object('app.config.TestingConfig')
    else:
        app.config.from_object('app.config.DevelopmentConfig')
    
    # تهيئة تطبيق الإعدادات
    config_class = app.config.pop('CONFIG_CLASS', None)
    if config_class:
        config_class.init_app(app)
    
    # تهيئة السجل
    setup_logging(app)
    
    # تهيئة معايير أمان الويب
    if app.config.get('TALISMAN_ENABLED', True):
        talisman = Talisman(
            app,
            force_https=app.config.get('TALISMAN_FORCE_HTTPS', False),
            strict_transport_security=app.config.get('TALISMAN_STRICT_TRANSPORT_SECURITY', True),
            content_security_policy=app.config.get('TALISMAN_CONTENT_SECURITY_POLICY', None)
        )
    
    # تهيئة JWT
    jwt = JWTManager(app)
    
    # تهيئة LoginManager
    login_manager = LoginManager(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'يرجى تسجيل الدخول للوصول إلى هذه الصفحة'
    login_manager.login_message_category = 'info'
    
    # دالة تحميل المستخدم
    @login_manager.user_loader
    def load_user(user_id):
        """
        دالة لتحميل المستخدم للمصادقة
        
        Args:
            user_id: معرف المستخدم
            
        Returns:
            User: كائن المستخدم
        """
        from app.models.user import User
        return User.get_by_id(user_id)
    
    # تهيئة محدد معدل الطلبات
    limiter = Limiter(
        app=app,
        key_func=get_remote_address,
        default_limits=app.config.get('RATELIMIT_DEFAULT', ["300/hour"]),
        storage_uri=app.config.get('RATELIMIT_STORAGE_URL', "memory://"),
        enabled=app.config.get('RATELIMIT_ENABLED', True)
    )
    
    # تهيئة التخزين المؤقت
    cache = Cache(app)
    
    # تسجيل دالة إغلاق قاعدة البيانات
    app.teardown_appcontext(close_db)
    
    # تهيئة قاعدة البيانات
    with app.app_context():
        init_db()
    
    # تسجيل مسارات التطبيق
    from app.routes import auth, evaluation, admin
    app.register_blueprint(auth.bp)
    app.register_blueprint(evaluation.bp)
    app.register_blueprint(admin.bp)
    
    # معالجات الخطأ
    @app.errorhandler(404)
    def page_not_found(e):
        """معالج الخطأ 404 - الصفحة غير موجودة"""
        if request.is_json:
            return jsonify({"error": "الصفحة غير موجودة"}), 404
        
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(500)
    def internal_server_error(e):
        """معالج الخطأ 500 - خطأ في الخادم"""
        logger.error(f"خطأ في الخادم: {e}")
        
        if request.is_json:
            return jsonify({"error": "حدث خطأ في الخادم"}), 500
        
        return render_template('errors/500.html'), 500
    
    # تسجيل مسارات API
    @app.route('/api/health')
    def health():
        """نقطة نهاية للتحقق من صحة النظام"""
        return jsonify({
            "status": "up",
            "database": check_database_connection()
        })
    
    # تسجيل الصفحة الرئيسية
    @app.route('/')
    def index():
        """الصفحة الرئيسية"""
        return render_template('index.html')
    
    # تسجيل معالجات السياق
    @app.context_processor
    def utility_processor():
        """
        إضافة دوال ومتغيرات مفيدة للقوالب
        
        Returns:
            dict: قاموس الدوال والمتغيرات
        """
        return {
            'app_name': 'نظام تقييم BTEC',
            'current_year': 2025,
            'version': '1.0.0',
        }
    
    logger.info(f"تم تهيئة التطبيق بنجاح في بيئة: {config_name}")
    
    return app

def setup_logging(app):
    """
    إعداد نظام السجلات للتطبيق
    
    Args:
        app: تطبيق Flask
    """
    # تعيين مستوى السجل
    log_level = app.config.get('LOG_LEVEL', 'INFO')
    
    # إنشاء مجلد السجلات إذا لم يكن موجودًا
    log_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs')
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # تهيئة سجل الملف
    log_file = app.config.get('LOG_FILE', os.path.join(log_dir, 'app.log'))
    file_handler = RotatingFileHandler(log_file, maxBytes=10485760, backupCount=10)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    file_handler.setLevel(getattr(logging, log_level))
    
    # تهيئة سجل وحدة التحكم
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter('%(levelname)s: %(message)s'))
    console_handler.setLevel(getattr(logging, log_level))
    
    # إعداد السجل الرئيسي
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level))
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)
    
    # إضافة معالجات إلى سجل التطبيق
    app.logger.addHandler(file_handler)
    app.logger.addHandler(console_handler)
    app.logger.setLevel(getattr(logging, log_level))
    
    # تعيين مستوى سجل Werkzeug
    logging.getLogger('werkzeug').setLevel(getattr(logging, app.config.get('WERKZEUG_LOG_LEVEL', 'WARNING')))
    
    logger.info(f"تم إعداد السجلات بمستوى: {log_level}")