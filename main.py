"""
نقطة الدخول الرئيسية لتطبيق نظام تقييم BTEC
يقوم بتشغيل التطبيق على المنفذ 3000
"""

import os
import logging
from backend.app import create_app
from dotenv import load_dotenv

# إعداد التسجيل
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='server.log',
    filemode='a'
)

# التأكد من تحميل متغيرات البيئة
load_dotenv()

# إنشاء تطبيق Flask مع الإعدادات المناسبة
app = create_app(os.getenv('FLASK_ENV', 'development'))

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=port, debug=True)