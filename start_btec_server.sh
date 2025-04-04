#!/bin/bash
# سكريبت لتشغيل خادم نظام تقييم BTEC

# تعيين متغيرات البيئة
export FLASK_APP=app.py
export FLASK_ENV=production
export FLASK_DEBUG=0

echo "تهيئة قاعدة البيانات..."
python init_db.py

echo "تشغيل خادم التطبيق..."
gunicorn -c gunicorn_config.py "app:create_app()"
