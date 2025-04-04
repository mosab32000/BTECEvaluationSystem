"""
ملف إعدادات تطبيق نظام تقييم BTEC
"""
import os
from datetime import timedelta

class Config:
    """
    الإعدادات الأساسية للتطبيق
    """
    # إعدادات Flask
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev_secret_key'
    DEBUG = False
    TESTING = False
    
    # إعدادات قاعدة البيانات
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///btec.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_recycle': 280,
        'pool_pre_ping': True
    }
    
    # إعدادات JWT
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or SECRET_KEY
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    JWT_BLACKLIST_ENABLED = True
    JWT_BLACKLIST_TOKEN_CHECKS = ['access', 'refresh']
    
    # إعدادات التخزين
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER') or 'uploads'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB
    
    # إعدادات OpenAI
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
    OPENAI_MODEL = os.environ.get('OPENAI_MODEL') or 'gpt-4'
    
    # إعدادات البلوكتشين
    BLOCKCHAIN_ENABLED = os.environ.get('BLOCKCHAIN_ENABLED', 'False').lower() == 'true'
    INFURA_URL = os.environ.get('INFURA_URL')
    CONTRACT_ADDRESS = os.environ.get('CONTRACT_ADDRESS')
    SIGNER_PRIVATE_KEY = os.environ.get('SIGNER_PRIVATE_KEY')
    
    # إعدادات البريد الإلكتروني
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'True').lower() == 'true'
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER')
    
    # إعدادات أخرى
    REQUIRE_EMAIL_VERIFICATION = os.environ.get('REQUIRE_EMAIL_VERIFICATION', 'False').lower() == 'true'
    SECURITY_PASSWORD_SALT = os.environ.get('SECURITY_PASSWORD_SALT') or 'btec_evaluation_system'
    
    @staticmethod
    def init_app(app):
        """
        تهيئة التطبيق
        
        Args:
            app: تطبيق Flask
        """
        pass

class DevelopmentConfig(Config):
    """
    إعدادات بيئة التطوير
    """
    DEBUG = True
    
    @staticmethod
    def init_app(app):
        """
        تهيئة التطبيق في بيئة التطوير
        
        Args:
            app: تطبيق Flask
        """
        Config.init_app(app)
        
        # تعطيل CSP في بيئة التطوير
        app.config['TALISMAN_ENABLED'] = False

class TestingConfig(Config):
    """
    إعدادات بيئة الاختبار
    """
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    
    # تعطيل حماية CSRF في بيئة الاختبار
    WTF_CSRF_ENABLED = False

class ProductionConfig(Config):
    """
    إعدادات بيئة الإنتاج
    """
    # استخدام قاعدة بيانات PostgreSQL في بيئة الإنتاج
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'postgresql://postgres:postgres@localhost/btec'
    
    # إعدادات الأمان
    @staticmethod
    def init_app(app):
        """
        تهيئة التطبيق في بيئة الإنتاج
        
        Args:
            app: تطبيق Flask
        """
        Config.init_app(app)
        
        # تكوين Talisman (HTTPS)
        from flask_talisman import Talisman
        talisman = Talisman(
            app,
            content_security_policy={
                'default-src': ["'self'"],
                'style-src': ["'self'", "'unsafe-inline'", 'cdn.jsdelivr.net', 'cdnjs.cloudflare.com', 'fonts.googleapis.com'],
                'script-src': ["'self'", "'unsafe-inline'", 'cdn.jsdelivr.net', 'cdnjs.cloudflare.com'],
                'font-src': ["'self'", 'cdn.jsdelivr.net', 'cdnjs.cloudflare.com', 'fonts.gstatic.com'],
                'img-src': ["'self'", 'data:', 'via.placeholder.com']
            }
        )

class HerokuConfig(ProductionConfig):
    """
    إعدادات للنشر على منصة Heroku
    """
    @staticmethod
    def init_app(app):
        """
        تهيئة التطبيق في بيئة Heroku
        
        Args:
            app: تطبيق Flask
        """
        ProductionConfig.init_app(app)
        
        # تكوين ProxyFix
        from werkzeug.middleware.proxy_fix import ProxyFix
        app.wsgi_app = ProxyFix(app.wsgi_app)

class DockerConfig(ProductionConfig):
    """
    إعدادات للنشر على Docker
    """
    @staticmethod
    def init_app(app):
        """
        تهيئة التطبيق في بيئة Docker
        
        Args:
            app: تطبيق Flask
        """
        ProductionConfig.init_app(app)

# قاموس بإعدادات التطبيق المختلفة
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'heroku': HerokuConfig,
    'docker': DockerConfig,
    'default': DevelopmentConfig
}