#!/bin/bash

# إعداد متغيرات البيئة
export FLASK_APP=app.py
export FLASK_ENV=production

# إنشاء قاعدة البيانات والجداول إذا لم تكن موجودة
echo "تهيئة قاعدة البيانات..."
python init_db.py

# تشغيل الخادم باستخدام Gunicorn للحصول على أداء أفضل وتشغيل مستمر
echo "تشغيل خادم التطبيق باستخدام Gunicorn..."
gunicorn -c gunicorn_config.py "app:create_app()"
