"""
ملف تشغيل تجريبي لنظام تقييم BTEC
"""
import os
import sys
import logging
from datetime import datetime

# إعداد تسجيل الأحداث
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

def run_app():
    """
    تشغيل تطبيق نظام تقييم BTEC
    """
    try:
        # استيراد التطبيق
        from app import create_app
        
        # إنشاء تطبيق Flask
        app = create_app()
        
        # تعيين متغيرات البيئة
        host = os.environ.get('HOST', '0.0.0.0')
        port = int(os.environ.get('PORT', 5000))
        debug = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
        
        # تشغيل التطبيق
        logger.info(f"تشغيل تطبيق نظام تقييم BTEC على {host}:{port} (وضع التصحيح: {debug})")
        app.run(host=host, port=port, debug=debug)
    
    except Exception as e:
        logger.error(f"خطأ أثناء تشغيل التطبيق: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    logger.info("بدء تشغيل نظام تقييم BTEC")
    run_app()