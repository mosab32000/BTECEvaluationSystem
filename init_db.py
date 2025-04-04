"""
هذا البرنامج يقوم بإنشاء قواعد البيانات المطلوبة لنظام تقييم BTEC
"""
import os
import sys
import logging
import base64
import secrets
from datetime import datetime

from cryptography.fernet import Fernet
from werkzeug.security import generate_password_hash

# تكوين التسجيل
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def ensure_encryption_key():
    """التأكد من وجود مفتاح التشفير، وإنشاء واحد جديد إذا لم يكن موجودًا"""
    if not os.environ.get('ENCRYPTION_KEY'):
        # إنشاء مفتاح تشفير جديد
        key = Fernet.generate_key()
        with open('.env', 'a') as f:
            f.write(f'\nENCRYPTION_KEY={key.decode()}\n')
        os.environ['ENCRYPTION_KEY'] = key.decode()
        logging.info("تم إنشاء مفتاح تشفير جديد وإضافته إلى ملف .env")

def ensure_secret_key(env_var, length=32):
    """التأكد من وجود مفتاح سري، وإنشاء واحد جديد إذا لم يكن موجودًا"""
    if not os.environ.get(env_var):
        # إنشاء مفتاح سري جديد
        key = secrets.token_hex(length)
        with open('.env', 'a') as f:
            f.write(f'\n{env_var}={key}\n')
        os.environ[env_var] = key
        logging.info(f"تم إنشاء مفتاح سري جديد لـ {env_var} وإضافته إلى ملف .env")

def create_default_admin():
    """إنشاء حساب مسؤول افتراضي إذا لم يكن موجودًا"""
    from app import db, create_app
    from app.models.user import User
    
    app = create_app()
    
    with app.app_context():
        # التحقق مما إذا كان هناك مسؤول رئيسي موجود بالفعل
        admin = User.query.filter_by(email='admin@btec-eval.com').first()
        
        if admin:
            logging.info(f"المسؤول الرئيسي موجود بالفعل: {admin.email}")
            return
        
        # إنشاء المسؤول الرئيسي
        admin = User(
            name="مصعب الحلالة",
            email="admin@btec-eval.com",
            password_hash=generate_password_hash("admin123"),
            role="admin",
            is_active=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        try:
            # حفظ المسؤول في قاعدة البيانات
            db.session.add(admin)
            db.session.commit()
            logging.info(f"تم إنشاء المسؤول الرئيسي بنجاح: {admin.email}")
        except Exception as e:
            db.session.rollback()
            logging.error(f"خطأ في إنشاء المسؤول الرئيسي: {str(e)}")

def create_default_rubrics():
    """إنشاء قوالب معايير تقييم افتراضية"""
    from app import db, create_app
    from app.models.rubric import Rubric
    
    app = create_app()
    
    with app.app_context():
        # التحقق مما إذا كانت هناك معايير تقييم موجودة بالفعل
        rubric_count = Rubric.query.count()
        
        if rubric_count > 0:
            logging.info(f"معايير التقييم الافتراضية موجودة بالفعل: {rubric_count} معيار")
            return
        
        # إنشاء معايير التقييم الافتراضية
        default_rubrics = [
            Rubric(
                name="معيار التقييم العام للمهام",
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
                },
                is_default=True,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            ),
            Rubric(
                name="معيار تقييم مشاريع البرمجة",
                description="معيار لتقييم مشاريع البرمجة والتطوير في BTEC",
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
                    "design": {
                        "title": "التصميم",
                        "weight": 0.1,
                        "description": "جودة تصميم واجهة المستخدم والبنية العامة"
                    }
                },
                is_default=True,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            ),
            Rubric(
                name="معيار تقييم عروض المشاريع",
                description="معيار لتقييم عروض المشاريع التقديمية في BTEC",
                criteria={
                    "content": {
                        "title": "المحتوى",
                        "weight": 0.3,
                        "description": "جودة واكتمال محتوى العرض"
                    },
                    "delivery": {
                        "title": "الإلقاء",
                        "weight": 0.3,
                        "description": "جودة الإلقاء والتواصل مع الجمهور"
                    },
                    "visual_aids": {
                        "title": "الوسائل البصرية",
                        "weight": 0.2,
                        "description": "جودة الشرائح والوسائل البصرية المستخدمة"
                    },
                    "time_management": {
                        "title": "إدارة الوقت",
                        "weight": 0.1,
                        "description": "مدى الالتزام بالوقت المخصص وتوزيعه بفعالية"
                    },
                    "qa_handling": {
                        "title": "التعامل مع الأسئلة",
                        "weight": 0.1,
                        "description": "مدى فعالية التعامل مع أسئلة الجمهور والمناقشة"
                    }
                },
                is_default=True,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
        ]
        
        try:
            # حفظ معايير التقييم في قاعدة البيانات
            for rubric in default_rubrics:
                db.session.add(rubric)
            
            db.session.commit()
            logging.info(f"تم إنشاء {len(default_rubrics)} من معايير التقييم الافتراضية")
        except Exception as e:
            db.session.rollback()
            logging.error(f"خطأ في إنشاء معايير التقييم الافتراضية: {str(e)}")

def setup_database():
    """إعداد وتهيئة قاعدة البيانات بالكامل"""
    from app import db, create_app
    
    # التأكد من وجود المفاتيح السرية
    ensure_secret_key('SECRET_KEY')
    ensure_secret_key('JWT_SECRET_KEY')
    ensure_encryption_key()
    
    # تحميل متغيرات البيئة
    from dotenv import load_dotenv
    load_dotenv()
    
    # إنشاء تطبيق Flask والسياق
    app = create_app()
    
    with app.app_context():
        try:
            # إنشاء جداول قاعدة البيانات
            db.create_all()
            logging.info("تم إنشاء جداول قاعدة البيانات بنجاح")
            
            # إنشاء البيانات الافتراضية
            create_default_admin()
            create_default_rubrics()
            
            logging.info("تم إعداد قاعدة البيانات بنجاح!")
        except Exception as e:
            logging.error(f"خطأ في إعداد قاعدة البيانات: {str(e)}")
            sys.exit(1)

if __name__ == "__main__":
    setup_database()