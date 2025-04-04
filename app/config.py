"""
ملف إعدادات نظام تقييم BTEC
"""

import os
from datetime import timedelta

class Config:
    """الإعدادات الأساسية المشتركة"""
    
    # إعدادات الأمان
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'btec-evaluation-system-secret-key'
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'btec-evaluation-system-jwt-secret-key'
    ENCRYPTION_KEY = os.environ.get('ENCRYPTION_KEY') or 'btec-evaluation-system-encryption-key'
    
    # إعدادات قاعدة البيانات
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///btec_evaluation.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # إعدادات JWT
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=24)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    
    # إعدادات التطبيق
    ITEMS_PER_PAGE = 10
    UPLOAD_FOLDER = 'uploads'
    
    # إعدادات الخدمات الخارجية
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
    INFURA_URL = os.environ.get('INFURA_URL')
    CONTRACT_ADDRESS = os.environ.get('CONTRACT_ADDRESS')
    SIGNER_PRIVATE_KEY = os.environ.get('SIGNER_PRIVATE_KEY')
    
    # إعدادات CORS
    ALLOWED_ORIGINS = os.environ.get('ALLOWED_ORIGINS', '*').split(',')


class DevelopmentConfig(Config):
    """إعدادات بيئة التطوير"""
    
    DEBUG = True
    FLASK_ENV = 'development'
    
    # إعدادات خاصة بالتطوير
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(days=7)  # فترة أطول للتوكن أثناء التطوير


class ProductionConfig(Config):
    """إعدادات بيئة الإنتاج"""
    
    DEBUG = False
    FLASK_ENV = 'production'
    
    # تأكد من وجود المفاتيح السرية في بيئة الإنتاج
    @classmethod
    def init_app(cls, app):
        assert os.environ.get('SECRET_KEY'), 'SECRET_KEY environment variable is not set'
        assert os.environ.get('JWT_SECRET_KEY'), 'JWT_SECRET_KEY environment variable is not set'
        assert os.environ.get('ENCRYPTION_KEY'), 'ENCRYPTION_KEY environment variable is not set'


class TestingConfig(Config):
    """إعدادات بيئة الاختبار"""
    
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///test.db'
    SERVER_NAME = 'localhost.localdomain'
    
    # إعدادات خاصة بالاختبار
    WTF_CSRF_ENABLED = False
