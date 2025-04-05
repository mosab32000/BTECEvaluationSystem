"""
نقطة الدخول الرئيسية للنشر في WSGI لنظام تقييم BTEC
"""

import os
import sys
import logging
from dotenv import load_dotenv

# إضافة المجلد الحالي إلى مسار Python
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# تحميل متغيرات البيئة من ملف .env
dotenv_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

# إعداد السجلات
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('server.log')
    ]
)

logger = logging.getLogger(__name__)
logger.info("بدء تشغيل نظام تقييم BTEC (WSGI)")

# استيراد تطبيق Flask
from app import create_app

# إنشاء تطبيق Flask
application = create_app()
app = application

# إذا تم تشغيل هذا الملف مباشرة
if __name__ == '__main__':
    # تشغيل التطبيق
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))