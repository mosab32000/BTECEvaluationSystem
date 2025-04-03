"""
نقطة الدخول الرئيسية لتطبيق نظام تقييم BTEC
يقوم بتشغيل التطبيق على المنفذ 3000
"""

import os
from dotenv import load_dotenv
from backend.app import create_app

# تحميل متغيرات البيئة من ملف .env
load_dotenv()

# إنشاء تطبيق Flask
app = create_app()

if __name__ == "__main__":
    # تشغيل التطبيق على المنفذ المحدد في المتغيرات البيئية أو 3000 افتراضيًا
    port = int(os.environ.get('PORT', 3000))
    app.run(host="0.0.0.0", port=port, debug=True)