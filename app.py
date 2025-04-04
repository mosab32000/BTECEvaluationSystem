"""
نقطة الدخول الرئيسية لتطبيق نظام تقييم BTEC
يقوم بتشغيل التطبيق على المنفذ 3000
"""
import os
import logging
from dotenv import load_dotenv

from app import create_app

# تحميل متغيرات البيئة من ملف .env
load_dotenv()

# إنشاء تطبيق Flask
app = create_app(os.getenv('FLASK_ENV', 'development'))

if __name__ == '__main__':
    # تشغيل التطبيق
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
