"""
نقطة دخول WSGI لخادم نظام تقييم BTEC
تستخدم لنشر التطبيق على خوادم الإنتاج مثل Gunicorn
"""

import os
import sys
import logging
from dotenv import load_dotenv

# تضمين الدليل الحالي في مسار البحث
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# تحميل متغيرات البيئة
load_dotenv()

from app import create_app

# إنشاء تطبيق التوزيع
app = create_app('production')

if __name__ == "__main__":
    # إعداد التسجيل للتشغيل المباشر (غير مستخدم عادة)
    logging.basicConfig(
        level=getattr(logging, os.environ.get('LOG_LEVEL', 'INFO').upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(os.environ.get('LOG_FILE', 'app.log')),
            logging.StreamHandler()
        ]
    )
    
    # تشغيل التطبيق مباشرة (للاختبار فقط)
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)