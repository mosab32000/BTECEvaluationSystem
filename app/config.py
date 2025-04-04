"""
ملف إعدادات نظام تقييم BTEC
"""
import os
from datetime import timedelta

class Config:
    """الإعدادات الأساسية المشتركة"""
    # سر التطبيق
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'btec-evaluation-system-secret-key'
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'btec-evaluation-system-jwt-secret-key'
    ENCRYPTION_KEY = os.environ.get('ENCRYPTION_KEY') or 'btec-evaluation-system-encryption-key'
    
    # قاعدة البيانات
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///btec_evaluation.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # JWT
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=24)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    
    # التصفح
    ITEMS_PER_PAGE = 10
    UPLOAD_FOLDER = 'uploads'
    
    # OpenAI & البلوكتشين
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
    INFURA_URL = os.environ.get('INFURA_URL')
    CONTRACT_ADDRESS = os.environ.get('CONTRACT_ADDRESS')
    SIGNER_PRIVATE_KEY = os.environ.get('SIGNER_PRIVATE_KEY')
    
    # CORS
    ALLOWED_ORIGINS = os.environ.get('ALLOWED_ORIGINS', '*').split(',')
    
    # التسجيل
    LOG_LEVEL = 'INFO'
    
    @classmethod
    def init_app(cls, app):
        pass

class DevelopmentConfig(Config):
    """إعدادات بيئة التطوير"""
    # تمكين وضع التصحيح
    DEBUG = True
    FLASK_ENV = 'development'
    
    # زيادة مدة JWT للتطوير
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(days=7)
    
    # تخطي التحقق من البلوكتشين في التطوير
    SKIP_BLOCKCHAIN_VERIFICATION = True
    
    # مستوى التسجيل
    LOG_LEVEL = 'DEBUG'

class ProductionConfig(Config):
    """إعدادات بيئة الإنتاج"""
    # تعطيل وضع التصحيح
    DEBUG = False
    FLASK_ENV = 'production'
    
    # استخدام أسرار آمنة من متغيرات البيئة
    SECRET_KEY = os.environ.get('SECRET_KEY')
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY')
    ENCRYPTION_KEY = os.environ.get('ENCRYPTION_KEY')
    
    # نشر الاستثناءات
    PROPAGATE_EXCEPTIONS = True
    
    @classmethod
    def init_app(cls, app):
        # تطبيق إعدادات إضافية لبيئة الإنتاج
        super(ProductionConfig, cls).init_app(app)

class TestingConfig(Config):
    """إعدادات بيئة الاختبار"""
    # تمكين وضع الاختبار
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///test.db'
    SERVER_NAME = 'localhost.localdomain'
    
    # تعطيل CSRF للاختبار
    WTF_CSRF_ENABLED = False
    
    # استخدام أسرار ثابتة للاختبار
    SECRET_KEY = 'test-secret-key'
    JWT_SECRET_KEY = 'test-jwt-secret-key'
    ENCRYPTION_KEY = 'test-encryption-key'
    
    # JWT مع مدة أقصر للاختبار
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(seconds=30)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(minutes=5)
