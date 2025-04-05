"""
حزمة تطبيق نظام تقييم BTEC

هذا الملف يقوم بتهيئة التطبيق وتكوين الإعدادات الأساسية.
"""
import os
import logging
from logging.handlers import RotatingFileHandler
from flask import Flask, render_template, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask_talisman import Talisman
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_caching import Cache

# إعداد التسجيل
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# تهيئة أشياء الملحقات
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
jwt = JWTManager()
cors = CORS()
talisman = Talisman()
limiter = Limiter(key_func=get_remote_address)
cache = Cache()

def create_app(config_object='app.config'):
    """
    إنشاء وتهيئة تطبيق Flask.
    
    Args:
        config_object: كائن الإعدادات
        
    Returns:
        Flask: تطبيق Flask المُهيأ
    """
    # إنشاء تطبيق Flask
    app = Flask(__name__, 
                template_folder='templates',
                static_folder='static')
    
    # تحميل الإعدادات
    app.config.from_object(config_object)
    
    # إعداد التسجيل للملف
    if not os.path.exists('logs'):
        os.mkdir('logs')
    
    file_handler = RotatingFileHandler('logs/btec_eval.log', maxBytes=10240, backupCount=10)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    file_handler.setLevel(logging.INFO)
    
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)
    app.logger.info('نظام تقييم BTEC بدأ التشغيل')
    
    # تهيئة الملحقات
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    jwt.init_app(app)
    cors.init_app(app)
    talisman.init_app(app, content_security_policy=None)
    limiter.init_app(app)
    cache.init_app(app)
    
    # إعداد login_manager
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'يرجى تسجيل الدخول للوصول إلى هذه الصفحة.'
    login_manager.login_message_category = 'info'
    
    # تسجيل المسارات
    from app.routes import auth, evaluation
    app.register_blueprint(auth.bp)
    app.register_blueprint(evaluation.bp)
    
    # تسجيل معالجات السياق
    from app.context_processors import global_template_vars
    app.context_processor(global_template_vars)
    
    # تسجيل معالجات الأخطاء
    @app.errorhandler(404)
    def page_not_found(e):
        """معالج الخطأ 404 - الصفحة غير موجودة"""
        return render_template('404.html'), 404
    
    @app.errorhandler(500)
    def internal_server_error(e):
        """معالج الخطأ 500 - خطأ في الخادم"""
        return render_template('500.html'), 500
    
    @app.route('/health')
    def health():
        """نقطة نهاية للتحقق من صحة النظام"""
        return jsonify({'status': 'up'})
    
    @app.route('/')
    def index():
        """الصفحة الرئيسية"""
        return render_template('index.html')
    
    return app