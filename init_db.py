"""
هذا البرنامج يقوم بإنشاء قواعد البيانات المطلوبة لنظام تقييم BTEC
"""
import os
import logging
import secrets
from datetime import datetime
from werkzeug.security import generate_password_hash
from flask.cli import with_appcontext
from flask import current_app
import click

# إعداد التسجيل
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def ensure_encryption_key():
    """التأكد من وجود مفتاح التشفير، وإنشاء واحد جديد إذا لم يكن موجوداً"""
    env_file = '.env'
    key_name = 'ENCRYPTION_KEY'
    
    # قراءة ملف .env إذا كان موجوداً
    env_vars = {}
    if os.path.exists(env_file):
        with open(env_file, 'r') as f:
            for line in f:
                if '=' in line:
                    key, value = line.strip().split('=', 1)
                    env_vars[key] = value
    
    # التحقق من وجود ENCRYPTION_KEY
    if key_name not in env_vars:
        # إنشاء مفتاح تشفير جديد (32 بايت مشفرة بـ hex)
        encryption_key = secrets.token_hex(32)
        
        # إضافة المفتاح إلى ملف .env
        with open(env_file, 'a') as f:
            f.write(f'\n{key_name}={encryption_key}\n')
        
        logger.info(f"تم إنشاء {key_name} جديد")
        
        # تحديث متغير البيئة
        os.environ[key_name] = encryption_key
    else:
        logger.info(f"{key_name} موجود بالفعل")

def ensure_secret_key(env_var, length=32):
    """التأكد من وجود مفتاح سري، وإنشاء واحد جديد إذا لم يكن موجوداً"""
    env_file = '.env'
    
    # قراءة ملف .env إذا كان موجوداً
    env_vars = {}
    if os.path.exists(env_file):
        with open(env_file, 'r') as f:
            for line in f:
                if '=' in line:
                    key, value = line.strip().split('=', 1)
                    env_vars[key] = value
    
    # التحقق من وجود المفتاح المطلوب
    if env_var not in env_vars:
        # إنشاء مفتاح جديد
        secret_key = secrets.token_hex(length)
        
        # إضافة المفتاح إلى ملف .env
        with open(env_file, 'a') as f:
            f.write(f'\n{env_var}={secret_key}\n')
        
        logger.info(f"تم إنشاء {env_var} جديد")
        
        # تحديث متغير البيئة
        os.environ[env_var] = secret_key
    else:
        logger.info(f"{env_var} موجود بالفعل")

def create_default_admin():
    """إنشاء حساب مسؤول افتراضي إذا لم يكن موجوداً"""
    from app import db
    from app.models.user import User
    
    # التحقق مما إذا كان هناك أي مستخدمين بالفعل
    admin_email = current_app.config.get('ADMIN_EMAIL', 'admin@btec-eval.com')
    admin = User.query.filter_by(email=admin_email).first()
    
    if admin:
        logger.info(f"المسؤول {admin_email} موجود بالفعل")
        return
    
    # إنشاء مستخدم مسؤول جديد
    default_password = current_app.config.get('DEFAULT_ADMIN_PASSWORD', 'defaultadmin2025')
    
    admin = User(
        email=admin_email,
        name='مصعب الحلالة - المدير',
        role='admin',
        created_at=datetime.utcnow(),
        password_hash=generate_password_hash(default_password)
    )
    
    try:
        db.session.add(admin)
        db.session.commit()
        logger.info(f"تم إنشاء المسؤول {admin_email} بنجاح")
    except Exception as e:
        db.session.rollback()
        logger.error(f"فشل إنشاء المسؤول: {str(e)}")

def create_default_rubrics():
    """إنشاء قوالب معايير تقييم افتراضية"""
    from app import db
    from app.models.rubric import Rubric
    
    # التحقق مما إذا كان هناك أي معايير تقييم بالفعل
    if Rubric.query.count() > 0:
        logger.info("معايير التقييم موجودة بالفعل")
        return
    
    # إنشاء قالب عام
    general_rubric = Rubric.create_default_rubric(
        name="معايير التقييم العامة",
        description="معايير تقييم عامة للمهام الأكاديمية",
        template_type="general"
    )
    
    # إنشاء قالب برمجة
    programming_rubric = Rubric.create_default_rubric(
        name="معايير تقييم البرمجة",
        description="معايير تقييم خاصة بمهام البرمجة والتطوير",
        template_type="programming"
    )
    
    try:
        db.session.add(general_rubric)
        db.session.add(programming_rubric)
        db.session.commit()
        logger.info("تم إنشاء معايير التقييم الافتراضية بنجاح")
    except Exception as e:
        db.session.rollback()
        logger.error(f"فشل إنشاء معايير التقييم الافتراضية: {str(e)}")

def create_default_courses():
    """إنشاء مساقات افتراضية"""
    # هذه الدالة غير منفذة حالياً، مخصصة للتوسع المستقبلي
    pass

@click.command('init-db')
@with_appcontext
def setup_database():
    """إعداد وتهيئة قاعدة البيانات بالكامل"""
    from app import db
    
    # إنشاء المفاتيح السرية
    ensure_encryption_key()
    ensure_secret_key('SECRET_KEY')
    ensure_secret_key('JWT_SECRET_KEY')
    ensure_secret_key('SECURITY_PASSWORD_SALT')
    
    try:
        # إنشاء جداول قاعدة البيانات
        db.create_all()
        logger.info("تم إنشاء جداول قاعدة البيانات بنجاح")
        
        # إنشاء بيانات افتراضية
        create_default_admin()
        create_default_rubrics()
        
        logger.info("تم إعداد قاعدة البيانات بنجاح")
        
    except Exception as e:
        logger.error(f"فشل إعداد قاعدة البيانات: {str(e)}")
        raise e

if __name__ == "__main__":
    from app import create_app
    
    app = create_app()
    with app.app_context():
        # إعداد قاعدة البيانات
        setup_database()
        logger.info("اكتمل إعداد قاعدة البيانات")