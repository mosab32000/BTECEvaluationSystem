"""
ملف إعدادات نظام تقييم BTEC
"""

import os
import logging
from datetime import timedelta

logger = logging.getLogger(__name__)

class Config:
    """الإعدادات العامة للتطبيق"""
    
    SECRET_KEY = os.environ.get("SECRET_KEY") or "مفتاح-سري-افتراضي-للتطوير-فقط"
    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY") or "مفتاح-سري-jwt-افتراضي-للتطوير-فقط"
    SESSION_TYPE = "filesystem"
    SESSION_PERMANENT = False
    SESSION_USE_SIGNER = True
    
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL") or "postgresql://postgres:postgres@localhost:5432/btec_evaluation"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False
    
    WTF_CSRF_ENABLED = True
    WTF_CSRF_SECRET_KEY = os.environ.get("WTF_CSRF_SECRET_KEY") or "مفتاح-سري-csrf-افتراضي-للتطوير-فقط"
    
    TALISMAN_ENABLED = os.environ.get("TALISMAN_ENABLED", "True").lower() == "true"
    TALISMAN_FORCE_HTTPS = os.environ.get("TALISMAN_FORCE_HTTPS", "False").lower() == "true"
    TALISMAN_STRICT_TRANSPORT_SECURITY = True
    
    JWT_ACCESS_TOKEN_EXPIRES = 3600  # ساعة واحدة
    JWT_REFRESH_TOKEN_EXPIRES = 2592000  # 30 يوم
    
    RATELIMIT_ENABLED = True
    RATELIMIT_DEFAULT = "300/hour"
    RATELIMIT_STORAGE_URL = "memory://"
    
    CACHE_TYPE = "simple"
    CACHE_DEFAULT_TIMEOUT = 300
    
    ENCRYPTION_KEY = os.environ.get("ENCRYPTION_KEY") or "مفتاح-تشفير-افتراضي-للتطوير-فقط-32-حرف"
    
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.dirname(__file__)), "uploads")
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 ميجابايت
    
    OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
    AI_ENABLED = os.environ.get("AI_ENABLED", "True").lower() == "true"
    AI_MODEL = os.environ.get("AI_MODEL", "gpt-3.5-turbo")
    
    BLOCKCHAIN_ENABLED = os.environ.get("BLOCKCHAIN_ENABLED", "False").lower() == "true"
    
    DEFAULT_LANGUAGE = os.environ.get("DEFAULT_LANGUAGE", "ar")
    SUPPORTED_LANGUAGES = ["ar", "en"]
    
    LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO").upper()
    LOG_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs", "app.log")
    
    @staticmethod
    def init_app(app):
        """تهيئة التطبيق بالإعدادات العامة"""
        pass


class DevelopmentConfig(Config):
    """إعدادات بيئة التطوير"""
    DEBUG = True
    TESTING = False
    
    TALISMAN_FORCE_HTTPS = False
    TALISMAN_CONTENT_SECURITY_POLICY = {
        "default-src": ["'self'", "'unsafe-inline'", "'unsafe-eval'", "data:", "*"],
        "img-src": ["'self'", "data:", "*"],
        "style-src": ["'self'", "'unsafe-inline'", "*"],
        "script-src": ["'self'", "'unsafe-inline'", "'unsafe-eval'", "*"],
        "font-src": ["'self'", "data:", "*"]
    }
    
    LOG_LEVEL = "DEBUG"
    
    @staticmethod
    def init_app(app):
        """تهيئة التطبيق بإعدادات التطوير"""
        Config.init_app(app)
        logger.debug("تم تهيئة التطبيق بإعدادات التطوير")


class TestingConfig(Config):
    """إعدادات بيئة الاختبار"""
    TESTING = True
    DEBUG = False
    WTF_CSRF_ENABLED = False
    
    SQLALCHEMY_DATABASE_URI = os.environ.get("TEST_DATABASE_URL") or "postgresql://postgres:postgres@localhost:5432/btec_evaluation_test"
    
    @staticmethod
    def init_app(app):
        """تهيئة التطبيق بإعدادات الاختبار"""
        Config.init_app(app)
        logger.debug("تم تهيئة التطبيق بإعدادات الاختبار")


class ProductionConfig(Config):
    """إعدادات بيئة الإنتاج"""
    DEBUG = False
    TESTING = False
    
    SECRET_KEY = os.environ.get("SECRET_KEY")
    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY")
    WTF_CSRF_SECRET_KEY = os.environ.get("WTF_CSRF_SECRET_KEY")
    ENCRYPTION_KEY = os.environ.get("ENCRYPTION_KEY")
    
    TALISMAN_FORCE_HTTPS = True
    TALISMAN_CONTENT_SECURITY_POLICY = {
        "default-src": ["'self'"],
        "img-src": ["'self'", "data:"],
        "style-src": ["'self'", "'unsafe-inline'"],
        "script-src": ["'self'"],
        "font-src": ["'self'", "data:"]
    }
    
    CACHE_TYPE = "redis"
    CACHE_REDIS_URL = os.environ.get("REDIS_URL")
    
    RATELIMIT_STORAGE_URL = os.environ.get("REDIS_URL")
    
    @staticmethod
    def init_app(app):
        """تهيئة التطبيق بإعدادات الإنتاج"""
        Config.init_app(app)
        
        # تهيئة مكتبة السجلات للإنتاج
        import logging
        from logging.handlers import RotatingFileHandler
        
        file_handler = RotatingFileHandler(Config.LOG_FILE, maxBytes=10 * 1024 * 1024, backupCount=5)
        file_handler.setFormatter(logging.Formatter(
            "%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]"
        ))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        
        app.logger.setLevel(logging.INFO)
        app.logger.info("بدء تشغيل تطبيق نظام تقييم BTEC في بيئة الإنتاج")