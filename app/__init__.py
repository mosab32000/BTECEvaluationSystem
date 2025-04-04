"""
ملف بداية تطبيق نظام تقييم BTEC
يقوم بإنشاء وتهيئة التطبيق
"""
import os
import logging
from datetime import datetime, timedelta

from flask import Flask, jsonify, render_template, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask_login import LoginManager
from flask_caching import Cache
from flask_talisman import Talisman
from sqlalchemy.orm import DeclarativeBase

# إعداد التسجيل
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# تعريف قاعدة نماذج SQLAlchemy
class Base(DeclarativeBase):
    pass

# تهيئة الامتدادات
db = SQLAlchemy(model_class=Base)
migrate = Migrate()
jwt = JWTManager()
cors = CORS()
login_manager = LoginManager()
cache = Cache()

def create_app(config_name='default'):
    """
    إنشاء وتكوين تطبيق Flask
    
    Args:
        config_name: اسم ملف التكوين المراد استخدامه
        
    Returns:
        Flask: تطبيق Flask
    """
    app = Flask(__name__, static_folder='../static', template_folder='../templates')
    
    # تكوين التطبيق
    configure_app(app, config_name)
    
    # تهيئة الامتدادات
    init_extensions(app)
    
    # تسجيل مسارات التطبيق
    register_blueprints(app)
    
    # تسجيل معالجات الأخطاء
    register_error_handlers(app)
    
    # تكوين التسجيل
    configure_logging(app)
    
    # تهيئة قاعدة البيانات
    init_database()
    
    @app.route('/health')
    def health():
        """
        فحص صحة النظام
        """
        return jsonify(
            status='success',
            message='نظام تقييم BTEC يعمل بشكل جيد',
            timestamp=datetime.utcnow().isoformat()
        )
    
    @app.route('/')
    def home():
        """
        الصفحة الرئيسية
        """
        return render_template('index.html')
    
    return app

def configure_app(app, config_name):
    """
    تكوين التطبيق من المتغيرات البيئية أو ملفات التكوين
    
    Args:
        app: تطبيق Flask
        config_name: اسم ملف التكوين
    """
    # تكوين من المتغيرات البيئية
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev_secret_key')
    app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', app.config['SECRET_KEY'])
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///btec.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        'pool_recycle': 280,
        'pool_pre_ping': True
    }
    
    # تكوين JWT
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=1)
    app.config['JWT_REFRESH_TOKEN_EXPIRES'] = timedelta(days=30)
    app.config['JWT_BLACKLIST_ENABLED'] = True
    app.config['JWT_BLACKLIST_TOKEN_CHECKS'] = ['access', 'refresh']
    
    # تكوين Cache
    app.config['CACHE_TYPE'] = 'simple'
    app.config['CACHE_DEFAULT_TIMEOUT'] = 300
    
    # تكوين الرفع
    app.config['UPLOAD_FOLDER'] = os.environ.get('UPLOAD_FOLDER', 'uploads')
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB
    
    # تكوين OpenAI
    app.config['OPENAI_API_KEY'] = os.environ.get('OPENAI_API_KEY')
    app.config['OPENAI_MODEL'] = os.environ.get('OPENAI_MODEL', 'gpt-4')
    
    # تكوين البلوكتشين
    app.config['BLOCKCHAIN_ENABLED'] = os.environ.get('BLOCKCHAIN_ENABLED', 'False').lower() == 'true'
    app.config['INFURA_URL'] = os.environ.get('INFURA_URL')
    app.config['CONTRACT_ADDRESS'] = os.environ.get('CONTRACT_ADDRESS')
    app.config['SIGNER_PRIVATE_KEY'] = os.environ.get('SIGNER_PRIVATE_KEY')
    
    # تكوين التحقق من البريد الإلكتروني
    app.config['REQUIRE_EMAIL_VERIFICATION'] = os.environ.get('REQUIRE_EMAIL_VERIFICATION', 'False').lower() == 'true'
    app.config['MAIL_SERVER'] = os.environ.get('MAIL_SERVER')
    app.config['MAIL_PORT'] = int(os.environ.get('MAIL_PORT', 587))
    app.config['MAIL_USE_TLS'] = os.environ.get('MAIL_USE_TLS', 'True').lower() == 'true'
    app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
    app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
    app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('MAIL_DEFAULT_SENDER')
    
    # تكوين الأمان
    app.config['SECURITY_PASSWORD_SALT'] = os.environ.get('SECURITY_PASSWORD_SALT', 'btec_evaluation_system')
    app.config['ENCRYPTION_KEY'] = os.environ.get('ENCRYPTION_KEY')

def init_extensions(app):
    """
    تهيئة امتدادات Flask
    
    Args:
        app: تطبيق Flask
    """
    # تهيئة قاعدة البيانات
    db.init_app(app)
    migrate.init_app(app, db)
    
    # تهيئة JWT
    jwt.init_app(app)
    
    @jwt.token_in_blocklist_loader
    def check_if_token_is_revoked(jwt_header, jwt_payload):
        from app.models.user import BlacklistedToken
        jti = jwt_payload['jti']
        return BlacklistedToken.is_blacklisted(jti)
    
    # تهيئة CORS
    cors.init_app(app, resources={r"/api/*": {"origins": "*"}})
    
    # تهيئة Login
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'يرجى تسجيل الدخول للوصول إلى هذه الصفحة'
    
    @login_manager.user_loader
    def load_user(user_id):
        from app.models.user import User
        return User.query.get(int(user_id))
    
    # تهيئة Cache
    cache.init_app(app)
    
    # تهيئة Talisman (HTTPS)
    # تعطيل CSP مؤقتًا للتطوير
    talisman = Talisman(
        app,
        force_https=False,
        content_security_policy=None,
        x_content_type_options=True,
        strict_transport_security=True,
        strict_transport_security_preload=True,
        referrer_policy="strict-origin-when-cross-origin"
    )

def register_blueprints(app):
    """
    تسجيل جميع مسارات التطبيق
    
    Args:
        app: تطبيق Flask
    """
    # استيراد Blueprints
    from app.routes.auth import auth_bp
    from app.routes.evaluation import evaluation_bp
    
    # تسجيل Blueprints
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(evaluation_bp, url_prefix='/api/evaluations')

def register_error_handlers(app):
    """
    تسجيل معالجات الأخطاء
    
    Args:
        app: تطبيق Flask
    """
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify(
            status='error',
            message='طلب غير صالح',
            error=str(error)
        ), 400
    
    @app.errorhandler(401)
    def unauthorized(error):
        return jsonify(
            status='error',
            message='غير مصرح بالوصول',
            error=str(error)
        ), 401
    
    @app.errorhandler(403)
    def forbidden(error):
        return jsonify(
            status='error',
            message='غير مسموح بالوصول',
            error=str(error)
        ), 403
    
    @app.errorhandler(404)
    def not_found(error):
        return jsonify(
            status='error',
            message='الصفحة غير موجودة',
            error=str(error)
        ), 404
    
    @app.errorhandler(500)
    def internal_server_error(error):
        return jsonify(
            status='error',
            message='خطأ في الخادم',
            error=str(error)
        ), 500

def configure_logging(app):
    """
    تكوين التسجيل
    
    Args:
        app: تطبيق Flask
    """
    if not app.debug:
        # إضافة معالج ملف التسجيل
        import logging
        from logging.handlers import RotatingFileHandler
        import os
        
        if not os.path.exists('logs'):
            os.mkdir('logs')
        
        file_handler = RotatingFileHandler('logs/btec.log', maxBytes=10240, backupCount=10)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(logging.INFO)
        
        app.logger.addHandler(file_handler)
        app.logger.setLevel(logging.INFO)
        app.logger.info('بدء تشغيل نظام تقييم BTEC')

def init_database():
    """
    تهيئة قاعدة البيانات وإنشاء الجداول الضرورية إذا لم تكن موجودة
    """
    from app import db
    
    try:
        # إنشاء جميع الجداول
        db.create_all()
        logger.info("تم إنشاء/التحقق من جداول قاعدة البيانات")
        
        # إنشاء مسؤول افتراضي
        create_default_admin()
        
        # إنشاء معايير تقييم افتراضية
        create_default_rubrics()
        
    except Exception as e:
        logger.error(f"خطأ في تهيئة قاعدة البيانات: {str(e)}")

def create_default_admin():
    """
    إنشاء حساب مسؤول افتراضي إذا لم يكن موجودًا
    """
    from app.models.user import User
    from app import db
    
    try:
        # التحقق من وجود مسؤول
        admin_exists = User.query.filter_by(role='admin').first()
        
        if not admin_exists:
            # إنشاء مسؤول افتراضي
            admin = User()
            admin.name = 'مصعب الحلالة'
            admin.email = 'admin@btec.ps'
            admin.password = 'Admin@123456'  # يتم تجزئة كلمة المرور تلقائيًا
            admin.role = 'admin'
            admin.is_active = True
            admin.is_verified = True
            
            db.session.add(admin)
            db.session.commit()
            
            logger.info("تم إنشاء حساب المسؤول الافتراضي")
    
    except Exception as e:
        logger.error(f"خطأ في إنشاء حساب المسؤول الافتراضي: {str(e)}")
        db.session.rollback()

def create_default_rubrics():
    """
    إنشاء قوالب معايير تقييم افتراضية
    """
    from app.models.rubric import RubricTemplate
    from app import db
    
    try:
        # التحقق من وجود معايير تقييم
        rubrics_exist = RubricTemplate.query.first()
        
        if not rubrics_exist:
            # إنشاء معيار تقييم افتراضي - تقرير BTEC
            report_rubric = RubricTemplate()
            report_rubric.name = 'معيار تقييم تقرير BTEC'
            report_rubric.description = 'معيار تقييم شامل لتقارير BTEC'
            report_rubric.set_criteria([
                {
                    'name': 'البحث والتحليل',
                    'description': 'مدى عمق البحث وجودة التحليل',
                    'weight': 25,
                    'levels': [
                        {'name': 'ممتاز', 'score': 5, 'description': 'بحث شامل وتحليل عميق'},
                        {'name': 'جيد جدًا', 'score': 4, 'description': 'بحث جيد وتحليل مفصل'},
                        {'name': 'جيد', 'score': 3, 'description': 'بحث مقبول وتحليل كافٍ'},
                        {'name': 'مقبول', 'score': 2, 'description': 'بحث سطحي وتحليل محدود'},
                        {'name': 'ضعيف', 'score': 1, 'description': 'بحث غير كافٍ وتحليل ضعيف'}
                    ]
                },
                {
                    'name': 'التنظيم والهيكل',
                    'description': 'تنظيم المحتوى وهيكل التقرير',
                    'weight': 20,
                    'levels': [
                        {'name': 'ممتاز', 'score': 5, 'description': 'تنظيم ممتاز وهيكل متماسك'},
                        {'name': 'جيد جدًا', 'score': 4, 'description': 'تنظيم جيد وهيكل واضح'},
                        {'name': 'جيد', 'score': 3, 'description': 'تنظيم مقبول وهيكل مناسب'},
                        {'name': 'مقبول', 'score': 2, 'description': 'تنظيم غير متسق وهيكل غير واضح'},
                        {'name': 'ضعيف', 'score': 1, 'description': 'تنظيم ضعيف وهيكل مفكك'}
                    ]
                },
                {
                    'name': 'المحتوى والمعرفة',
                    'description': 'دقة المحتوى وعمق المعرفة',
                    'weight': 25,
                    'levels': [
                        {'name': 'ممتاز', 'score': 5, 'description': 'محتوى دقيق ومعرفة متعمقة'},
                        {'name': 'جيد جدًا', 'score': 4, 'description': 'محتوى جيد ومعرفة شاملة'},
                        {'name': 'جيد', 'score': 3, 'description': 'محتوى مقبول ومعرفة كافية'},
                        {'name': 'مقبول', 'score': 2, 'description': 'محتوى محدود ومعرفة سطحية'},
                        {'name': 'ضعيف', 'score': 1, 'description': 'محتوى غير دقيق ومعرفة غير كافية'}
                    ]
                },
                {
                    'name': 'التواصل والكتابة',
                    'description': 'وضوح التواصل وجودة الكتابة',
                    'weight': 15,
                    'levels': [
                        {'name': 'ممتاز', 'score': 5, 'description': 'تواصل واضح وكتابة ممتازة'},
                        {'name': 'جيد جدًا', 'score': 4, 'description': 'تواصل جيد وكتابة فعالة'},
                        {'name': 'جيد', 'score': 3, 'description': 'تواصل مقبول وكتابة مناسبة'},
                        {'name': 'مقبول', 'score': 2, 'description': 'تواصل محدود وكتابة ضعيفة'},
                        {'name': 'ضعيف', 'score': 1, 'description': 'تواصل غير واضح وكتابة سيئة'}
                    ]
                },
                {
                    'name': 'الابتكار والإبداع',
                    'description': 'مستوى الابتكار والإبداع في العمل',
                    'weight': 15,
                    'levels': [
                        {'name': 'ممتاز', 'score': 5, 'description': 'ابتكار استثنائي وإبداع متميز'},
                        {'name': 'جيد جدًا', 'score': 4, 'description': 'ابتكار ملحوظ وإبداع جيد'},
                        {'name': 'جيد', 'score': 3, 'description': 'بعض الابتكار والإبداع'},
                        {'name': 'مقبول', 'score': 2, 'description': 'ابتكار محدود وإبداع ضئيل'},
                        {'name': 'ضعيف', 'score': 1, 'description': 'افتقار للابتكار والإبداع'}
                    ]
                }
            ])
            
            # إنشاء معيار تقييم افتراضي - مشروع BTEC
            project_rubric = RubricTemplate()
            project_rubric.name = 'معيار تقييم مشروع BTEC'
            project_rubric.description = 'معيار تقييم شامل لمشاريع BTEC'
            project_rubric.set_criteria([
                {
                    'name': 'التخطيط والتنظيم',
                    'description': 'جودة التخطيط وتنظيم المشروع',
                    'weight': 20,
                    'levels': [
                        {'name': 'ممتاز', 'score': 5, 'description': 'تخطيط استراتيجي وتنظيم ممتاز'},
                        {'name': 'جيد جدًا', 'score': 4, 'description': 'تخطيط شامل وتنظيم جيد'},
                        {'name': 'جيد', 'score': 3, 'description': 'تخطيط مقبول وتنظيم كافٍ'},
                        {'name': 'مقبول', 'score': 2, 'description': 'تخطيط محدود وتنظيم غير متسق'},
                        {'name': 'ضعيف', 'score': 1, 'description': 'تخطيط ضعيف وتنظيم سيئ'}
                    ]
                },
                {
                    'name': 'التنفيذ والمهارات التقنية',
                    'description': 'جودة التنفيذ والمهارات التقنية المستخدمة',
                    'weight': 25,
                    'levels': [
                        {'name': 'ممتاز', 'score': 5, 'description': 'تنفيذ متقن ومهارات تقنية متميزة'},
                        {'name': 'جيد جدًا', 'score': 4, 'description': 'تنفيذ جيد ومهارات تقنية قوية'},
                        {'name': 'جيد', 'score': 3, 'description': 'تنفيذ مقبول ومهارات تقنية كافية'},
                        {'name': 'مقبول', 'score': 2, 'description': 'تنفيذ متوسط ومهارات تقنية محدودة'},
                        {'name': 'ضعيف', 'score': 1, 'description': 'تنفيذ ضعيف ومهارات تقنية غير كافية'}
                    ]
                },
                {
                    'name': 'الابتكار وحل المشكلات',
                    'description': 'الابتكار والقدرة على حل المشكلات',
                    'weight': 20,
                    'levels': [
                        {'name': 'ممتاز', 'score': 5, 'description': 'ابتكار استثنائي وحلول إبداعية للمشكلات'},
                        {'name': 'جيد جدًا', 'score': 4, 'description': 'ابتكار ملحوظ وحلول فعالة للمشكلات'},
                        {'name': 'جيد', 'score': 3, 'description': 'بعض الابتكار وحلول مقبولة للمشكلات'},
                        {'name': 'مقبول', 'score': 2, 'description': 'ابتكار محدود وحلول بسيطة للمشكلات'},
                        {'name': 'ضعيف', 'score': 1, 'description': 'افتقار للابتكار وحلول غير فعالة للمشكلات'}
                    ]
                },
                {
                    'name': 'تحقيق الأهداف',
                    'description': 'مدى تحقيق أهداف المشروع',
                    'weight': 20,
                    'levels': [
                        {'name': 'ممتاز', 'score': 5, 'description': 'تحقيق كامل لجميع الأهداف بتميز'},
                        {'name': 'جيد جدًا', 'score': 4, 'description': 'تحقيق معظم الأهداف بشكل جيد'},
                        {'name': 'جيد', 'score': 3, 'description': 'تحقيق الأهداف الرئيسية بشكل مقبول'},
                        {'name': 'مقبول', 'score': 2, 'description': 'تحقيق جزئي للأهداف'},
                        {'name': 'ضعيف', 'score': 1, 'description': 'فشل في تحقيق معظم الأهداف'}
                    ]
                },
                {
                    'name': 'التوثيق والعرض',
                    'description': 'جودة التوثيق والعرض التقديمي',
                    'weight': 15,
                    'levels': [
                        {'name': 'ممتاز', 'score': 5, 'description': 'توثيق شامل وعرض متميز'},
                        {'name': 'جيد جدًا', 'score': 4, 'description': 'توثيق جيد وعرض فعال'},
                        {'name': 'جيد', 'score': 3, 'description': 'توثيق مقبول وعرض مناسب'},
                        {'name': 'مقبول', 'score': 2, 'description': 'توثيق محدود وعرض ضعيف'},
                        {'name': 'ضعيف', 'score': 1, 'description': 'توثيق غير كافٍ وعرض سيئ'}
                    ]
                }
            ])
            
            # حفظ معايير التقييم
            db.session.add(report_rubric)
            db.session.add(project_rubric)
            db.session.commit()
            
            logger.info("تم إنشاء معايير التقييم الافتراضية")
    
    except Exception as e:
        logger.error(f"خطأ في إنشاء معايير التقييم الافتراضية: {str(e)}")
        db.session.rollback()