"""
ملف WSGI لتشغيل تطبيق نظام تقييم BTEC على خدمات استضافة مثل Render
يستخدم هذا الملف في إعدادات Procfile
"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv

# تحميل متغيرات البيئة
load_dotenv()

from app import create_app

# إنشاء تطبيق Flask
app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))