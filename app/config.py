"""
ملف إعدادات نظام تقييم BTEC
"""
import os
from datetime import timedelta

class Config:
    """الإعدادات الأساسية المشتركة"""
    # أمان التطبيق
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'btec-evaluation-system-secret-key'
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'btec-evaluation-system-jwt-secret-key'
    ENCRYPTION_KEY = os.environ.get('ENCRYPTION_KEY') or 'btec-evaluation-system-encryption-key'
    
    # قاعدة البيانات
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///btec_evaluation.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # JWT إعدادات
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=24)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    
    # الصفحات والتحميل
    ITEMS_PER_PAGE = 10
    UPLOAD_FOLDER = 'uploads'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB كحد أقصى لحجم الملف المرفوع
    
    # API خارجية
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
    INFURA_URL = os.environ.get('INFURA_URL')
    CONTRACT_ADDRESS = os.environ.get('CONTRACT_ADDRESS')
    SIGNER_PRIVATE_KEY = os.environ.get('SIGNER_PRIVATE_KEY')
    
    # CORS إعدادات
    ALLOWED_ORIGINS = os.environ.get('ALLOWED_ORIGINS', '*').split(',')
    
    # التسجيل
    LOG_LEVEL = 'INFO'
    
    # التخزين المؤقت
    CACHE_TYPE = os.environ.get('CACHE_TYPE', 'SimpleCache')
    CACHE_REDIS_URL = os.environ.get('CACHE_REDIS_URL')
    CACHE_DEFAULT_TIMEOUT = int(os.environ.get('CACHE_DEFAULT_TIMEOUT', 300))
    
    # محدد الطلبات
    RATELIMIT_DEFAULT = os.environ.get('RATELIMIT_DEFAULT', '200 per day;50 per hour')
    RATELIMIT_STORAGE_URL = os.environ.get('RATELIMIT_STORAGE_URL', 'memory://')
    
    # تهيئة التطبيق
    @classmethod
    def init_app(cls, app):
        pass

class DevelopmentConfig(Config):
    """إعدادات بيئة التطوير"""
    # وضع التصحيح
    DEBUG = True
    FLASK_ENV = 'development'
    
    # تمديد مدة JWT في التطوير
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(days=7)
    
    # تخطي التحقق من البلوكتشين في التطوير
    SKIP_BLOCKCHAIN_VERIFICATION = True
    
    # السماح بـ CORS في التطوير
    CORS_HEADERS = 'Content-Type'
    
    # مستوى التسجيل
    LOG_LEVEL = 'DEBUG'
    
    # تخزين مؤقت أبسط في التطوير
    CACHE_TYPE = 'SimpleCache'

class ProductionConfig(Config):
    """إعدادات بيئة الإنتاج"""
    # تعطيل وضع التصحيح
    DEBUG = False
    FLASK_ENV = 'production'
    
    # استخدام مفاتيح آمنة من متغيرات البيئة
    SECRET_KEY = os.environ.get('SECRET_KEY')
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY')
    ENCRYPTION_KEY = os.environ.get('ENCRYPTION_KEY')
    
    # إرسال الاستثناءات إلى التطبيق
    PROPAGATE_EXCEPTIONS = True
    
    # تخزين مؤقت باستخدام Redis
    CACHE_TYPE = os.environ.get('CACHE_TYPE', 'RedisCache')
    
    # تهيئة خاصة في الإنتاج
    @classmethod
    def init_app(cls, app):
        Config.init_app(app)
        
        # معالجة الأخطاء عبر البريد الإلكتروني أو خدمة رصد الأخطاء
        # يمكن إضافة إعدادات إضافية هنا
        
        # تكوين محدد الطلبات بشكل أكثر صرامة في الإنتاج
        app.config['RATELIMIT_DEFAULT'] = os.environ.get('RATELIMIT_DEFAULT', '100 per day;20 per hour')

class TestingConfig(Config):
    """إعدادات بيئة الاختبار"""
    # وضع الاختبار
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///test.db'
    SERVER_NAME = 'localhost.localdomain'
    
    # تعطيل CSRF في الاختبارات
    WTF_CSRF_ENABLED = False
    
    # مفاتيح ثابتة للاختبار
    SECRET_KEY = 'test-secret-key'
    JWT_SECRET_KEY = 'test-jwt-secret-key'
    ENCRYPTION_KEY = 'test-encryption-key'
    
    # مدد أقصر للرموز المميزة في الاختبار
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(seconds=30)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(minutes=5)
    
    # تخطي التحقق من البلوكتشين في الاختبار
    SKIP_BLOCKCHAIN_VERIFICATION = True