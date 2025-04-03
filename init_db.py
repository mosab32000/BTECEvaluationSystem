"""
هذا البرنامج يقوم بإنشاء قواعد البيانات المطلوبة لنظام تقييم BTEC
"""

import os
import base64
import logging
import secrets
import json
from flask import Flask
from dotenv import load_dotenv

# إعداد التسجيل
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger(__name__)

# تحميل متغيرات البيئة
load_dotenv()

def ensure_encryption_key():
    """التأكد من وجود مفتاح التشفير، وإنشاء واحد جديد إذا لم يكن موجودًا"""
    if 'ENCRYPTION_KEY' not in os.environ or not os.environ.get('ENCRYPTION_KEY'):
        encryption_key = base64.urlsafe_b64encode(secrets.token_bytes(32)).decode()
        logger.info("تم إنشاء مفتاح تشفير جديد")
        
        # تحديث ملف .env
        env_path = '.env'
        env_content = []
        if os.path.exists(env_path):
            with open(env_path, 'r') as f:
                env_content = f.readlines()
        
        key_set = False
        for i, line in enumerate(env_content):
            if line.startswith('ENCRYPTION_KEY='):
                env_content[i] = f'ENCRYPTION_KEY={encryption_key}\n'
                key_set = True
                break
        
        if not key_set:
            env_content.append(f'ENCRYPTION_KEY={encryption_key}\n')
        
        with open(env_path, 'w') as f:
            f.writelines(env_content)
        
        os.environ['ENCRYPTION_KEY'] = encryption_key
        logger.info("تم تحديث مفتاح التشفير في ملف .env")
    else:
        logger.info("مفتاح التشفير موجود مسبقاً")

def ensure_secret_key(env_var, length=32):
    """التأكد من وجود مفتاح سري، وإنشاء واحد جديد إذا لم يكن موجودًا"""
    if env_var not in os.environ or not os.environ.get(env_var):
        secret_key = secrets.token_hex(length)
        logger.info(f"تم إنشاء مفتاح سري جديد لـ {env_var}")
        
        # تحديث ملف .env
        env_path = '.env'
        env_content = []
        if os.path.exists(env_path):
            with open(env_path, 'r') as f:
                env_content = f.readlines()
        
        key_set = False
        for i, line in enumerate(env_content):
            if line.startswith(f'{env_var}='):
                env_content[i] = f'{env_var}={secret_key}\n'
                key_set = True
                break
        
        if not key_set:
            env_content.append(f'{env_var}={secret_key}\n')
        
        with open(env_path, 'w') as f:
            f.writelines(env_content)
        
        os.environ[env_var] = secret_key
        logger.info(f"تم تحديث {env_var} في ملف .env")
    else:
        logger.info(f"{env_var} موجود مسبقاً")

def create_default_admin():
    """إنشاء حساب مسؤول افتراضي إذا لم يكن موجودًا"""
    # سيتم تنفيذ هذا لاحقاً عند تكامل قاعدة البيانات
    logger.info("تم تخطي إنشاء حساب مسؤول (سيتم تنفيذه لاحقاً)")

def create_default_rubrics():
    """إنشاء قوالب معايير تقييم افتراضية"""
    # سيتم تنفيذ هذا لاحقاً عند تكامل قاعدة البيانات
    logger.info("تم تخطي إنشاء قوالب معايير التقييم (سيتم تنفيذه لاحقاً)")

def setup_database():
    """إعداد وتهيئة قاعدة البيانات بالكامل"""
    # التأكد من وجود مفاتيح التشفير والمفاتيح السرية
    ensure_encryption_key()
    ensure_secret_key('SECRET_KEY')
    ensure_secret_key('JWT_SECRET_KEY')
    
    # إنشاء حساب مسؤول افتراضي
    create_default_admin()
    
    # إنشاء قوالب معايير التقييم الافتراضية
    create_default_rubrics()
    
    logger.info("تم الانتهاء من إعداد قاعدة البيانات بنجاح")

if __name__ == '__main__':
    try:
        setup_database()
        print("تم إعداد قاعدة البيانات بنجاح")
    except Exception as e:
        logger.error(f"حدث خطأ أثناء إعداد قاعدة البيانات: {e}")
        print(f"فشل إعداد قاعدة البيانات: {e}")