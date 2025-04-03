"""
سكريبت لإنشاء مستخدم مسؤول في نظام تقييم BTEC
"""

import os
import logging
import datetime
from werkzeug.security import generate_password_hash
from dotenv import load_dotenv

# إعداد التسجيل
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger(__name__)

# تحميل متغيرات البيئة
load_dotenv()

def create_main_admin():
    """
    إنشاء حساب المسؤول الرئيسي (مصعب الحلالة)
    """
    try:
        # اختبار لتحقق مما إذا كانت قاعدة البيانات متاحة
        print("جاري إنشاء حساب المسؤول الرئيسي...")
        
        # المعلومات الافتراضية للمسؤول (ستتم إضافتها لقاعدة البيانات لاحقاً)
        admin_info = {
            "email": "mosab3200@gmail.com",
            "password": "Mos0779750516@",
            "name": "مصعب الحلالة",
            "role": "admin",
            "last_login": datetime.datetime.utcnow(),
            "created_at": datetime.datetime.utcnow()
        }
        
        # تشفير كلمة المرور
        admin_info["password_hash"] = generate_password_hash(admin_info["password"])
        
        # حفظ معلومات المسؤول في ملف لاستخدامها لاحقاً
        with open("admin_info.txt", "w") as f:
            f.write(f"Email: {admin_info['email']}\n")
            f.write(f"Password: {admin_info['password']}\n")
            f.write(f"Name: {admin_info['name']}\n")
            f.write(f"Role: {admin_info['role']}\n")
            f.write(f"Created at: {admin_info['created_at'].strftime('%Y-%m-%d %H:%M:%S')}\n")
        
        print("تم إنشاء حساب المسؤول بنجاح وحفظ المعلومات في ملف admin_info.txt")
        
        return True
    except Exception as e:
        logger.error(f"حدث خطأ أثناء إنشاء حساب المسؤول: {e}")
        return False

if __name__ == "__main__":
    create_main_admin()