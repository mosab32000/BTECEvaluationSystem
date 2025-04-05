"""
ملف إعدادات نظام تقييم BTEC
"""
import os
from datetime import timedelta

class Config:
    """الإعدادات الأساسية المشتركة"""
    # إعدادات التطبيق
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev_key')
    SESSION_TYPE = 'filesystem'
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)
    
    # إعدادات قاعدة البيانات
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_recycle': 300,
        'pool_pre_ping': True,
    }
    
    # إعدادات JWT
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'dev_jwt_key')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    
    # إعدادات أمان إضافية
    SECURITY_PASSWORD_SALT = os.environ.get('SECURITY_PASSWORD_SALT', 'dev_salt')
    
    # إعدادات التخزين المؤقت
    CACHE_TYPE = 'SimpleCache'
    CACHE_DEFAULT_TIMEOUT = 300
    
    # إعدادات الحد من معدل الطلبات
    RATELIMIT_DEFAULT = "100 per hour"
    RATELIMIT_STORAGE_URI = "memory://"
    
    # إعدادات الذكاء الاصطناعي
    AI_ENABLED = os.environ.get('AI_ENABLED', 'true').lower() == 'true'
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
    OPENAI_MODEL = os.environ.get('OPENAI_MODEL', 'gpt-4')
    
    # إعدادات البلوكتشين
    BLOCKCHAIN_ENABLED = os.environ.get('BLOCKCHAIN_ENABLED', 'false').lower() == 'true'
    INFURA_URL = os.environ.get('INFURA_URL')
    CONTRACT_ADDRESS = os.environ.get('CONTRACT_ADDRESS')
    SIGNER_PRIVATE_KEY = os.environ.get('SIGNER_PRIVATE_KEY')
    
    # إعدادات المسؤول
    ADMIN_EMAIL = os.environ.get('ADMIN_EMAIL', 'admin@btec-eval.com')
    DEFAULT_ADMIN_PASSWORD = os.environ.get('DEFAULT_ADMIN_PASSWORD', 'defaultadmin2025')


class DevelopmentConfig(Config):
    """إعدادات بيئة التطوير"""
    DEBUG = True
    DEVELOPMENT = True


class TestingConfig(Config):
    """إعدادات بيئة الاختبار"""
    TESTING = True
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False
    PRESERVE_CONTEXT_ON_EXCEPTION = False


class ProductionConfig(Config):
    """إعدادات بيئة الإنتاج"""
    DEBUG = False
    TESTING = False
    
    # إعدادات أمان إضافية للإنتاج
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_SECURE = True
    REMEMBER_COOKIE_HTTPONLY = True


# تكوين قاموس للإعدادات
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}

# الحصول على الإعدادات الحالية
def get_config():
    """الحصول على كائن الإعدادات الحالي بناءً على بيئة التشغيل"""
    environment = os.environ.get('FLASK_ENV', 'development')
    return config.get(environment, config['default'])