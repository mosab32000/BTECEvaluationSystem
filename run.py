"""
نقطة الدخول الرئيسية لتطبيق نظام تقييم BTEC
"""
import os
import sys
import logging
from dotenv import load_dotenv

# تحميل متغيرات البيئة من ملف .env
load_dotenv()

# إعداد السجلات
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('app.log')
    ]
)
logger = logging.getLogger(__name__)

def check_requirements():
    """التحقق من توفر المتطلبات الأساسية"""
    try:
        import flask
        import werkzeug
        import flask_jwt_extended
        logger.info("تم التحقق من المتطلبات الأساسية")
        return True
    except ImportError as e:
        logger.error(f"خطأ في المتطلبات: {str(e)}")
        return False

def check_database():
    """التحقق من الاتصال بقاعدة البيانات"""
    from app.database import check_database_connection, init_db
    
    connected, error = check_database_connection()
    if not connected:
        logger.error(f"فشل الاتصال بقاعدة البيانات: {error}")
        return False
    
    # تهيئة قاعدة البيانات إذا لم تكن موجودة
    logger.info("تم الاتصال بقاعدة البيانات بنجاح، جاري التحقق من هيكل الجداول...")
    if not init_db():
        logger.error("فشل في تهيئة قاعدة البيانات")
        return False
    
    return True

def main():
    """الدالة الرئيسية لتشغيل التطبيق"""
    # التحقق من المتطلبات
    if not check_requirements():
        logger.error("فشل في التحقق من المتطلبات الأساسية")
        return
    
    # التحقق من اتصال قاعدة البيانات
    if not check_database():
        logger.error("فشل في التحقق من قاعدة البيانات")
        return
    
    # إنشاء وتهيئة التطبيق
    from app import create_app
    app = create_app()
    
    # إنشاء مستخدم المسؤول الافتراضي إذا لم يكن موجودًا
    from app.models.user import User
    from werkzeug.security import generate_password_hash
    
    admin_email = os.environ.get('ADMIN_EMAIL', 'admin@btec-eval.com')
    admin_password = os.environ.get('DEFAULT_ADMIN_PASSWORD', 'defaultadmin2025')
    
    admin = User.get_by_email(admin_email)
    if not admin:
        logger.info(f"إنشاء مستخدم المسؤول الافتراضي: {admin_email}")
        admin = User(
            email=admin_email,
            password_hash=generate_password_hash(admin_password),
            name='مسؤول النظام',
            role='admin'
        )
        admin.save()
    
    # تشغيل التطبيق
    port = int(os.environ.get('PORT', 5000))
    host = os.environ.get('HOST', '0.0.0.0')
    debug = os.environ.get('DEBUG', 'False').lower() == 'true'
    
    logger.info(f"بدء تشغيل نظام تقييم BTEC على المنفذ {port}")
    app.run(host=host, port=port, debug=debug)

if __name__ == '__main__':
    main()