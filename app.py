"""
نقطة الدخول الرئيسية لتطبيق نظام تقييم BTEC
يقوم بتشغيل التطبيق على المنفذ 5000
"""

import os
from dotenv import load_dotenv
from backend.app import create_app

# تحميل متغيرات البيئة من ملف .env
load_dotenv()

# إنشاء تطبيق Flask
app = create_app()

if __name__ == "__main__":
    # تشغيل التطبيق على المنفذ 8080 وجعله متاحًا على جميع الواجهات
    app.run(host="0.0.0.0", port=8080, debug=True)