"""
ملف بداية تطبيق نظام تقييم BTEC
يقوم بإنشاء وتهيئة التطبيق
"""
import logging
import os
import sys
from datetime import datetime, timedelta
from logging.handlers import RotatingFileHandler

from flask import Flask, jsonify, render_template, request
from flask_jwt_extended import JWTManager
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from flask_talisman import Talisman
from flask_caching import Cache
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from sqlalchemy.orm import DeclarativeBase

# إعداد تسجيل الأحداث
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# إنشاء فئة أساسية للنماذج
class Base(DeclarativeBase):
    pass


# تهيئة امتدادات Flask
db = SQLAlchemy(model_class=Base)
jwt = JWTManager()
cache = Cache()
limiter = Limiter(key_func=get_remote_address)


def create_app(config_name='default'):
    """
    إنشاء وتكوين تطبيق Flask
    
    Args:
        config_name: اسم ملف التكوين المراد استخدامه
        
    Returns:
        Flask: تطبيق Flask
    """
    app = Flask(__name__, 
                static_folder="../static", 
                template_folder="../templates")
    
    # تحميل التكوين من الملف المناسب أو المتغيرات البيئية
    configure_app(app, config_name)
    
    # تهيئة امتدادات Flask
    init_extensions(app)
    
    # تسجيل المسارات
    register_blueprints(app)
    
    # تسجيل معالجات الأخطاء
    register_error_handlers(app)
    
    # تكوين التسجيل
    configure_logging(app)
    
    # تهيئة قاعدة البيانات
    with app.app_context():
        init_database()
    
    # مسارات النظام الأساسية
    @app.route('/health')
    def health():
        """
        فحص صحة النظام
        """
        try:
            # التحقق من الوصول إلى قاعدة البيانات
            db_status = False
            user_count = 0
            evaluation_count = 0
            
            try:
                from app.models.user import User
                from app.models.evaluation import Evaluation
                
                with app.app_context():
                    user_count = User.query.count()
                    evaluation_count = Evaluation.query.count()
                    db_status = True
            except Exception as e:
                logger.error(f"Database health check error: {e}")
            
            # نظام الذكاء الاصطناعي
            ai_status = False
            try:
                from app.core.ai_evaluator import AIEvaluator
                ai = AIEvaluator()
                ai_status = ai.client is not None
            except Exception as e:
                logger.error(f"AI health check error: {e}")
            
            # نظام البلوكتشين
            blockchain_status = False
            try:
                from app.core.blockchain_verifier import BlockchainVerifier
                blockchain = BlockchainVerifier()
                blockchain_status = blockchain.connected
            except Exception as e:
                logger.error(f"Blockchain health check error: {e}")
            
            # جمع المقاييس
            uptime = "Unknown"
            try:
                from app.database import get_metrics
                metrics = get_metrics()
            except Exception as e:
                logger.error(f"Metrics health check error: {e}")
                metrics = {}
            
            # إعداد استجابة الصحة
            health_data = {
                'status': 'ok' if db_status else 'degraded',
                'timestamp': datetime.utcnow().isoformat(),
                'version': os.environ.get('APP_VERSION', '1.0.0'),
                'components': {
                    'database': {
                        'status': 'ok' if db_status else 'error',
                        'details': {
                            'users': user_count,
                            'evaluations': evaluation_count
                        }
                    },
                    'ai': {
                        'status': 'ok' if ai_status else 'error',
                        'model': os.environ.get('OPENAI_MODEL', 'unknown')
                    },
                    'blockchain': {
                        'status': 'ok' if blockchain_status else 'disabled',
                        'network': os.environ.get('BLOCKCHAIN_NETWORK', 'none')
                    }
                },
                'metrics': metrics
            }
            
            return jsonify(health_data)
        except Exception as e:
            logger.error(f"Health check error: {e}")
            return jsonify({
                'status': 'error',
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }), 500

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
    # تكوين أساسي
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-key-CHANGE-ME-in-production')
    app.config['DEBUG'] = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    
    # تكوين قاعدة البيانات
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///btec.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        'pool_recycle': 300,
        'pool_pre_ping': True
    }
    
    # تكوين JWT
    app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', app.config['SECRET_KEY'])
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=1)
    app.config['JWT_REFRESH_TOKEN_EXPIRES'] = timedelta(days=30)
    app.config['JWT_BLACKLIST_ENABLED'] = True
    app.config['JWT_BLACKLIST_TOKEN_CHECKS'] = ['access', 'refresh']
    
    # تكوين التخزين المؤقت
    cache_type = os.environ.get('CACHE_TYPE', 'SimpleCache')
    cache_config = {'CACHE_TYPE': cache_type}
    
    if cache_type == 'RedisCache':
        cache_config['CACHE_REDIS_URL'] = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
        cache_config['CACHE_DEFAULT_TIMEOUT'] = 300
    
    app.config.update(cache_config)
    
    # تكوين محدد الطلبات
    app.config['RATELIMIT_DEFAULT'] = "200 per day, 50 per hour"
    app.config['RATELIMIT_STORAGE_URL'] = os.environ.get('REDIS_URL', 'memory://')
    app.config['RATELIMIT_STRATEGY'] = 'fixed-window'
    
    # تكوين الأمان
    app.config['TALISMAN_FORCE_HTTPS'] = os.environ.get('FORCE_HTTPS', 'False').lower() == 'true'
    app.config['TALISMAN_CONTENT_SECURITY_POLICY'] = {
        'default-src': "'self'",
        'style-src': ["'self'", "'unsafe-inline'", "fonts.googleapis.com"],
        'font-src': ["'self'", "fonts.gstatic.com"],
        'img-src': ["'self'", "data:"],
        'script-src': ["'self'", "'unsafe-inline'", "'unsafe-eval'"],
        'connect-src': ["'self'"]
    }


def init_extensions(app):
    """
    تهيئة امتدادات Flask
    
    Args:
        app: تطبيق Flask
    """
    # تهيئة امتداد قاعدة البيانات
    db.init_app(app)
    
    # تهيئة امتداد JWT
    jwt.init_app(app)
    
    # تهيئة امتداد التخزين المؤقت
    cache.init_app(app)
    
    # تهيئة امتداد محدد الطلبات
    limiter.init_app(app)
    
    # تهيئة امتداد Talisman (أمان الويب)
    if app.config.get('TALISMAN_FORCE_HTTPS', False):
        Talisman(app, 
                content_security_policy=app.config.get('TALISMAN_CONTENT_SECURITY_POLICY'),
                force_https=app.config.get('TALISMAN_FORCE_HTTPS', False))
    
    # تهيئة معالج حدث انتهاء صلاحية رمز JWT
    @jwt.token_in_blocklist_loader
    def check_if_token_is_revoked(jwt_header, jwt_payload):
        from app.routes.auth import check_if_token_is_revoked
        return check_if_token_is_revoked(jwt_header, jwt_payload)


def register_blueprints(app):
    """
    تسجيل جميع مسارات التطبيق
    
    Args:
        app: تطبيق Flask
    """
    # استيراد وتسجيل جميع المسارات
    from app.routes.auth import auth_bp
    from app.routes.evaluation import evaluation_bp
    
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
        logger.warning(f"Bad request: {error}")
        return jsonify({
            'status': 'error',
            'message': 'طلب غير صالح',
            'error': str(error)
        }), 400
    
    @app.errorhandler(401)
    def unauthorized(error):
        logger.warning(f"Unauthorized: {error}")
        return jsonify({
            'status': 'error',
            'message': 'غير مصرح',
            'error': str(error)
        }), 401
    
    @app.errorhandler(403)
    def forbidden(error):
        logger.warning(f"Forbidden: {error}")
        return jsonify({
            'status': 'error',
            'message': 'محظور',
            'error': str(error)
        }), 403
    
    @app.errorhandler(404)
    def not_found(error):
        logger.warning(f"Not found: {error}")
        return jsonify({
            'status': 'error',
            'message': 'غير موجود',
            'error': str(error)
        }), 404
    
    @app.errorhandler(500)
    def internal_server_error(error):
        logger.error(f"Internal server error: {error}")
        return jsonify({
            'status': 'error',
            'message': 'خطأ داخلي في الخادم',
            'error': str(error)
        }), 500


def configure_logging(app):
    """
    تكوين التسجيل
    
    Args:
        app: تطبيق Flask
    """
    if not app.debug:
        # إنشاء مجلد سجلات إذا لم يكن موجودًا
        logs_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs')
        if not os.path.exists(logs_dir):
            os.makedirs(logs_dir)
        
        # إعداد مُعالِج ملف دوار
        file_handler = RotatingFileHandler(
            os.path.join(logs_dir, 'btec.log'),
            maxBytes=1024 * 1024 * 10,  # 10 ميغابايت
            backupCount=5
        )
        
        # تكوين مُعالِج السجل
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(logging.INFO)
        
        # إضافة المُعالِج إلى التطبيق والسجل الجذر
        app.logger.addHandler(file_handler)
        app.logger.setLevel(logging.INFO)
        logging.getLogger().addHandler(file_handler)
        
        app.logger.info('BTEC Evaluation System startup')


def init_database():
    """
    تهيئة قاعدة البيانات وإنشاء الجداول الضرورية إذا لم تكن موجودة
    """
    try:
        # إنشاء الجداول
        db.create_all()
        
        # إنشاء المسؤول الافتراضي إذا لم يكن موجودًا
        create_default_admin()
        
        # إنشاء قوالب تقييم افتراضية
        create_default_rubrics()
        
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Database initialization error: {e}")


def create_default_admin():
    """
    إنشاء حساب مسؤول افتراضي إذا لم يكن موجودًا
    """
    try:
        from app.models.user import User
        from werkzeug.security import generate_password_hash
        
        # التحقق مما إذا كان هناك أي مسؤولين موجودين بالفعل
        admin_exists = User.query.filter_by(role='admin').first()
        
        if not admin_exists:
            # إنشاء مسؤول افتراضي
            admin_email = os.environ.get('ADMIN_EMAIL', 'admin@btec.edu')
            admin_password = os.environ.get('ADMIN_PASSWORD', 'Btec@12345')
            
            admin = User()
            admin.email = admin_email
            admin.password_hash = generate_password_hash(admin_password)
            admin.name = 'BTEC Admin'
            admin.role = 'admin'
            
            db.session.add(admin)
            db.session.commit()
            
            logger.info(f"Default admin created: {admin_email}")
    except Exception as e:
        logger.error(f"Error creating default admin: {e}")
        db.session.rollback()


def create_default_rubrics():
    """
    إنشاء قوالب معايير تقييم افتراضية
    """
    try:
        from app.models.rubric import RubricTemplate
        
        # التحقق مما إذا كان هناك أي قوالب موجودة بالفعل
        default_rubric_exists = RubricTemplate.query.filter_by(is_default=True).first()
        
        if not default_rubric_exists:
            # إنشاء قالب افتراضي لمعايير BTEC
            default_rubric = RubricTemplate()
            default_rubric.name = 'معايير BTEC الأساسية'
            default_rubric.description = 'قالب معايير BTEC القياسي للتقييم'
            default_rubric.is_default = True
            
            # إعداد معايير التقييم
            criteria = [
                {
                    'name': 'المعرفة والفهم',
                    'description': 'إظهار المعرفة والفهم للمفاهيم الرئيسية والمصطلحات والنظريات'
                },
                {
                    'name': 'التطبيق العملي',
                    'description': 'تطبيق المعرفة والمهارات في سياقات عملية وواقعية'
                },
                {
                    'name': 'البحث والتحليل',
                    'description': 'القدرة على البحث وتحليل المعلومات وتقييم المصادر'
                },
                {
                    'name': 'التفكير النقدي',
                    'description': 'تقييم الأفكار والحجج والمعلومات بشكل نقدي'
                },
                {
                    'name': 'المهارات التقنية',
                    'description': 'إظهار الكفاءة في استخدام الأدوات والتقنيات الخاصة بالمجال'
                },
                {
                    'name': 'الاتصال والعرض',
                    'description': 'توصيل الأفكار والمعلومات بشكل واضح ومنظم ومناسب للجمهور'
                }
            ]
            
            default_rubric.set_criteria(criteria)
            
            db.session.add(default_rubric)
            db.session.commit()
            
            logger.info(f"Default rubric template created: {default_rubric.name}")
    except Exception as e:
        logger.error(f"Error creating default rubrics: {e}")
        db.session.rollback()