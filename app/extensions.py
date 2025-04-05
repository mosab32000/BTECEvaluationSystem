"""
تعريف امتدادات Flask لنظام تقييم BTEC
"""

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_talisman import Talisman
from flask_caching import Cache

# تهيئة SQLAlchemy
db = SQLAlchemy()

# تهيئة Flask-Migrate
migrate = Migrate()

# تهيئة Flask-Login
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message = 'يرجى تسجيل الدخول للوصول إلى هذه الصفحة.'
login_manager.login_message_category = 'info'

# تهيئة JWT
jwt = JWTManager()

# تهيئة CORS
cors = CORS()

# تهيئة Rate Limiter
limiter = Limiter(key_func=get_remote_address)

# تهيئة Talisman (أمان HTTP)
talisman = Talisman()

# تهيئة Cache
cache = Cache()