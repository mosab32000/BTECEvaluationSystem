"""
هذا البرنامج يقوم بإنشاء قواعد البيانات المطلوبة لنظام تقييم BTEC
"""

import os
import sys
from flask_migrate import Migrate, init, migrate, upgrade
from dotenv import load_dotenv
import logging
import base64
from cryptography.fernet import Fernet

# تكوين التسجيل
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# تحميل متغيرات البيئة
load_dotenv()

# استيراد التطبيق ونماذج قاعدة البيانات
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
from backend.app import create_app
from backend.app.database import db
from backend.app.models import User, Evaluation, RubricTemplate, SystemMetrics

def ensure_encryption_key():
    """التأكد من وجود مفتاح التشفير، وإنشاء واحد جديد إذا لم يكن موجودًا"""
    if not os.environ.get('ENCRYPTION_KEY'):
        logger.info("إنشاء مفتاح تشفير جديد...")
        key = Fernet.generate_key()
        with open('.env', 'a') as f:
            f.write(f"\nENCRYPTION_KEY={key.decode()}\n")
        logger.info("تم إنشاء مفتاح التشفير وحفظه في ملف .env")
        # تحديث متغيرات البيئة الحالية
        os.environ['ENCRYPTION_KEY'] = key.decode()
        return key.decode()
    return os.environ.get('ENCRYPTION_KEY')

def ensure_secret_key(env_var, length=32):
    """التأكد من وجود مفتاح سري، وإنشاء واحد جديد إذا لم يكن موجودًا"""
    if not os.environ.get(env_var):
        logger.info(f"إنشاء {env_var} جديد...")
        import secrets
        secret_key = secrets.token_hex(length)
        with open('.env', 'a') as f:
            f.write(f"\n{env_var}={secret_key}\n")
        logger.info(f"تم إنشاء {env_var} وحفظه في ملف .env")
        # تحديث متغيرات البيئة الحالية
        os.environ[env_var] = secret_key
        return secret_key
    return os.environ.get(env_var)

def create_default_admin():
    """إنشاء حساب مسؤول افتراضي إذا لم يكن موجودًا"""
    from backend.app.models import User
    admin_email = "admin@btec.edu"
    
    with app.app_context():
        if not User.query.filter_by(email=admin_email).first():
            logger.info("إنشاء حساب المسؤول الافتراضي...")
            admin = User(email=admin_email, role='admin', name='BTEC System Admin')
            admin.set_password("admin12345")  # كلمة مرور مؤقتة يجب تغييرها
            db.session.add(admin)
            db.session.commit()
            logger.info(f"تم إنشاء حساب المسؤول: {admin_email}")
            logger.warning("يرجى تغيير كلمة المرور الافتراضية!")
        else:
            logger.info("حساب المسؤول موجود بالفعل.")

def create_default_rubrics():
    """إنشاء قوالب معايير تقييم افتراضية"""
    with app.app_context():
        admin = User.query.filter_by(role='admin').first()
        
        if not admin:
            logger.error("لم يتم العثور على مسؤول لإنشاء قوالب المعايير!")
            return
            
        if RubricTemplate.query.filter_by(is_default=True).count() == 0:
            logger.info("إنشاء قوالب معايير التقييم الافتراضية...")
            
            default_rubric = {
                "sections": [
                    {
                        "name": "الفهم والتحليل",
                        "weight": 25,
                        "criteria": [
                            "فهم عميق لمتطلبات المهمة",
                            "قدرة على تحليل المشكلة أو السؤال",
                            "تطبيق المفاهيم النظرية بشكل صحيح"
                        ]
                    },
                    {
                        "name": "التنفيذ والمهارات العملية",
                        "weight": 35,
                        "criteria": [
                            "إظهار المهارات العملية المطلوبة",
                            "اتباع الإجراءات الصحيحة",
                            "استخدام الأدوات والتقنيات بشكل مناسب",
                            "الدقة في التنفيذ"
                        ]
                    },
                    {
                        "name": "البحث والاستدلال",
                        "weight": 20,
                        "criteria": [
                            "استخدام مصادر متنوعة وموثوقة",
                            "الاستدلال المنطقي",
                            "تقديم الأدلة المناسبة"
                        ]
                    },
                    {
                        "name": "التواصل والعرض",
                        "weight": 20,
                        "criteria": [
                            "وضوح العرض والتنسيق",
                            "استخدام اللغة المهنية المناسبة",
                            "تنظيم الأفكار بشكل منطقي",
                            "الالتزام بإرشادات التوثيق"
                        ]
                    }
                ]
            }
            
            technical_rubric = {
                "sections": [
                    {
                        "name": "الأساسيات التقنية",
                        "weight": 30,
                        "criteria": [
                            "فهم المبادئ الأساسية للموضوع",
                            "تطبيق المفاهيم التقنية بشكل صحيح",
                            "استخدام المصطلحات التقنية بدقة"
                        ]
                    },
                    {
                        "name": "حل المشكلات",
                        "weight": 35,
                        "criteria": [
                            "تحديد المشكلة بشكل صحيح",
                            "تطوير حلول منهجية",
                            "تقييم البدائل",
                            "تنفيذ الحل الأمثل"
                        ]
                    },
                    {
                        "name": "التوثيق والعرض",
                        "weight": 20,
                        "criteria": [
                            "توثيق العمليات بشكل صحيح",
                            "شرح الخطوات المتبعة بوضوح",
                            "تقديم الأدلة بطريقة منظمة"
                        ]
                    },
                    {
                        "name": "التفكير النقدي",
                        "weight": 15,
                        "criteria": [
                            "تقييم نقدي للحلول",
                            "تحديد نقاط القوة والضعف",
                            "اقتراح تحسينات"
                        ]
                    }
                ]
            }
            
            # إنشاء قالب المعيار الافتراضي
            default_template = RubricTemplate(
                name="معيار BTEC العام",
                description="معيار تقييم عام لمهام BTEC",
                is_default=True,
                created_by=admin.id
            )
            default_template.set_rubric_data(default_rubric)
            
            # إنشاء قالب المعيار التقني
            tech_template = RubricTemplate(
                name="معيار BTEC التقني",
                description="معيار تقييم للمهام التقنية",
                is_default=False,
                created_by=admin.id
            )
            tech_template.set_rubric_data(technical_rubric)
            
            db.session.add(default_template)
            db.session.add(tech_template)
            db.session.commit()
            
            logger.info("تم إنشاء قوالب معايير التقييم الافتراضية.")
        else:
            logger.info("قوالب معايير التقييم الافتراضية موجودة بالفعل.")

def setup_database():
    """إعداد وتهيئة قاعدة البيانات بالكامل"""
    logger.info("بدء إعداد قاعدة البيانات...")
    
    # التأكد من وجود المفاتيح السرية
    ensure_secret_key('SECRET_KEY')
    ensure_secret_key('JWT_SECRET_KEY')
    ensure_encryption_key()
    
    try:
        # إنشاء مجلد الهجرات إذا لم يكن موجودًا
        migrations_dir = os.path.join('migrations')
        os.makedirs(migrations_dir, exist_ok=True)
        
        with app.app_context():
            # تهيئة قاعدة البيانات
            db.create_all()
            logger.info("تم إنشاء جداول قاعدة البيانات بنجاح.")
            
            # إنشاء المسؤول الافتراضي
            create_default_admin()
            
            # إنشاء قوالب المعايير الافتراضية
            create_default_rubrics()
            
        logger.info("تم إعداد قاعدة البيانات بنجاح!")
        return True
    except Exception as e:
        logger.error(f"حدث خطأ أثناء إعداد قاعدة البيانات: {e}")
        return False

if __name__ == "__main__":
    # إنشاء تطبيق Flask
    app = create_app()
    
    if setup_database():
        logger.info("تم تهيئة قاعدة البيانات بنجاح. النظام جاهز للاستخدام.")
        sys.exit(0)
    else:
        logger.error("فشل في إعداد قاعدة البيانات.")
        sys.exit(1)