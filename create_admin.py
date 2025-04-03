"""
سكريبت لإنشاء مستخدم مسؤول في نظام تقييم BTEC
"""

from backend.app import create_app
from backend.app.database import db
from backend.app.models import User
from werkzeug.security import generate_password_hash
import logging

# إعداد السجل
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_main_admin():
    """
    إنشاء حساب المسؤول الرئيسي (مصعب الحلالة)
    """
    admin_email = "mosab3200@gmail.com"
    admin_password = "Mos0779750516@"
    admin_name = "مصعب الحلالة"
    
    app = create_app()
    with app.app_context():
        # التحقق مما إذا كان المسؤول موجوداً بالفعل
        admin = User.query.filter_by(email=admin_email).first()
        
        if not admin:
            # إنشاء حساب المسؤول
            admin = User(
                email=admin_email,
                password_hash=generate_password_hash(admin_password),
                name=admin_name,
                role="admin",
                is_active=True
            )
            
            try:
                db.session.add(admin)
                db.session.commit()
                logger.info(f"تم إنشاء حساب المسؤول بالبريد الإلكتروني: {admin_email}")
                return True
            except Exception as e:
                db.session.rollback()
                logger.error(f"خطأ أثناء إنشاء حساب المسؤول: {e}")
                return False
        else:
            # تحديث كلمة المرور إذا كان المسؤول موجوداً بالفعل
            admin.password_hash = generate_password_hash(admin_password)
            admin.name = admin_name
            admin.is_active = True
            admin.role = "admin"  # التأكد من أن الدور هو مسؤول
            
            try:
                db.session.commit()
                logger.info(f"تم تحديث حساب المسؤول: {admin_email}")
                return True
            except Exception as e:
                db.session.rollback()
                logger.error(f"خطأ أثناء تحديث حساب المسؤول: {e}")
                return False

if __name__ == "__main__":
    if create_main_admin():
        logger.info("تمت العملية بنجاح.")
    else:
        logger.error("فشلت العملية.")