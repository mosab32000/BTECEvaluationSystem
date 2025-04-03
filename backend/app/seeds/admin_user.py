"""
ملف بذور لإنشاء المستخدم المسؤول في نظام تقييم BTEC
"""

from werkzeug.security import generate_password_hash
from ..models import User, db
import logging

# إعداد السجل
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_admin_user():
    """
    إنشاء حساب المسؤول عن النظام إذا لم يكن موجوداً بالفعل
    """
    admin_email = "mosab3200@gmail.com"
    
    # التحقق مما إذا كان المسؤول موجوداً بالفعل
    admin = User.query.filter_by(email=admin_email).first()
    
    if not admin:
        # إنشاء حساب المسؤول
        admin = User(
            email=admin_email,
            password_hash=generate_password_hash("Mos0779750516@"),
            name="مصعب الحلالة",
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
        admin.password_hash = generate_password_hash("Mos0779750516@")
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