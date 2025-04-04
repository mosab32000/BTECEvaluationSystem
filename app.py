"""
نقطة الدخول الرئيسية لتطبيق نظام تقييم BTEC
يقوم بتشغيل التطبيق على المنفذ 5000
"""
import os
import logging
from dotenv import load_dotenv

# تحميل المتغيرات البيئية
load_dotenv()

# تكوين التسجيل
logging.basicConfig(level=logging.INFO,
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# استيراد التطبيق
from app import create_app

# إنشاء تطبيق Flask
app = create_app()

if __name__ == "__main__":
    # تشغيل التطبيق
    host = os.environ.get('HOST', '0.0.0.0')
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    
    logger.info(f"تشغيل تطبيق نظام تقييم BTEC على {host}:{port} (وضع التصحيح: {debug})")
    app.run(host=host, port=port, debug=debug)