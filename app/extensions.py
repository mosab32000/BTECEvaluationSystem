"""
ملحقات التطبيق في نظام تقييم BTEC
"""

import os

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from flask_login import LoginManager
from flask_jwt_extended import JWTManager
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_talisman import Talisman
from flask_caching import Cache
from flask_cors import CORS

# إنشاء لوجين مانجر
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message = 'يرجى تسجيل الدخول للوصول إلى هذه الصفحة.'
login_manager.login_message_category = 'info'

# إنشاء جيه دبليو تي مانجر
jwt = JWTManager()

# إنشاء ليميتر
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

# إنشاء كاش
cache = Cache(config={
    'CACHE_TYPE': 'simple',
    'CACHE_DEFAULT_TIMEOUT': 300
})

# إنشاء قاعدة البيانات
class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

# إنشاء تاليسمان (الأمان)
talisman = Talisman()

# إنشاء كورس (للمصادر المتقاطعة)
cors = CORS()