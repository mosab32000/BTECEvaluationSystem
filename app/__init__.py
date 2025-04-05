"""
حزمة تطبيق نظام تقييم BTEC

هذا الملف يقوم بتهيئة التطبيق وتكوين الإعدادات الأساسية.
"""
import os
import logging
from logging.handlers import RotatingFileHandler

from flask import Flask, request, jsonify, g, render_template
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_login import LoginManager
from flask_talisman import Talisman
from flask_caching import Cache
from werkzeug.security import generate_password_hash
from dotenv import load_dotenv

from app.config import config, default_config
from app.database import close_db, init_db, check_database_connection

# تهيئة السجل
logger = logging.getLogger(__name__)

# إعداد الكائنات العالمية
login_manager = LoginManager()
jwt = JWTManager()
limiter = Limiter(key_func=get_remote_address)
talisman = Talisman()
cache = Cache()

def create_app(config_name=None):
    """
    إنشاء وتهيئة تطبيق Flask.
    
    Args:
        config_name (str): اسم الإعدادات
        
    Returns:
        Flask: تطبيق Flask المُهيأ
    """
    # إنشاء تطبيق Flask
    app = Flask(__name__)
    
    # تحديد الإعدادات
    if config_name is None:
        config_name = os.environ.get('FLASK_CONFIG', default_config)
    
    # تطبيق الإعدادات
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    
    # تسجيل دوال تنظيف الحالة
    app.teardown_appcontext(close_db)
    
    # تهيئة الإضافات
    login_manager.init_app(app)
    jwt.init_app(app)
    limiter.init_app(app)
    cache.init_app(app)
    
    # تهيئة Talisman (أمان HTTP)
    if app.config.get('TALISMAN_ENABLED', True):
        csp = app.config.get('TALISMAN_CONTENT_SECURITY_POLICY')
        talisman.init_app(
            app,
            force_https=app.config.get('TALISMAN_FORCE_HTTPS', False),
            content_security_policy=csp,
            content_security_policy_nonce_in=['script-src', 'style-src']
        )
    
    # تهيئة CORS
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    
    # إعداد مدير تسجيل الدخول
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'يرجى تسجيل الدخول للوصول إلى هذه الصفحة.'
    login_manager.login_message_category = 'info'
    
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
    
    # تسجيل البلوبرنت (Blueprints)
    from app.routes.auth import bp as auth_bp
    from app.routes.admin import bp as admin_bp
    from app.routes.evaluation import bp as evaluation_bp
    # from app.routes.api import bp as api_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(evaluation_bp)
    # app.register_blueprint(api_bp)
    
    # معالجات الأخطاء
    @app.errorhandler(404)
    def page_not_found(e):
        """معالج الخطأ 404 - الصفحة غير موجودة"""
        if request.path.startswith('/api/'):
            return jsonify({"error": "المورد غير موجود"}), 404
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(500)
    def internal_server_error(e):
        """معالج الخطأ 500 - خطأ في الخادم"""
        logger.error(f"خطأ في الخادم: {e}")
        if request.path.startswith('/api/'):
            return jsonify({"error": "حدث خطأ في الخادم"}), 500
        return render_template('errors/500.html'), 500
    
    # طرق التطبيق الرئيسية
    @app.route('/health')
    def health():
        """نقطة نهاية للتحقق من صحة النظام"""
        status = {
            'status': 'up',
            'services': {
                'database': check_database_connection(),
                'app': True
            }
        }
        
        # فحص حالة النظام
        if not status['services']['database']:
            status['status'] = 'degraded'
        
        # تحديد كود الاستجابة
        status_code = 200 if status['status'] == 'up' else 503
        
        return jsonify(status), status_code
    
    @app.route('/')
    def index():
        """الصفحة الرئيسية"""
        return render_template('index.html')
    
    # تهيئة قاعدة البيانات
    with app.app_context():
        try:
            init_db()
        except Exception as e:
            logger.error(f"خطأ في تهيئة قاعدة البيانات: {e}")
    
    return app