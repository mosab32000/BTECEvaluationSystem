"""
سكريبت لإنشاء مستخدم مسؤول في نظام تقييم BTEC
"""

from dotenv import load_dotenv
import os
from flask import Flask
from werkzeug.security import generate_password_hash

# تحميل متغيرات البيئة
load_dotenv()

# إنشاء تطبيق Flask
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'default-secret-key')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# استيراد نماذج قاعدة البيانات
from backend.app.database import db
from backend.app.models import User

db.init_app(app)

def create_main_admin():
    """
    إنشاء حساب المسؤول الرئيسي (مصعب الحلالة)
    """
    with app.app_context():
        # التحقق ما إذا كان المستخدم موجودًا
        admin_email = "admin@btec-eval.com"
        
        # البحث عن المستخدم
        admin = User.query.filter_by(email=admin_email).first()
        
        if admin:
            print(f"المسؤول موجود بالفعل: {admin_email}")
            return admin
        
        # إنشاء مستخدم مسؤول جديد
        new_admin = User(
            email=admin_email,
            name="مصعب العجارمة",
            role="admin",
            is_active=True
        )
        
        # تعيين كلمة المرور
        new_admin.set_password("admin123")
        
        # حفظ المستخدم في قاعدة البيانات
        db.session.add(new_admin)
        db.session.commit()
        
        print(f"تم إنشاء المسؤول بنجاح: {admin_email}")
        return new_admin

if __name__ == "__main__":
    create_main_admin()
    print("بيانات الدخول:")
    print("البريد الإلكتروني: admin@btec-eval.com")
    print("كلمة المرور: admin123")