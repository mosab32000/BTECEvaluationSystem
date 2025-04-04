"""
سكريبت لإنشاء مستخدم مسؤول في نظام تقييم BTEC
"""
import os
import sys
import logging
from datetime import datetime

from flask import Flask
from werkzeug.security import generate_password_hash
from dotenv import load_dotenv

from app import db, create_app
from app.models.user import User
from app.database import log_audit

# تكوين التسجيل
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def create_main_admin():
    """
    إنشاء حساب المسؤول الرئيسي (مصعب الحلالة)
    """
    # تحميل متغيرات البيئة
    load_dotenv()
    
    # إنشاء تطبيق Flask
    app = create_app(os.getenv('FLASK_ENV', 'development'))
    
    # العمل داخل سياق التطبيق
    with app.app_context():
        try:
            # التحقق مما إذا كان هناك مسؤول رئيسي موجود بالفعل
            admin = User.query.filter_by(email='admin@btec-eval.com').first()
            
            if admin:
                logging.info(f"المسؤول الرئيسي موجود بالفعل: {admin.email}")
                return
            
            # إنشاء المسؤول الرئيسي
            main_admin = User(
                name="مصعب الحلالة",
                email="admin@btec-eval.com",
                password_hash=generate_password_hash("admin123"),
                role="admin",
                is_active=True,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            
            # حفظ المسؤول في قاعدة البيانات
            db.session.add(main_admin)
            db.session.commit()
            
            # تسجيل الحدث في السجل
            logging.info(f"تم إنشاء المسؤول الرئيسي بنجاح: {main_admin.email}")
            try:
                log_audit('admin_creation', 'System', f"تم إنشاء المسؤول الرئيسي: {main_admin.email}")
            except Exception as e:
                logging.warning(f"تعذر تسجيل الحدث في سجل التدقيق: {str(e)}")
            
            print(f"""
================================================
تم إنشاء حساب المسؤول الرئيسي بنجاح:
------------------------------------------------
الاسم: {main_admin.name}
البريد الإلكتروني: {main_admin.email}
كلمة المرور: admin123
================================================
يرجى تغيير كلمة المرور بعد تسجيل الدخول الأول!
================================================
            """)
            
        except Exception as e:
            db.session.rollback()
            logging.error(f"خطأ في إنشاء المسؤول الرئيسي: {str(e)}")
            sys.exit(1)

if __name__ == "__main__":
    create_main_admin()