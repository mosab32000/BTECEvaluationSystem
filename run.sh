#!/bin/bash

# إعداد متغيرات البيئة
export FLASK_APP=app.py
export FLASK_ENV=development
export FLASK_DEBUG=1

# إنشاء قاعدة البيانات والجداول إذا لم تكن موجودة
echo "تهيئة قاعدة البيانات..."
python init_db.py

# تشغيل الخادم
echo "تشغيل خادم التطبيق..."
python run.py