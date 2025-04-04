"""
ملف بداية تطبيق نظام تقييم BTEC
يقوم بإنشاء وتهيئة التطبيق
"""
import os
import logging
from datetime import timedelta
from pathlib import Path

from flask import Flask, Blueprint, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from sqlalchemy.orm import DeclarativeBase

# تكوين قاعدة البيانات
class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)
jwt = JWTManager()
migrate = Migrate()

def create_app(config_name='default'):
    """
    إنشاء وتكوين تطبيق Flask
    """
    app = Flask(__name__, 
                static_folder='../static',
                template_folder='../templates')
    
    # تكوين التطبيق استنادًا إلى البيئة المحددة
    app.config.from_object(f'app.config.{config_name.capitalize()}Config')
    
    # تهيئة قاعدة البيانات
    db.init_app(app)
    
    # تهيئة مكتبة JWT
    jwt.init_app(app)
    
    # تهيئة مكتبة الترحيل
    migrate.init_app(app, db)
    
    # تكوين CORS
    CORS(app, resources={r"/api/*": {"origins": app.config.get('ALLOWED_ORIGINS', '*')}})
    
    # تسجيل المسارات
    register_blueprints(app)
    
    # تكوين معالجات الأخطاء
    register_error_handlers(app)
    
    # تكوين التسجيل
    configure_logging(app)
    
    # تهيئة قاعدة البيانات (إنشاء الجداول)
    with app.app_context():
        try:
            init_database()
            logging.info("تم تهيئة قاعدة البيانات بنجاح")
        except Exception as e:
            logging.error(f"خطأ في تهيئة قاعدة البيانات: {str(e)}")
    
    # مسار للتحقق من صحة التطبيق
    @app.route('/health')
    def health():
        """
        فحص صحة النظام
        """
        return jsonify({
            'status': 'success',
            'message': 'BTEC Evaluation System is running'
        })
    
    # الصفحة الرئيسية
    @app.route('/')
    def home():
        """
        الصفحة الرئيسية
        """
        return app.send_static_file('index.html')
    
    return app

def register_blueprints(app):
    """
    تسجيل جميع مسارات التطبيق
    """
    # استيراد المسارات من وحدات المسارات
    try:
        # مسارات API
        from app.routes.auth import auth_bp
        from app.routes.evaluation import eval_bp
        from app.routes.admin import admin_bp
        from app.routes.frontend import frontend_bp
        
        # تجميع مسارات API
        api_bp = Blueprint('api', __name__, url_prefix='/api')
        api_bp.register_blueprint(auth_bp)
        api_bp.register_blueprint(eval_bp)
        api_bp.register_blueprint(admin_bp)
        
        # تسجيل المسارات
        app.register_blueprint(api_bp)
        app.register_blueprint(frontend_bp)
    except ImportError as e:
        logging.error(f"خطأ في استيراد وحدات المسارات: {str(e)}")

def register_error_handlers(app):
    """
    تسجيل معالجات الأخطاء
    """
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            'status': 'error',
            'message': 'طلب غير صحيح',
            'details': str(error)
        }), 400
    
    @app.errorhandler(401)
    def unauthorized(error):
        return jsonify({
            'status': 'error',
            'message': 'غير مصرح',
            'details': str(error)
        }), 401
    
    @app.errorhandler(403)
    def forbidden(error):
        return jsonify({
            'status': 'error',
            'message': 'محظور',
            'details': str(error)
        }), 403
    
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'status': 'error',
            'message': 'غير موجود',
            'details': str(error)
        }), 404
    
    @app.errorhandler(500)
    def internal_server_error(error):
        return jsonify({
            'status': 'error',
            'message': 'خطأ داخلي في الخادم',
            'details': str(error)
        }), 500

def configure_logging(app):
    """
    تكوين التسجيل
    """
    log_level = app.config.get('LOG_LEVEL', logging.INFO)
    log_format = '%(asctime)s [%(levelname)s] - %(message)s'
    
    # إنشاء مجلد السجلات إذا لم يكن موجودًا
    log_dir = Path('logs')
    log_dir.mkdir(exist_ok=True)
    
    # تكوين التسجيل
    logging.basicConfig(
        level=log_level,
        format=log_format,
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('logs/app.log')
        ]
    )

def init_database():
    """
    تهيئة قاعدة البيانات وإنشاء الجداول الضرورية إذا لم تكن موجودة
    """
    # إنشاء الجداول
    db.create_all()
    
    # إنشاء حساب مسؤول افتراضي إذا لم يكن موجودًا
    create_default_admin()
    
    # إنشاء قوالب معايير تقييم افتراضية
    create_default_rubrics()

def create_default_admin():
    """
    إنشاء حساب مسؤول افتراضي إذا لم يكن موجودًا
    """
    from app.models.user import User
    from werkzeug.security import generate_password_hash
    
    # التحقق مما إذا كان هناك حساب مسؤول موجود بالفعل
    admin = User.query.filter_by(role='admin').first()
    if not admin:
        # إنشاء حساب المسؤول
        default_admin = User(
            name="مسؤول النظام",
            email="admin@btec-eval.com",
            password_hash=generate_password_hash("admin123"),
            role="admin",
            is_active=True
        )
        db.session.add(default_admin)
        db.session.commit()
        logging.info("تم إنشاء حساب المسؤول الافتراضي")

def create_default_rubrics():
    """
    إنشاء قوالب معايير تقييم افتراضية
    """
    from app.models.rubric import Rubric
    
    # التحقق مما إذا كانت هناك معايير تقييم موجودة بالفعل
    rubric_count = Rubric.query.count()
    if rubric_count == 0:
        # إنشاء معايير التقييم الافتراضية
        default_rubrics = [
            Rubric(
                name="معيار التقييم BTEC العام",
                description="معيار تقييم عام لمهام BTEC",
                criteria={
                    "content": {
                        "title": "المحتوى",
                        "weight": 0.4,
                        "description": "مدى اكتمال وجودة المحتوى المقدم"
                    },
                    "analysis": {
                        "title": "التحليل",
                        "weight": 0.3,
                        "description": "مستوى التحليل والتفكير النقدي"
                    },
                    "presentation": {
                        "title": "العرض والتنسيق",
                        "weight": 0.2,
                        "description": "جودة العرض والتنسيق والهيكل"
                    },
                    "research": {
                        "title": "البحث",
                        "weight": 0.1,
                        "description": "جودة المصادر والبحث"
                    }
                }
            ),
            Rubric(
                name="معيار تقييم المشاريع التقنية",
                description="معيار لتقييم المشاريع التقنية في BTEC",
                criteria={
                    "functionality": {
                        "title": "الوظائف",
                        "weight": 0.35,
                        "description": "مدى نجاح المشروع في تنفيذ الوظائف المطلوبة"
                    },
                    "code_quality": {
                        "title": "جودة الكود",
                        "weight": 0.25,
                        "description": "جودة وكفاءة الكود البرمجي"
                    },
                    "documentation": {
                        "title": "التوثيق",
                        "weight": 0.2,
                        "description": "جودة واكتمال توثيق المشروع"
                    },
                    "testing": {
                        "title": "الاختبار",
                        "weight": 0.1,
                        "description": "مدى شمولية ودقة اختبارات المشروع"
                    },
                    "presentation": {
                        "title": "العرض",
                        "weight": 0.1,
                        "description": "جودة عرض المشروع وتقديمه"
                    }
                }
            )
        ]
        
        # إضافة المعايير إلى قاعدة البيانات
        for rubric in default_rubrics:
            db.session.add(rubric)
        
        db.session.commit()
        logging.info(f"تم إنشاء {len(default_rubrics)} من معايير التقييم الافتراضية")
