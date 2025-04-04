#!/bin/bash
# سكريبت لتشغيل نظام تقييم BTEC بواسطة workflow

# تعيين المتغيرات
export FLASK_APP=app.py
export FLASK_ENV=production
export FLASK_DEBUG=0

echo "تهيئة قاعدة البيانات..."
python init_db.py

echo "تشغيل خادم التطبيق..."
python run.py
