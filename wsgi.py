"""
نقطة الدخول الرئيسية للنشر في WSGI لنظام تقييم BTEC
"""

import os
import secrets

# تحميل متغيرات البيئة من ملف .env
from dotenv import load_dotenv
load_dotenv()

# ضمان وجود المفاتيح السرية
def ensure_secret_key(env_var, length=32):
    """التأكد من وجود المفتاح السري، وإنشاء واحد جديد إذا لم يكن موجوداً"""
    if env_var not in os.environ:
        os.environ[env_var] = secrets.token_hex(length)

# ضمان وجود المفاتيح السرية الأساسية
ensure_secret_key("SECRET_KEY")
ensure_secret_key("JWT_SECRET_KEY")
ensure_secret_key("WTF_CSRF_SECRET_KEY")

# إنشاء كائن التطبيق
from app import create_app
app = create_app()

if __name__ == "__main__":
    # تعيين المنفذ من متغيرات البيئة أو استخدام القيمة الافتراضية
    port = int(os.environ.get("PORT", 5000))
    # تشغيل التطبيق
    app.run(host="0.0.0.0", port=port)