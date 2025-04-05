#!/usr/bin/env python3
"""
نقطة الدخول الرئيسية لخادم نظام تقييم BTEC
تهدف هذه النقطة إلى تشغيل الخادم بشكل مستمر على Replit
"""

import os
import logging
import signal
import sys
import time
from pathlib import Path
from dotenv import load_dotenv

# إعداد تسجيل السجلات
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - btec_eval - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('app.log')
    ]
)

logger = logging.getLogger('btec_eval')

def ensure_secret_key(env_var, length=32):
    """التأكد من وجود المفتاح السري، وإنشاء واحد جديد إذا لم يكن موجوداً"""
    import secrets
    
    # التحقق من وجود المفتاح في متغيرات البيئة
    if env_var not in os.environ:
        # إنشاء مفتاح جديد
        new_key = secrets.token_hex(length)
        os.environ[env_var] = new_key
        
        # إضافة المفتاح إلى ملف .env
        env_file = Path('.env')
        if env_file.exists():
            with open(env_file, 'r', encoding='utf-8') as f:
                env_lines = f.readlines()
                
            # البحث عن المفتاح وتحديثه
            found = False
            for i, line in enumerate(env_lines):
                if line.startswith(f"{env_var}="):
                    env_lines[i] = f"{env_var}={new_key}\n"
                    found = True
                    break
            
            # إضافة المفتاح إذا لم يكن موجودًا
            if not found:
                env_lines.append(f"{env_var}={new_key}\n")
                
            with open(env_file, 'w', encoding='utf-8') as f:
                f.writelines(env_lines)
        else:
            # إنشاء ملف .env إذا لم يكن موجودًا
            with open(env_file, 'w', encoding='utf-8') as f:
                f.write(f"{env_var}={new_key}\n")
                
        logger.info(f"تم إنشاء {env_var} جديد")
        logger.info(f"تم حفظ {env_var} في ملف .env")

def setup_environment():
    """إعداد متغيرات البيئة الضرورية"""
    logger.info("إعداد متغيرات البيئة الضرورية...")
    
    # تحميل متغيرات البيئة من ملف .env
    load_dotenv()
    
    # التأكد من وجود المفاتيح السرية الضرورية
    ensure_secret_key('SECRET_KEY')
    ensure_secret_key('JWT_SECRET_KEY')
    ensure_secret_key('WTF_CSRF_SECRET_KEY')
    ensure_secret_key('SECURITY_PASSWORD_SALT')
    
    # ضبط متغيرات البيئة الافتراضية إذا لم تكن موجودة
    if 'FLASK_APP' not in os.environ:
        os.environ['FLASK_APP'] = 'wsgi.py'
    
    if 'FLASK_ENV' not in os.environ:
        os.environ['FLASK_ENV'] = 'development'
    
    if 'FLASK_DEBUG' not in os.environ:
        os.environ['FLASK_DEBUG'] = '1'
    
    if 'LOG_LEVEL' not in os.environ:
        os.environ['LOG_LEVEL'] = 'INFO'
    
    logger.info("تم إعداد متغيرات البيئة بنجاح")

def check_database_connection():
    """التحقق من اتصال قاعدة البيانات"""
    logger.info("التحقق من اتصال قاعدة البيانات...")
    
    import time
    import sqlalchemy
    from sqlalchemy.exc import SQLAlchemyError
    
    # الحصول على رابط قاعدة البيانات من متغيرات البيئة
    database_url = os.environ.get('DATABASE_URL')
    if not database_url:
        logger.error("متغير البيئة DATABASE_URL غير موجود")
        return False
    
    # محاولة الاتصال بقاعدة البيانات
    for attempt in range(3):
        try:
            engine = sqlalchemy.create_engine(database_url)
            connection = engine.connect()
            connection.close()
            logger.info("تم التحقق من قاعدة البيانات بنجاح")
            return True
        except SQLAlchemyError as e:
            logger.warning(f"فشل الاتصال بقاعدة البيانات (محاولة {attempt+1}/3): {e}")
            time.sleep(2)
    
    logger.error("فشل الاتصال بقاعدة البيانات بعد 3 محاولات")
    return False

def init_database():
    """تهيئة قاعدة البيانات وإنشاء الجداول"""
    logger.info("تهيئة قاعدة البيانات...")
    
    try:
        # استيراد الملفات اللازمة لتهيئة قاعدة البيانات
        from app import create_app, db
        
        # إنشاء تطبيق Flask مع سياق التطبيق
        app = create_app()
        with app.app_context():
            # إنشاء جميع الجداول
            db.create_all()
            
            # محاولة إنشاء مستخدم مسؤول إذا لم يكن موجودًا
            try:
                from app.models.user import User
                
                # التحقق من وجود أي مستخدمين
                if User.query.count() == 0:
                    # إنشاء مستخدم مسؤول
                    from werkzeug.security import generate_password_hash
                    
                    admin_user = User(
                        email="admin@btec.edu",
                        name="مسؤول النظام",
                        password_hash=generate_password_hash("admin123"),
                        role="admin",
                        is_active=True
                    )
                    db.session.add(admin_user)
                    db.session.commit()
                    logger.info("تم إنشاء مستخدم مسؤول افتراضي")
            except Exception as e:
                logger.error(f"خطأ أثناء إنشاء مستخدم مسؤول: {e}")
        
        logger.info("تم تهيئة قاعدة البيانات بنجاح")
        return True
    except Exception as e:
        logger.error(f"خطأ أثناء تهيئة قاعدة البيانات: {e}")
        return False

def start_server():
    """بدء تشغيل الخادم"""
    try:
        from flask.cli import load_dotenv
        from app import create_app
        
        # تحميل متغيرات البيئة
        load_dotenv()
        
        # إنشاء تطبيق Flask
        app = create_app()
        
        # تشغيل التطبيق
        logger.info("بدء تشغيل نظام تقييم BTEC...")
        app.run(host="0.0.0.0", port=5000, debug=True)
        
    except Exception as e:
        logger.error(f"خطأ أثناء تشغيل الخادم: {e}")
        return False

def main():
    """الدالة الرئيسية"""
    logger.info("بدء تشغيل نظام تقييم BTEC...")
    
    # إعداد متغيرات البيئة
    setup_environment()
    
    # التحقق من اتصال قاعدة البيانات
    if not check_database_connection():
        logger.error("فشل الاتصال بقاعدة البيانات. توقف التشغيل.")
        return
    
    # تهيئة قاعدة البيانات
    if not init_database():
        logger.error("فشل تهيئة قاعدة البيانات. توقف التشغيل.")
        return
    
    # بدء تشغيل الخادم
    start_server()

if __name__ == "__main__":
    main()
