"""
إعدادات نظام تقييم BTEC
"""

import os
import logging
from datetime import timedelta

import dj_database_url

# إعدادات البيئة
class Config:
    """الإعدادات الأساسية"""
    # إعدادات البيئة
    ENV = os.environ.get('FLASK_ENV', 'production')
    DEBUG = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    TESTING = False
    
    # إعدادات التطبيق
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'this-should-be-changed-in-production'
    APP_NAME = 'نظام تقييم BTEC'
    VERSION = '1.0.0'
    
    # إعدادات قاعدة البيانات
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    if SQLALCHEMY_DATABASE_URI and SQLALCHEMY_DATABASE_URI.startswith('postgres://'):
        SQLALCHEMY_DATABASE_URI = SQLALCHEMY_DATABASE_URI.replace('postgres://', 'postgresql://', 1)
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_recycle': 300,
        'pool_pre_ping': True
    }
    
    # إعدادات JWT
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or SECRET_KEY
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    JWT_BLACKLIST_ENABLED = True
    JWT_BLACKLIST_TOKEN_CHECKS = ['access', 'refresh']
    
    # إعدادات التشفير
    ENCRYPTION_KEY = os.environ.get('ENCRYPTION_KEY')
    
    # إعدادات التخزين المؤقت
    CACHE_TYPE = 'simple'  # يمكن تغييره إلى 'redis' في الإنتاج
    CACHE_DEFAULT_TIMEOUT = 300  # 5 دقائق
    
    # إعدادات التسجيل
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO').upper()
    LOG_FILE = os.environ.get('LOG_FILE', 'app.log')
    
    # إعدادات الملفات الثابتة
    STATIC_FOLDER = 'static'
    STATIC_URL_PATH = '/static'
    
    # إعدادات القوالب
    TEMPLATE_FOLDER = 'templates'
    
    # إعدادات تحميل الملفات
    UPLOAD_FOLDER = os.path.join('static', 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 ميجابايت
    
    # إعدادات البريد الإلكتروني
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 25))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'False').lower() == 'true'
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER', 'no-reply@btec-eval.com')
    
    # إعدادات الواجهة البرمجية للذكاء الاصطناعي
    AI_API_KEY = os.environ.get('AI_API_KEY')
    AI_API_URL = os.environ.get('AI_API_URL', 'https://api.openai.com/v1')
    AI_MODEL = os.environ.get('AI_MODEL', 'gpt-4-turbo')
    
    # إعدادات Redis (للتخزين المؤقت والمهام الخلفية)
    REDIS_URL = os.environ.get('REDIS_URL')
    
    # إعدادات طابور المهام (Celery)
    CELERY_BROKER_URL = os.environ.get('REDIS_URL') or 'redis://localhost:6379/0'
    CELERY_RESULT_BACKEND = os.environ.get('REDIS_URL') or 'redis://localhost:6379/0'
    
    # إعدادات الأمان
    SESSION_COOKIE_SECURE = os.environ.get('SESSION_COOKIE_SECURE', 'False').lower() == 'true'
    SESSION_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_SECURE = SESSION_COOKIE_SECURE
    REMEMBER_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_DURATION = timedelta(days=14)
    
    @staticmethod
    def init_app(app):
        """تهيئة التطبيق"""
        # إعداد التسجيل
        logging.basicConfig(
            level=getattr(logging, app.config['LOG_LEVEL']),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            filename=app.config['LOG_FILE']
        )
        
        # التأكد من وجود مجلد التحميل
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# إعدادات بيئة التطوير
class DevelopmentConfig(Config):
    """إعدادات بيئة التطوير"""
    ENV = 'development'
    DEBUG = True
    
    # استخدام قاعدة بيانات SQLite محلية للتطوير
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///dev.db'
    
    # تعطيل بعض تدابير الأمان في بيئة التطوير
    SESSION_COOKIE_SECURE = False
    REMEMBER_COOKIE_SECURE = False
    
    @staticmethod
    def init_app(app):
        Config.init_app(app)
        app.logger.setLevel(logging.DEBUG)

# إعدادات بيئة الاختبار
class TestingConfig(Config):
    """إعدادات بيئة الاختبار"""
    ENV = 'testing'
    TESTING = True
    DEBUG = True
    
    # استخدام قاعدة بيانات SQLite في الذاكرة للاختبار
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL') or 'sqlite:///:memory:'
    
    # تعطيل حماية نموذج CSRF للاختبار
    WTF_CSRF_ENABLED = False
    
    # تقليل وقت انتهاء صلاحية الرمز للاختبار
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(seconds=10)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(seconds=30)
    
    # تعطيل بعض تدابير الأمان في بيئة الاختبار
    SESSION_COOKIE_SECURE = False
    REMEMBER_COOKIE_SECURE = False

# إعدادات بيئة الإنتاج
class ProductionConfig(Config):
    """إعدادات بيئة الإنتاج"""
    @staticmethod
    def init_app(app):
        Config.init_app(app)
        
        # استخدام Talisman لإضافة رؤوس أمان HTTP
        from flask_talisman import Talisman
        
        csp = {
            'default-src': "'self'",
            'img-src': ['*', "data:"],
            'style-src': ["'self'", "'unsafe-inline'", "https://fonts.googleapis.com"],
            'font-src': ["'self'", "https://fonts.gstatic.com"],
            'script-src': ["'self'", "'unsafe-inline'", "'unsafe-eval'"],
            'connect-src': ["'self'"]
        }
        
        Talisman(
            app,
            content_security_policy=csp,
            content_security_policy_nonce_in=['script-src', 'style-src'],
            force_https=True,
            strict_transport_security=True,
            strict_transport_security_preload=True,
            strict_transport_security_max_age=31536000,  # 1 سنة
            referrer_policy='same-origin'
        )

# قاموس التكوينات
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}