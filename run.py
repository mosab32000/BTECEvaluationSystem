"""
نقطة الدخول الرئيسية لتطبيق نظام تقييم BTEC
"""
import os
import logging
from dotenv import load_dotenv

# تحميل متغيرات البيئة من ملف .env إذا كان موجوداً
if os.path.exists('.env'):
    load_dotenv()
    print("تم تحميل ملف .env")

# إعداد التسجيل
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# التأكد من وجود المجلدات الضرورية
for folder in ['logs', 'static', 'templates', 'app/models', 'app/routes', 'app/core']:
    os.makedirs(folder, exist_ok=True)

# إنشاء تطبيق Flask باستخدام المصنع
from app import create_app

app = create_app()

# تشغيل التطبيق
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    
    logger.info(f"بدء تشغيل نظام تقييم BTEC على المنفذ {port}")
    
    app.run(host='0.0.0.0', port=port, debug=True)