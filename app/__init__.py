"""
نظام تقييم BTEC - Bilād alShām Technical Education College
"""

import os
import logging
from datetime import datetime

from flask import Flask, render_template, request, jsonify

from app.extensions import (
    db, login_manager, jwt, limiter, cache, talisman, cors
)
from app.config import config

def create_app(config_name=None):
    """
    إنشاء تطبيق Flask
    
    Args:
        config_name (str, optional): اسم التكوين. افتراضيًا None.
    
    Returns:
        Flask: تطبيق Flask
    """
    if not config_name:
        config_name = os.environ.get('FLASK_ENV', 'development')
    
    # إنشاء التطبيق
    app = Flask(__name__)
    
    # تهيئة الإعدادات
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    
    # إنشاء مجلدات التطبيق إذا لم تكن موجودة
    _ensure_app_folders(app)
    
    # تهيئة التسجيل
    _init_logging(app)
    
    # تهيئة الملحقات
    _init_extensions(app)
    
    # تهيئة إدارة المستخدمين
    _init_user_management(app)
    
    # تسجيل المسارات
    _register_blueprints(app)
    
    # تهيئة معالجات الأخطاء
    _init_error_handlers(app)
    
    # تهيئة وحدة التشفير
    _init_encryption(app)
    
    return app

def _ensure_app_folders(app):
    """
    التأكد من وجود مجلدات التطبيق
    
    Args:
        app (Flask): تطبيق Flask
    """
    # إنشاء مجلد التحميل
    upload_folder = app.config.get('UPLOAD_FOLDER')
    if upload_folder:
        os.makedirs(upload_folder, exist_ok=True)
    
    # إنشاء مجلد التصدير
    export_folder = os.path.join('static', 'exports')
    os.makedirs(export_folder, exist_ok=True)
    
    # إنشاء مجلد السجلات
    log_folder = 'logs'
    os.makedirs(log_folder, exist_ok=True)

def _init_logging(app):
    """
    تهيئة التسجيل
    
    Args:
        app (Flask): تطبيق Flask
    """
    # إعداد مستوى التسجيل
    app.logger.setLevel(getattr(logging, app.config.get('LOG_LEVEL', 'INFO')))
    
    # إضافة معالج ملف السجل
    log_file = app.config.get('LOG_FILE', 'app.log')
    file_handler = logging.FileHandler(log_file)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    ))
    app.logger.addHandler(file_handler)
    
    app.logger.info('تم بدء التطبيق في %s', datetime.now().isoformat())

def _init_extensions(app):
    """
    تهيئة ملحقات التطبيق
    
    Args:
        app (Flask): تطبيق Flask
    """
    # قاعدة البيانات
    db.init_app(app)
    
    # تهيئة JWT
    jwt.init_app(app)
    
    # تهيئة محدد معدل الطلبات
    limiter.init_app(app)
    
    # تهيئة ذاكرة التخزين المؤقت
    cache.init_app(app)
    
    # تهيئة الأمان (Talisman)
    if app.config.get('ENV') == 'production':
        talisman.init_app(app)
    
    # تهيئة مشاركة الموارد عبر الأصول (CORS)
    cors.init_app(app)

def _init_user_management(app):
    """
    تهيئة إدارة المستخدمين
    
    Args:
        app (Flask): تطبيق Flask
    """
    login_manager.init_app(app)
    
    @login_manager.user_loader
    def load_user(user_id):
        """
        تحميل المستخدم حسب المعرف
        
        Args:
            user_id (str): معرف المستخدم
        
        Returns:
            User: كائن المستخدم
        """
        from app.models.user import User
        return User.query.get(int(user_id))

def _register_blueprints(app):
    """
    تسجيل مخططات المسارات
    
    Args:
        app (Flask): تطبيق Flask
    """
    # استيراد المسارات
    from app.routes.main import main_bp
    from app.routes.auth import auth_bp
    from app.routes.api import api_bp
    
    # تسجيل المسارات
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(api_bp)

def _init_error_handlers(app):
    """
    تهيئة معالجات الأخطاء
    
    Args:
        app (Flask): تطبيق Flask
    """
    @app.errorhandler(404)
    def page_not_found(error):
        """معالجة خطأ 404 - الصفحة غير موجودة"""
        if request.path.startswith('/api/'):
            return jsonify({'error': 'Resource not found'}), 404
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(500)
    def server_error(error):
        """معالجة خطأ 500 - خطأ في الخادم"""
        app.logger.error('خطأ في الخادم: %s', str(error))
        if request.path.startswith('/api/'):
            return jsonify({'error': 'Internal server error'}), 500
        return render_template('errors/500.html'), 500
    
    @app.errorhandler(403)
    def forbidden(error):
        """معالجة خطأ 403 - غير مصرح به"""
        if request.path.startswith('/api/'):
            return jsonify({'error': 'Forbidden'}), 403
        return render_template('errors/403.html'), 403
    
    @app.errorhandler(401)
    def unauthorized(error):
        """معالجة خطأ 401 - غير مصادق عليه"""
        if request.path.startswith('/api/'):
            return jsonify({'error': 'Unauthorized'}), 401
        return render_template('errors/401.html'), 401
    
    # معالجة أخطاء محدد معدل الطلبات
    from flask_limiter.errors import RateLimitExceeded
    
    @app.errorhandler(RateLimitExceeded)
    def handle_rate_limit_exceeded(error):
        """معالجة خطأ تجاوز حد معدل الطلبات"""
        if request.path.startswith('/api/'):
            return jsonify({'error': 'Rate limit exceeded'}), 429
        return render_template('errors/429.html'), 429

def _init_encryption(app):
    """
    تهيئة وحدة التشفير
    
    Args:
        app (Flask): تطبيق Flask
    """
    from app.security.encryption import init_encryption
    init_encryption(app.config.get('ENCRYPTION_KEY'))