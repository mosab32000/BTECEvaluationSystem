#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
سكريبت لإنشاء مستخدم مسؤول في نظام تقييم BTEC
"""

import os
import sys
import logging
import getpass
from werkzeug.security import generate_password_hash
from dotenv import load_dotenv

# إعداد السجلات
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('admin_creator')

# تحميل متغيرات البيئة
load_dotenv()

# استيراد نظام قاعدة البيانات
sys.path.append(os.path.dirname(__file__))
from app import create_app, db
from app.models.user import User

def create_admin_user(email, name, password):
    """
    إنشاء مستخدم مسؤول جديد
    
    Args:
        email (str): البريد الإلكتروني للمسؤول
        name (str): اسم المسؤول
        password (str): كلمة المرور
    
    Returns:
        bool: نجاح العملية
    """
    try:
        # التحقق مما إذا كان المستخدم موجودًا
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            logger.warning(f"المستخدم بالبريد الإلكتروني {email} موجود بالفعل")
            return False
        
        # إنشاء مستخدم مسؤول جديد
        admin_user = User(
            email=email,
            name=name,
            password_hash=generate_password_hash(password),
            role='admin',
            is_active=True
        )
        
        # حفظ المستخدم في قاعدة البيانات
        db.session.add(admin_user)
        db.session.commit()
        
        logger.info(f"تم إنشاء المستخدم المسؤول {email} بنجاح")
        return True
    
    except Exception as e:
        logger.error(f"خطأ أثناء إنشاء المستخدم المسؤول: {str(e)}")
        return False

def create_main_admin():
    """
    إنشاء حساب المسؤول الرئيسي (مصعب الحلالة)
    """
    app = create_app()
    with app.app_context():
        # مسح الشاشة
        os.system('cls' if os.name == 'nt' else 'clear')
        
        print("\n" + "=" * 60)
        print("  إنشاء حساب المسؤول الرئيسي لنظام تقييم BTEC".center(60))
        print("=" * 60 + "\n")
        
        # بيانات المسؤول الافتراضية
        default_email = "admin@btec-eval.edu"
        default_name = "مصعب الحلحولي"
        
        # طلب البيانات من المستخدم
        email = input(f"البريد الإلكتروني للمسؤول [{default_email}]: ") or default_email
        name = input(f"اسم المسؤول [{default_name}]: ") or default_name
        
        # طلب كلمة المرور بشكل آمن (مخفي)
        password = getpass.getpass("كلمة المرور: ")
        confirm_password = getpass.getpass("تأكيد كلمة المرور: ")
        
        # التحقق من تطابق كلمات المرور
        if password != confirm_password:
            print("\n⚠️  خطأ: كلمات المرور غير متطابقة")
            return False
        
        # التحقق من طول كلمة المرور
        if len(password) < 8:
            print("\n⚠️  خطأ: يجب أن تكون كلمة المرور 8 أحرف على الأقل")
            return False
        
        # إنشاء المستخدم المسؤول
        success = create_admin_user(email, name, password)
        
        if success:
            print("\n✅  تم إنشاء حساب المسؤول بنجاح")
        else:
            print("\n❌  فشل في إنشاء حساب المسؤول")
        
        return success

if __name__ == "__main__":
    create_main_admin()