"""
ملف بداية تطبيق نظام تقييم BTEC
يقوم بإنشاء وتهيئة التطبيق
"""

import os
import logging
from flask import Flask, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask_migrate import Migrate
from datetime import timedelta
from logging.handlers import RotatingFileHandler

# تهيئة قاعدة البيانات
db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()

def create_app(config_name='default'):
    """
    إنشاء وتكوين تطبيق Flask
    """
    app = Flask(__name__, template_folder='../templates', static_folder='../static')
    
    # تحميل الإعدادات حسب بيئة التشغيل
    if config_name == 'production':
        app.config.from_object('app.config.ProductionConfig')
    else:
        app.config.from_object('app.config.DevelopmentConfig')
    
    # تكوين التسجيل
    configure_logging(app)
    
    # تهيئة المكونات الإضافية
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    CORS(app, resources={r"/api/*": {"origins": app.config['ALLOWED_ORIGINS']}})
    
    # تسجيل المسارات
    register_blueprints(app)
    
    # تسجيل معالجات الأخطاء
    register_error_handlers(app)
    
    @app.route('/health')
    def health():
        """
        فحص صحة النظام
        """
        return jsonify(status="ok", message="نظام تقييم BTEC يعمل بشكل جيد")
    
    @app.route('/home')
    def home():
        """
        الصفحة الرئيسية
        """
        return render_template('index.html')
    
    return app

def register_blueprints(app):
    """
    تسجيل جميع مسارات التطبيق
    """
    # مسارات API
    from app.routes.auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/api/auth')
    
    from app.routes.health import health as health_blueprint
    app.register_blueprint(health_blueprint, url_prefix='/api/health')
    
    from app.routes.evaluations import evaluations as evaluations_blueprint
    app.register_blueprint(evaluations_blueprint, url_prefix='/api/evaluations')
    
    from app.routes.user import user as user_blueprint
    app.register_blueprint(user_blueprint, url_prefix='/api/user')
    
    from app.routes.admin import admin as admin_blueprint
    app.register_blueprint(admin_blueprint, url_prefix='/api/admin')
    
    # مسارات الواجهة الأمامية
    from app.routes.frontend import frontend as frontend_blueprint
    app.register_blueprint(frontend_blueprint)

def register_error_handlers(app):
    """
    تسجيل معالجات الأخطاء
    """
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify(error="خطأ في الطلب", message=str(error)), 400
    
    @app.errorhandler(401)
    def unauthorized(error):
        return jsonify(error="غير مصرح", message="يجب تسجيل الدخول للوصول إلى هذا المورد"), 401
    
    @app.errorhandler(403)
    def forbidden(error):
        return jsonify(error="محظور", message="ليس لديك صلاحية للوصول إلى هذا المورد"), 403
    
    @app.errorhandler(404)
    def not_found(error):
        return jsonify(error="غير موجود", message="المورد المطلوب غير موجود"), 404
    
    @app.errorhandler(500)
    def internal_server_error(error):
        return jsonify(error="خطأ في الخادم", message="حدث خطأ داخلي في الخادم"), 500

def configure_logging(app):
    """
    تكوين التسجيل
    """
    if not app.debug:
        # إنشاء مجلد السجلات إذا لم يكن موجوداً
        if not os.path.exists('logs'):
            os.mkdir('logs')
        
        file_handler = RotatingFileHandler('logs/btec_evaluation.log', maxBytes=10240, backupCount=10)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        
        app.logger.setLevel(logging.INFO)
        app.logger.info('بدء تشغيل نظام تقييم BTEC')

def init_database():
    """
    تهيئة قاعدة البيانات وإنشاء الجداول الضرورية إذا لم تكن موجودة
    """
    with create_app().app_context():
        db.create_all()
