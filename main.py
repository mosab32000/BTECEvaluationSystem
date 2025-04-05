"""
نقطة الدخول الرئيسية لتطبيق نظام تقييم BTEC
"""

import os
import sys
import logging
from dotenv import load_dotenv

# تهيئة السجلات
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

# تحميل متغيرات البيئة من ملف .env
load_dotenv()

# إنشاء المجلدات الضرورية
os.makedirs('logs', exist_ok=True)
os.makedirs('uploads', exist_ok=True)
os.makedirs('static/uploads', exist_ok=True)

# استيراد تطبيق Flask
from wsgi import app

if __name__ == "__main__":
    # تعيين المنفذ من متغيرات البيئة أو استخدام القيمة الافتراضية
    port = int(os.environ.get("PORT", 5000))
    
    logger.info(f"بدء تشغيل نظام تقييم BTEC على المنفذ {port}")
    
    # تشغيل التطبيق
    app.run(host="0.0.0.0", port=port, debug=True)