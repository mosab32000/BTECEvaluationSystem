"""
التطبيق الرئيسي لمنصة مُدقِّق
"""
import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager

# تهيئة المتغيرات العامة
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
jwt = JWTManager()

def create_app(config_class=None):
    """إنشاء وتكوين تطبيق Flask"""
    app = Flask(__name__)
    
    # تكوين التطبيق
    if config_class:
        app.config.from_object(config_class)
    else:
        # استخدام التكوين من المتغيرات البيئية أو القيم الافتراضية
        app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'default-secret-key-for-development')
        app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///mudaqqiq.db')
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', 'default-jwt-secret-key-for-development')
    
    # تهيئة الإضافات
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'يرجى تسجيل الدخول للوصول إلى هذه الصفحة'
    jwt.init_app(app)
    
    # تسجيل المخططات
    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)
    
    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/auth')
    
    from .admin import admin as admin_blueprint
    app.register_blueprint(admin_blueprint, url_prefix='/admin')
    
    from .api import api as api_blueprint
    app.register_blueprint(api_blueprint, url_prefix='/api')
    
    from .projects import projects as projects_blueprint
    app.register_blueprint(projects_blueprint, url_prefix='/projects')
    
    from .castle_grok import castle_grok as castle_grok_blueprint
    app.register_blueprint(castle_grok_blueprint, url_prefix='/castle_grok')
    
    # إعداد معالجي الأخطاء
    @app.errorhandler(404)
    def page_not_found(e):
        return 'صفحة غير موجودة', 404

    @app.errorhandler(500)
    def internal_server_error(e):
        return 'خطأ في الخادم', 500
    
    # إنشاء قاعدة البيانات إذا لم تكن موجودة
    with app.app_context():
        db.create_all()
    
    return app