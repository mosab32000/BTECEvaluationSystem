"""
ملف إعدادات نظام تقييم BTEC
"""
import os
import logging
from dotenv import load_dotenv

# تحميل متغيرات البيئة
load_dotenv()

# تهيئة السجل
logger = logging.getLogger(__name__)

class Config:
    """الإعدادات العامة للتطبيق"""
    # إعدادات التطبيق
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
    
    # إعدادات الأمان
    TALISMAN_ENABLED = os.environ.get('TALISMAN_ENABLED', 'True').lower() == 'true'
    TALISMAN_FORCE_HTTPS = os.environ.get('TALISMAN_FORCE_HTTPS', 'False').lower() == 'true'
    TALISMAN_STRICT_TRANSPORT_SECURITY = True
    
    # إعدادات JSON Web Token
    JWT_ACCESS_TOKEN_EXPIRES = 3600  # ساعة واحدة
    JWT_REFRESH_TOKEN_EXPIRES = 2592000  # 30 يوم
    
    # إعدادات Limiter
    RATELIMIT_ENABLED = True
    RATELIMIT_DEFAULT = "300/hour"
    RATELIMIT_STORAGE_URL = "memory://"
    
    # إعدادات الذاكرة المؤقتة
    CACHE_TYPE = 'simple'
    CACHE_DEFAULT_TIMEOUT = 300
    
    # إعدادات التشفير
    ENCRYPTION_KEY = os.environ.get('ENCRYPTION_KEY') or 'مفتاح-تشفير-افتراضي-للتطوير-فقط-32-حرف'
    
    # إعدادات الرفع
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 ميجابايت
    
    # إعدادات OpenAI
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
    AI_ENABLED = os.environ.get('AI_ENABLED', 'True').lower() == 'true'
    AI_MODEL = os.environ.get('AI_MODEL', 'gpt-3.5-turbo')
    
    # إعدادات البلوكتشين
    BLOCKCHAIN_ENABLED = os.environ.get('BLOCKCHAIN_ENABLED', 'False').lower() == 'true'
    
    # إعدادات اللغة
    DEFAULT_LANGUAGE = os.environ.get('DEFAULT_LANGUAGE', 'ar')
    SUPPORTED_LANGUAGES = ['ar', 'en']
    
    # إعدادات التسجيل
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO').upper()
    LOG_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs', 'app.log')
    
    @staticmethod
    def init_app(app):
        """تهيئة التطبيق بالإعدادات العامة"""
        # إنشاء مجلد الرفع إذا لم يكن موجودًا
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
    
    # إعدادات الأمان
    TALISMAN_FORCE_HTTPS = False
    TALISMAN_CONTENT_SECURITY_POLICY = {
        'default-src': ["'self'", "'unsafe-inline'", "'unsafe-eval'", 'data:', '*'],
        'img-src': ["'self'", 'data:', '*'],
        'style-src': ["'self'", "'unsafe-inline'", '*'],
        'script-src': ["'self'", "'unsafe-inline'", "'unsafe-eval'", '*'],
        'font-src': ["'self'", 'data:', '*']
    }
    
    @staticmethod
    def init_app(app):
        """تهيئة التطبيق بإعدادات التطوير"""
        Config.init_app(app)
        
        # إعداد التسجيل
        file_handler = logging.FileHandler(Config.LOG_FILE)
        file_handler.setLevel(getattr(logging, Config.LOG_LEVEL))
        file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(file_formatter)
        
        console_handler = logging.StreamHandler()
        console_handler.setLevel(getattr(logging, Config.LOG_LEVEL))
        console_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        console_handler.setFormatter(console_formatter)
        
        # تهيئة سجل التطبيق
        app.logger.setLevel(getattr(logging, Config.LOG_LEVEL))
        app.logger.addHandler(file_handler)
        app.logger.addHandler(console_handler)
        
        # تهيئة سجل التطوير
        dev_logger = logging.getLogger('development')
        dev_logger.setLevel(getattr(logging, Config.LOG_LEVEL))
        dev_logger.addHandler(file_handler)
        dev_logger.addHandler(console_handler)
        
        dev_logger.info('تهيئة بيئة التطوير')

class TestingConfig(Config):
    """إعدادات بيئة الاختبار"""
    TESTING = True
    DEBUG = False
    WTF_CSRF_ENABLED = False
    
    # استخدام قاعدة بيانات منفصلة للاختبار
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL') or 'postgresql://postgres:postgres@localhost:5432/btec_evaluation_test'
    
    @staticmethod
    def init_app(app):
        """تهيئة التطبيق بإعدادات الاختبار"""
        Config.init_app(app)
        
        # تعطيل التسجيل أثناء الاختبار
        app.logger.setLevel(logging.ERROR)

class ProductionConfig(Config):
    """إعدادات بيئة الإنتاج"""
    DEBUG = False
    TESTING = False
    
    # يجب تعيين المفاتيح السرية في بيئة الإنتاج
    SECRET_KEY = os.environ.get('SECRET_KEY')
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY')
    WTF_CSRF_SECRET_KEY = os.environ.get('WTF_CSRF_SECRET_KEY')
    ENCRYPTION_KEY = os.environ.get('ENCRYPTION_KEY')
    
    # إعدادات الأمان المشددة
    TALISMAN_FORCE_HTTPS = True
    TALISMAN_CONTENT_SECURITY_POLICY = {
        'default-src': ["'self'"],
        'img-src': ["'self'", 'data:'],
        'style-src': ["'self'", "'unsafe-inline'"],
        'script-src': ["'self'"],
        'font-src': ["'self'", 'data:']
    }
    
    # إعدادات الذاكرة المؤقتة
    CACHE_TYPE = 'redis'
    CACHE_REDIS_URL = os.environ.get('REDIS_URL')
    
    # إعدادات Limiter
    RATELIMIT_STORAGE_URL = os.environ.get('REDIS_URL')
    
    @staticmethod
    def init_app(app):
        """تهيئة التطبيق بإعدادات الإنتاج"""
        Config.init_app(app)
        
        # التحقق من تعيين المفاتيح السرية
        if not app.config['SECRET_KEY'] or app.config['SECRET_KEY'] == 'مفتاح-سري-افتراضي-للتطوير-فقط':
            app.logger.error('SECRET_KEY غير معين في بيئة الإنتاج')
            raise ValueError('يجب تعيين SECRET_KEY في بيئة الإنتاج')
        
        if not app.config['JWT_SECRET_KEY'] or app.config['JWT_SECRET_KEY'] == 'مفتاح-سري-jwt-افتراضي-للتطوير-فقط':
            app.logger.error('JWT_SECRET_KEY غير معين في بيئة الإنتاج')
            raise ValueError('يجب تعيين JWT_SECRET_KEY في بيئة الإنتاج')
        
        if not app.config['ENCRYPTION_KEY'] or app.config['ENCRYPTION_KEY'] == 'مفتاح-تشفير-افتراضي-للتطوير-فقط-32-حرف':
            app.logger.error('ENCRYPTION_KEY غير معين في بيئة الإنتاج')
            raise ValueError('يجب تعيين ENCRYPTION_KEY في بيئة الإنتاج')
        
        # إعداد التسجيل
        file_handler = logging.FileHandler(Config.LOG_FILE)
        file_handler.setLevel(getattr(logging, Config.LOG_LEVEL))
        file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(file_formatter)
        
        # تهيئة سجل التطبيق
        app.logger.setLevel(getattr(logging, Config.LOG_LEVEL))
        app.logger.addHandler(file_handler)
        
        app.logger.info('تهيئة بيئة الإنتاج')

# قاموس الإعدادات
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}

# الإعدادات الافتراضية
default_config = os.environ.get('FLASK_CONFIG', 'default')