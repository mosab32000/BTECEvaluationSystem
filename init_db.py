"""
هذا البرنامج يقوم بإنشاء قواعد البيانات المطلوبة لنظام تقييم BTEC
"""
import os
import logging
import base64
import json
from dotenv import load_dotenv
from backend.app import create_app
from backend.app.database import db
from backend.app.models.user import User
from backend.app.models.rubric import RubricTemplate
from werkzeug.security import generate_password_hash

# إعداد التسجيل
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def ensure_encryption_key():
    """التأكد من وجود مفتاح التشفير، وإنشاء واحد جديد إذا لم يكن موجودًا"""
    if not os.environ.get('ENCRYPTION_KEY'):
        # إنشاء مفتاح فيرنت جديد وتحويله إلى base64
        from cryptography.fernet import Fernet
        key = Fernet.generate_key()
        key_str = key.decode('utf-8')
        
        # تحديث ملف .env
        with open('.env', 'r') as f:
            lines = f.readlines()
            
        with open('.env', 'w') as f:
            for line in lines:
                if line.startswith('ENCRYPTION_KEY='):
                    f.write(f'ENCRYPTION_KEY={key_str}\n')
                else:
                    f.write(line)
        
        os.environ['ENCRYPTION_KEY'] = key_str
        logger.info("تم إنشاء مفتاح تشفير جديد وتخزينه")
    else:
        logger.info("مفتاح التشفير موجود بالفعل")

def ensure_secret_key(env_var, length=32):
    """التأكد من وجود مفتاح سري، وإنشاء واحد جديد إذا لم يكن موجودًا"""
    if not os.environ.get(env_var):
        import secrets
        key = secrets.token_hex(length)
        
        # تحديث ملف .env
        with open('.env', 'r') as f:
            lines = f.readlines()
            
        with open('.env', 'w') as f:
            for line in lines:
                if line.startswith(f'{env_var}='):
                    f.write(f'{env_var}={key}\n')
                else:
                    f.write(line)
        
        os.environ[env_var] = key
        logger.info(f"تم إنشاء مفتاح {env_var} جديد وتخزينه")
    else:
        logger.info(f"مفتاح {env_var} موجود بالفعل")

def create_default_admin():
    """إنشاء حساب مسؤول افتراضي إذا لم يكن موجودًا"""
    from create_admin import create_main_admin
    if create_main_admin():
        logger.info("تم إنشاء حساب المسؤول الرئيسي بنجاح")
    else:
        logger.info("حساب المسؤول الرئيسي موجود بالفعل")

def create_default_rubrics():
    """إنشاء قوالب معايير تقييم افتراضية"""
    try:
        # التحقق مما إذا كانت هناك قوالب موجودة بالفعل
        if RubricTemplate.query.filter_by(is_default=True).first():
            logger.info("قوالب المعايير الافتراضية موجودة بالفعل")
            return True
        
        # إنشاء قالب معايير BTEC الافتراضي
        btec_rubric = {
            "criteria": [
                {
                    "name": "فهم المفاهيم",
                    "description": "فهم المفاهيم الأساسية والمتقدمة",
                    "weight": 0.25,
                    "levels": [
                        {"name": "ممتاز", "score": 4, "description": "فهم ممتاز للمفاهيم المعقدة"},
                        {"name": "جيد جداً", "score": 3, "description": "فهم واضح لمعظم المفاهيم"},
                        {"name": "جيد", "score": 2, "description": "فهم أساسي مع بعض الفجوات"},
                        {"name": "مقبول", "score": 1, "description": "فهم محدود للمفاهيم الأساسية"}
                    ]
                },
                {
                    "name": "تطبيق المهارات",
                    "description": "القدرة على تطبيق المهارات العملية",
                    "weight": 0.25,
                    "levels": [
                        {"name": "ممتاز", "score": 4, "description": "تطبيق متقن للمهارات في حالات معقدة"},
                        {"name": "جيد جداً", "score": 3, "description": "تطبيق فعال للمهارات بشكل عام"},
                        {"name": "جيد", "score": 2, "description": "تطبيق أساسي مع أخطاء بسيطة"},
                        {"name": "مقبول", "score": 1, "description": "صعوبة في تطبيق المهارات الأساسية"}
                    ]
                },
                {
                    "name": "التحليل والتقييم",
                    "description": "القدرة على تحليل المعلومات وتقييمها",
                    "weight": 0.25,
                    "levels": [
                        {"name": "ممتاز", "score": 4, "description": "تحليل وتقييم شامل ومتعمق"},
                        {"name": "جيد جداً", "score": 3, "description": "تحليل جيد مع بعض الاستنتاجات"},
                        {"name": "جيد", "score": 2, "description": "تحليل أساسي مع تقييم محدود"},
                        {"name": "مقبول", "score": 1, "description": "تحليل سطحي مع ضعف في التقييم"}
                    ]
                },
                {
                    "name": "عرض وتواصل",
                    "description": "جودة العرض والتواصل",
                    "weight": 0.25,
                    "levels": [
                        {"name": "ممتاز", "score": 4, "description": "عرض منظم واضح مع تواصل فعال"},
                        {"name": "جيد جداً", "score": 3, "description": "عرض منظم مع تواصل جيد بشكل عام"},
                        {"name": "جيد", "score": 2, "description": "عرض مفهوم مع بعض مشاكل التواصل"},
                        {"name": "مقبول", "score": 1, "description": "عرض غير منظم مع ضعف في التواصل"}
                    ]
                }
            ]
        }
        
        # الحصول على معرف المسؤول (إذا كان موجودًا)
        admin = User.query.filter_by(role='admin').first()
        admin_id = admin.id if admin else None
        
        # إنشاء قالب معايير BTEC
        btec_template = RubricTemplate(
            name="معايير تقييم BTEC الافتراضية",
            description="قالب افتراضي لتقييم مهام BTEC بناءً على معايير BTEC القياسية",
            content=json.dumps(btec_rubric, ensure_ascii=False),
            is_default=True,
            created_by=admin_id
        )
        
        db.session.add(btec_template)
        db.session.commit()
        
        logger.info("تم إنشاء قوالب المعايير الافتراضية بنجاح")
        return True
    except Exception as e:
        logger.error(f"خطأ أثناء إنشاء قوالب المعايير الافتراضية: {e}")
        return False

def setup_database():
    """إعداد وتهيئة قاعدة البيانات بالكامل"""
    try:
        # تحميل متغيرات البيئة
        load_dotenv()
        
        # التأكد من وجود مفاتيح الأمان
        ensure_secret_key('SECRET_KEY')
        ensure_secret_key('JWT_SECRET_KEY')
        ensure_encryption_key()
        
        # إنشاء تطبيق Flask مع مع سياق التطبيق
        app = create_app()
        with app.app_context():
            # إنشاء جداول قاعدة البيانات
            db.create_all()
            logger.info("تم إنشاء جداول قاعدة البيانات بنجاح")
            
            # إنشاء المسؤول الافتراضي
            create_default_admin()
            
            # إنشاء قوالب المعايير الافتراضية
            create_default_rubrics()
            
            logger.info("اكتمل إعداد قاعدة البيانات بنجاح")
        
        return True
    except Exception as e:
        logger.error(f"خطأ أثناء إعداد قاعدة البيانات: {e}")
        return False

if __name__ == "__main__":
    setup_database()