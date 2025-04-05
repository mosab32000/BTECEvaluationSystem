"""
ملف التكوين لنظام تقييم BTEC
"""

import os
from pathlib import Path
import dj_database_url

# المسار الأساسي للتطبيق
BASE_DIR = Path(__file__).resolve().parent.parent

# إعدادات الأمان
SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-key-for-development')
JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', SECRET_KEY)
ENCRYPTION_KEY = os.environ.get('ENCRYPTION_KEY')

# إعدادات التشغيل
DEBUG = os.environ.get('DEBUG', 'False') == 'True'
TESTING = os.environ.get('TESTING', 'False') == 'True'

# معلومات النظام
VERSION = '1.0.0'
APP_NAME = 'نظام تقييم BTEC'

# المضيفين المسموح لهم
ALLOWED_HOSTS = [
    os.environ.get('RENDER_EXTERNAL_HOSTNAME', ''),
    'localhost',
    '127.0.0.1',
    '0.0.0.0'
]
# إزالة القيم الفارغة
ALLOWED_HOSTS = [host for host in ALLOWED_HOSTS if host]

# إعدادات قاعدة البيانات
SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///btec.db')
# التعامل مع تنسيق Render المختلف لـ DATABASE_URL
if SQLALCHEMY_DATABASE_URI.startswith('postgres://'):
    SQLALCHEMY_DATABASE_URI = SQLALCHEMY_DATABASE_URI.replace('postgres://', 'postgresql://', 1)

SQLALCHEMY_ENGINE_OPTIONS = {
    'pool_recycle': 300,
    'pool_pre_ping': True,
}

# إعدادات الملفات الثابتة
STATIC_URL = '/static/'
STATIC_FOLDER = os.path.join(BASE_DIR, 'app', 'static')
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# إعدادات التخزين المؤقت
CACHE_TYPE = 'SimpleCache'
CACHE_DEFAULT_TIMEOUT = 300  # 5 دقائق

# إعدادات JWT
JWT_ACCESS_TOKEN_EXPIRES = 3600  # ساعة واحدة
JWT_REFRESH_TOKEN_EXPIRES = 2592000  # 30 يوم

# إعدادات أخرى
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 ميجابايت

# إعدادات OpenAI API (إذا كانت مستخدمة)
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
OPENAI_MODEL = os.environ.get('OPENAI_MODEL', 'gpt-3.5-turbo')

# إعدادات البلوكشين (إذا كانت مستخدمة)
BLOCKCHAIN_ENABLED = os.environ.get('BLOCKCHAIN_ENABLED', 'False') == 'True'
BLOCKCHAIN_PROVIDER = os.environ.get('BLOCKCHAIN_PROVIDER', 'http://localhost:8545')
BLOCKCHAIN_NETWORK = os.environ.get('BLOCKCHAIN_NETWORK', 'development')