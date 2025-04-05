"""
ملف تكوين منصة مُدقِّق
"""
import os
from datetime import timedelta

class Config(object):
    """الفئة الأساسية للتكوين"""
    SECRET_KEY = os.environ.get('SECRET_KEY', 'default-secret-key-for-development')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///mudaqqiq.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # تكوين JWT
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'default-jwt-secret-key-for-development')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    
    # تكوين البريد الإلكتروني
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.example.com')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() in ['true', 'on', '1']
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME', '')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD', '')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER', 'mudaqqiq@example.com')
    
    # تكوين تحميل الملفات
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'app/static/uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB الحد الأقصى لحجم الملف
    ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'txt', 'png', 'jpg', 'jpeg', 'gif'}
    
    # تكوين CORS
    CORS_HEADERS = 'Content-Type'
    
    # تكوين التخزين المؤقت
    CACHE_TYPE = 'simple'
    CACHE_DEFAULT_TIMEOUT = 300
    
    # تكوين التسجيل
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    LOG_FILE = 'mudaqqiq.log'
    
    # تكوين قلعة Grok
    CASTLE_GROK_ENABLED = True
    CASTLE_GROK_THEME = 'mystical'
    
    # تكوين نظام التقييم
    AI_EVALUATION_ENABLED = True
    MAX_PROJECTS_PER_USER = 20
    
    # تكوين منصة مُدقِّق
    MUDAQQIQ_NAME = 'منصة مُدقِّق لتقييم مشاريع BTEC'
    MUDAQQIQ_VERSION = '1.0.0'
    MUDAQQIQ_ADMIN_EMAIL = os.environ.get('MUDAQQIQ_ADMIN_EMAIL', 'admin@example.com')
    
    @staticmethod
    def init_app(app):
        """تهيئة التطبيق"""
        pass

class DevelopmentConfig(Config):
    """تكوين بيئة التطوير"""
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or 'sqlite:///mudaqqiq_dev.db'

class TestingConfig(Config):
    """تكوين بيئة الاختبار"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL') or 'sqlite:///mudaqqiq_test.db'
    WTF_CSRF_ENABLED = False

class ProductionConfig(Config):
    """تكوين بيئة الإنتاج"""
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    
    @classmethod
    def init_app(cls, app):
        """تهيئة التطبيق"""
        Config.init_app(app)
        
        # تسجيل رسائل الخطأ في البريد الإلكتروني
        import logging
        from logging.handlers import SMTPHandler
        credentials = None
        secure = None
        if cls.MAIL_USERNAME and cls.MAIL_PASSWORD:
            credentials = (cls.MAIL_USERNAME, cls.MAIL_PASSWORD)
        if cls.MAIL_USE_TLS:
            secure = ()
        mail_handler = SMTPHandler(
            mailhost=(cls.MAIL_SERVER, cls.MAIL_PORT),
            fromaddr=cls.MAIL_DEFAULT_SENDER,
            toaddrs=[cls.MUDAQQIQ_ADMIN_EMAIL],
            subject='خطأ في منصة مُدقِّق',
            credentials=credentials,
            secure=secure)
        mail_handler.setLevel(logging.ERROR)
        app.logger.addHandler(mail_handler)

config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}