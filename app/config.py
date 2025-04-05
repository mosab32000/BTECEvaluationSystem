"""
ملف إعدادات نظام تقييم BTEC
"""
import os
import secrets
from datetime import timedelta

from dotenv import load_dotenv

# تحميل المتغيرات البيئية
load_dotenv()

class Config:
    """الإعدادات العامة للتطبيق"""
    
    # الإعدادات الأساسية
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'مفتاح-سري-افتراضي-للتطوير-فقط'
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'مفتاح-سري-jwt-افتراضي-للتطوير-فقط'
    SESSION_TYPE = 'filesystem'
    SESSION_PERMANENT = False
    SESSION_USE_SIGNER = True
    
    # إعدادات قاعدة البيانات
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'postgresql://postgres:postgres@localhost:5432/btec_evaluation'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False
    
    # إعدادات CSRF
    WTF_CSRF_ENABLED = True
    WTF_CSRF_SECRET_KEY = os.environ.get('WTF_CSRF_SECRET_KEY') or 'مفتاح-سري-csrf-افتراضي-للتطوير-فقط'
    
    # إعدادات أمان الويب (Talisman)
    TALISMAN_ENABLED = os.environ.get('TALISMAN_ENABLED', 'True').lower() == 'true'
    TALISMAN_FORCE_HTTPS = os.environ.get('TALISMAN_FORCE_HTTPS', 'False').lower() == 'true'
    TALISMAN_STRICT_TRANSPORT_SECURITY = True
    
    # إعدادات JWT
    JWT_ACCESS_TOKEN_EXPIRES = 3600  # ساعة واحدة
    JWT_REFRESH_TOKEN_EXPIRES = 2592000  # 30 يوم
    
    # إعدادات محدد معدل الطلبات
    RATELIMIT_ENABLED = True
    RATELIMIT_DEFAULT = "300/hour"
    RATELIMIT_STORAGE_URL = "memory://"
    
    # إعدادات التخزين المؤقت
    CACHE_TYPE = 'simple'
    CACHE_DEFAULT_TIMEOUT = 300
    
    # إعدادات التشفير
    ENCRYPTION_KEY = os.environ.get('ENCRYPTION_KEY') or 'مفتاح-تشفير-افتراضي-للتطوير-فقط-32-حرف'
    
    # إعدادات تحميل الملفات
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 ميجابايت
    
    # إعدادات الذكاء الاصطناعي
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
    AI_ENABLED = os.environ.get('AI_ENABLED', 'True').lower() == 'true'
    AI_MODEL = os.environ.get('AI_MODEL', 'gpt-3.5-turbo')
    
    # إعدادات البلوكتشين
    BLOCKCHAIN_ENABLED = os.environ.get('BLOCKCHAIN_ENABLED', 'False').lower() == 'true'
    
    # إعدادات اللغة
    DEFAULT_LANGUAGE = os.environ.get('DEFAULT_LANGUAGE', 'ar')
    SUPPORTED_LANGUAGES = ['ar', 'en']
    
    # إعدادات السجل
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO').upper()
    LOG_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs', 'app.log')
    
    @staticmethod
    def init_app(app):
        """تهيئة التطبيق بالإعدادات العامة"""
        # إنشاء مجلد التحميل إذا لم يكن موجودًا
        if not os.path.exists(Config.UPLOAD_FOLDER):
            os.makedirs(Config.UPLOAD_FOLDER)
        
        # إنشاء مجلد السجلات إذا لم يكن موجودًا
        log_dir = os.path.dirname(Config.LOG_FILE)
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)

class DevelopmentConfig(Config):
    """إعدادات بيئة التطوير"""
    DEBUG = True
    TESTING = False
    
    # إعدادات أمان الويب للتطوير
    TALISMAN_FORCE_HTTPS = False
    TALISMAN_CONTENT_SECURITY_POLICY = {
        'default-src': ["'self'", "'unsafe-inline'", "'unsafe-eval'", 'data:', '*'],
        'img-src': ["'self'", 'data:', '*'],
        'style-src': ["'self'", "'unsafe-inline'", '*'],
        'script-src': ["'self'", "'unsafe-inline'", "'unsafe-eval'", '*'],
        'font-src': ["'self'", 'data:', '*']
    }
    
    # إعدادات السجل للتطوير
    LOG_LEVEL = 'DEBUG'
    
    @staticmethod
    def init_app(app):
        """تهيئة التطبيق بإعدادات التطوير"""
        Config.init_app(app)
        app.logger.info('تم تهيئة التطبيق في بيئة التطوير')

class TestingConfig(Config):
    """إعدادات بيئة الاختبار"""
    TESTING = True
    DEBUG = False
    WTF_CSRF_ENABLED = False
    
    # استخدام قاعدة بيانات اختبار منفصلة
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL') or 'postgresql://postgres:postgres@localhost:5432/btec_evaluation_test'
    
    @staticmethod
    def init_app(app):
        """تهيئة التطبيق بإعدادات الاختبار"""
        Config.init_app(app)
        app.logger.info('تم تهيئة التطبيق في بيئة الاختبار')

class ProductionConfig(Config):
    """إعدادات بيئة الإنتاج"""
    DEBUG = False
    TESTING = False
    
    # إعدادات أمان مشددة في الإنتاج
    SECRET_KEY = os.environ.get('SECRET_KEY')
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY')
    WTF_CSRF_SECRET_KEY = os.environ.get('WTF_CSRF_SECRET_KEY')
    ENCRYPTION_KEY = os.environ.get('ENCRYPTION_KEY')
    
    # إعدادات أمان الويب المشددة
    TALISMAN_FORCE_HTTPS = True
    TALISMAN_CONTENT_SECURITY_POLICY = {
        'default-src': ["'self'"],
        'img-src': ["'self'", 'data:'],
        'style-src': ["'self'", "'unsafe-inline'"],
        'script-src': ["'self'"],
        'font-src': ["'self'", 'data:']
    }
    
    # استخدام Redis للتخزين المؤقت في الإنتاج
    CACHE_TYPE = 'redis'
    CACHE_REDIS_URL = os.environ.get('REDIS_URL')
    
    # استخدام Redis لمحدد معدل الطلبات في الإنتاج
    RATELIMIT_STORAGE_URL = os.environ.get('REDIS_URL')
    
    @staticmethod
    def init_app(app):
        """تهيئة التطبيق بإعدادات الإنتاج"""
        Config.init_app(app)
        
        # التأكد من وجود المفاتيح السرية في الإنتاج
        if not app.config['SECRET_KEY']:
            app.config['SECRET_KEY'] = secrets.token_hex(16)
            app.logger.warning('تم إنشاء مفتاح سري عشوائي للتطبيق')
        
        if not app.config['JWT_SECRET_KEY']:
            app.config['JWT_SECRET_KEY'] = secrets.token_hex(16)
            app.logger.warning('تم إنشاء مفتاح سري JWT عشوائي')
        
        app.logger.info('تم تهيئة التطبيق في بيئة الإنتاج')