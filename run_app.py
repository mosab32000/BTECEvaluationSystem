"""
ملف تشغيل تطبيق نظام تقييم BTEC
"""
import os
import sys
import logging
from dotenv import load_dotenv

# تحميل متغيرات البيئة
load_dotenv()

# تكوين السجلات
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('app.log')
    ]
)
logger = logging.getLogger(__name__)

def main():
    """
    النقطة الرئيسية لتشغيل تطبيق نظام تقييم BTEC
    """
    try:
        # تهيئة قاعدة البيانات
        from app.database import init_db, check_database_connection
        
        # التحقق من اتصال قاعدة البيانات
        connected, error = check_database_connection()
        if not connected:
            logger.error(f"فشل الاتصال بقاعدة البيانات: {error}")
            return
        
        logger.info("تم الاتصال بقاعدة البيانات بنجاح")
        
        # تهيئة هيكل قاعدة البيانات
        if init_db():
            logger.info("تم تهيئة قاعدة البيانات بنجاح")
        else:
            logger.error("فشل في تهيئة قاعدة البيانات")
            return
        
        # إنشاء معايير التقييم الافتراضية
        from app.models.rubric import Rubric
        if Rubric.create_default_rubrics():
            logger.info("تم التحقق من معايير التقييم الافتراضية")
        
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
            if admin.save():
                logger.info("تم إنشاء مستخدم المسؤول بنجاح")
            else:
                logger.error("فشل في إنشاء مستخدم المسؤول")
        
        # تشغيل التطبيق
        from app import create_app
        app = create_app()
        
        host = os.environ.get('HOST', '0.0.0.0')
        port = int(os.environ.get('PORT', 5000))
        debug = os.environ.get('DEBUG', 'False').lower() == 'true'
        
        logger.info(f"بدء تشغيل نظام تقييم BTEC على {host}:{port}")
        app.run(host=host, port=port, debug=debug)
    
    except Exception as e:
        logger.error(f"حدث خطأ أثناء تشغيل التطبيق: {str(e)}", exc_info=True)

if __name__ == '__main__':
    main()