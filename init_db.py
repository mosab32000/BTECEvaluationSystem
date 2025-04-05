#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
هذا البرنامج يقوم بإنشاء قواعد البيانات المطلوبة لنظام تقييم BTEC
"""

import os
import sys
import logging
import secrets
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash

# تهيئة السجلات
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('db_init')

# تحميل متغيرات البيئة
load_dotenv()

# إضافة المجلد الحالي إلى مسار النظام
sys.path.append(os.path.dirname(__file__))

def ensure_environment_variables():
    """التأكد من وجود متغيرات البيئة الضرورية"""
    logger.info("التحقق من متغيرات البيئة...")
    
    # قائمة المتغيرات الضرورية
    required_vars = [
        "DATABASE_URL",
        "SECRET_KEY",
        "JWT_SECRET_KEY",
        "WTF_CSRF_SECRET_KEY",
        "ENCRYPTION_KEY"
    ]
    
    missing_vars = []
    for var in required_vars:
        if var not in os.environ:
            missing_vars.append(var)
    
    # إنشاء المتغيرات المفقودة
    if missing_vars:
        logger.warning(f"المتغيرات التالية مفقودة: {', '.join(missing_vars)}")
        for var in missing_vars:
            logger.info(f"إنشاء متغير {var} تلقائيًا...")
            ensure_secret_key(var)
    else:
        logger.info("جميع متغيرات البيئة اللازمة موجودة")

def ensure_encryption_key():
    """التأكد من وجود مفتاح التشفير، وإنشاء واحد جديد إذا لم يكن موجوداً"""
    if "ENCRYPTION_KEY" not in os.environ:
        # مفتاح تشفير يجب أن يكون بطول 32 بايت (256 بت)
        os.environ["ENCRYPTION_KEY"] = secrets.token_hex(16)
        logger.info("تم إنشاء مفتاح تشفير جديد")
        
        # حفظ المفتاح في ملف .env إذا كان موجوداً
        dotenv_file = os.path.join(os.path.dirname(__file__), '.env')
        if os.path.exists(dotenv_file):
            with open(dotenv_file, 'a') as f:
                f.write(f"\nENCRYPTION_KEY={os.environ['ENCRYPTION_KEY']}\n")
            logger.info("تم حفظ مفتاح التشفير في ملف .env")

def ensure_secret_key(env_var, length=32):
    """التأكد من وجود مفتاح سري، وإنشاء واحد جديد إذا لم يكن موجوداً"""
    if env_var not in os.environ:
        os.environ[env_var] = secrets.token_hex(length)
        logger.info(f"تم إنشاء {env_var} جديد")
        
        # حفظ المفتاح في ملف .env إذا كان موجوداً
        dotenv_file = os.path.join(os.path.dirname(__file__), '.env')
        if os.path.exists(dotenv_file):
            with open(dotenv_file, 'a') as f:
                f.write(f"\n{env_var}={os.environ[env_var]}\n")
            logger.info(f"تم حفظ {env_var} في ملف .env")

def create_default_admin():
    """إنشاء حساب مسؤول افتراضي إذا لم يكن موجوداً"""
    logger.info("التحقق من وجود حساب المسؤول الافتراضي...")
    
    from app import create_app, db
    from app.models.user import User
    
    app = create_app()
    with app.app_context():
        # التحقق من وجود مستخدم مسؤول
        admin = User.query.filter_by(role='admin').first()
        if admin:
            logger.info(f"حساب المسؤول موجود بالفعل: {admin.email}")
            return
        
        # إنشاء حساب المسؤول الافتراضي
        default_email = "admin@btec-eval.edu"
        default_name = "مصعب الحلحولي"
        default_password = "Btec@admin123"  # للتطوير فقط، يجب تغييره في بيئة الإنتاج
        
        admin_user = User(
            email=default_email,
            name=default_name,
            password_hash=generate_password_hash(default_password),
            role='admin',
            is_active=True
        )
        
        db.session.add(admin_user)
        db.session.commit()
        
        logger.info(f"تم إنشاء حساب المسؤول الافتراضي: {default_email}")
        logger.warning("يجب تغيير كلمة المرور الافتراضية في بيئة الإنتاج!")

def create_default_rubrics():
    """إنشاء قوالب معايير تقييم افتراضية"""
    logger.info("إنشاء قوالب معايير تقييم افتراضية...")
    
    from app import create_app, db
    from app.models.rubric import Rubric
    from app.models.user import User
    
    app = create_app()
    with app.app_context():
        # التحقق من وجود معايير تقييم
        if Rubric.query.count() > 0:
            logger.info("معايير التقييم موجودة بالفعل")
            return
        
        # الحصول على المستخدم المسؤول
        admin = User.query.filter_by(role='admin').first()
        if not admin:
            logger.error("لا يمكن إنشاء معايير التقييم: المستخدم المسؤول غير موجود")
            return
        
        # معيار تقييم BTEC الأساسي
        basic_rubric = Rubric(
            name="معيار تقييم BTEC الأساسي",
            description="معيار التقييم الأساسي للمهام وفق نظام BTEC",
            criteria={
                "التحليل": {
                    "description": "تحليل المفاهيم والأفكار والمعلومات",
                    "weight": 25
                },
                "التنفيذ": {
                    "description": "تنفيذ المهارات والتقنيات المطلوبة",
                    "weight": 25
                },
                "التقييم": {
                    "description": "تقييم المعلومات والأساليب والنتائج",
                    "weight": 25
                },
                "التوثيق": {
                    "description": "توثيق المصادر وتنظيم المعلومات",
                    "weight": 25
                }
            },
            max_score=100,
            created_by=admin.id
        )
        
        # معيار تقييم BTEC المتقدم
        advanced_rubric = Rubric(
            name="معيار تقييم BTEC المتقدم",
            description="معيار التقييم المتقدم للمهام وفق نظام BTEC",
            criteria={
                "التحليل": {
                    "description": "تحليل المفاهيم والأفكار والمعلومات بعمق",
                    "weight": 20
                },
                "التنفيذ": {
                    "description": "تنفيذ المهارات والتقنيات المطلوبة بدقة عالية",
                    "weight": 20
                },
                "التقييم": {
                    "description": "تقييم المعلومات والأساليب والنتائج بشكل نقدي",
                    "weight": 20
                },
                "الإبداع": {
                    "description": "إظهار مستوى عالٍ من الإبداع والابتكار",
                    "weight": 20
                },
                "التوثيق": {
                    "description": "توثيق المصادر وتنظيم المعلومات بشكل احترافي",
                    "weight": 20
                }
            },
            max_score=100,
            created_by=admin.id
        )
        
        db.session.add(basic_rubric)
        db.session.add(advanced_rubric)
        db.session.commit()
        
        logger.info("تم إنشاء قوالب معايير التقييم الافتراضية")

def create_default_courses():
    """إنشاء مساقات افتراضية"""
    logger.info("إنشاء مساقات افتراضية...")
    
    from app import create_app, db
    from app.models.course import Course
    from app.models.user import User
    
    app = create_app()
    with app.app_context():
        # التحقق من وجود مساقات
        if hasattr(Course, 'query') and Course.query.count() > 0:
            logger.info("المساقات موجودة بالفعل")
            return
        
        # الحصول على المستخدم المسؤول
        admin = User.query.filter_by(role='admin').first()
        if not admin:
            logger.error("لا يمكن إنشاء المساقات: المستخدم المسؤول غير موجود")
            return
        
        # قائمة المساقات الافتراضية
        default_courses = [
            {
                "code": "BTEC101",
                "name": "مقدمة في نظم المعلومات",
                "description": "مساق تمهيدي في نظم المعلومات وتطبيقاتها",
                "instructor_id": admin.id
            },
            {
                "code": "BTEC201",
                "name": "تطوير التطبيقات",
                "description": "مساق متوسط في تطوير تطبيقات الويب والموبايل",
                "instructor_id": admin.id
            },
            {
                "code": "BTEC301",
                "name": "إدارة المشاريع",
                "description": "مساق متقدم في إدارة المشاريع التقنية وتطبيقاتها",
                "instructor_id": admin.id
            }
        ]
        
        # إضافة المساقات إلى قاعدة البيانات
        for course_data in default_courses:
            course = Course(**course_data)
            db.session.add(course)
        
        db.session.commit()
        logger.info("تم إنشاء المساقات الافتراضية")

def setup_database():
    """إعداد وتهيئة قاعدة البيانات بالكامل"""
    logger.info("بدء تهيئة قاعدة البيانات لنظام تقييم BTEC...")
    
    # التأكد من وجود المتغيرات البيئية الضرورية
    ensure_environment_variables()
    
    # التأكد من وجود مفتاح التشفير
    ensure_encryption_key()
    
    # إنشاء قاعدة البيانات وجداولها
    from app import create_app, db
    
    app = create_app()
    with app.app_context():
        logger.info("إنشاء جداول قاعدة البيانات...")
        db.create_all()
        logger.info("تم إنشاء جداول قاعدة البيانات بنجاح")
    
    # إنشاء المستخدم المسؤول الافتراضي
    create_default_admin()
    
    # إنشاء قوالب معايير التقييم الافتراضية
    create_default_rubrics()
    
    # إنشاء المساقات الافتراضية
    create_default_courses()
    
    logger.info("اكتملت تهيئة قاعدة البيانات بنجاح")

if __name__ == "__main__":
    # إنشاء المجلدات الضرورية
    os.makedirs(os.path.join(os.path.dirname(__file__), 'logs'), exist_ok=True)
    os.makedirs(os.path.join(os.path.dirname(__file__), 'uploads'), exist_ok=True)
    os.makedirs(os.path.join(os.path.dirname(__file__), 'static', 'uploads'), exist_ok=True)
    
    # تهيئة قاعدة البيانات
    setup_database()