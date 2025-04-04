#!/bin/bash

# نص ملف تشغيل workflow لنظام تقييم BTEC
echo "بدء تشغيل workflow لنظام تقييم BTEC..."

# إعداد متغيرات البيئة
export FLASK_APP=app.py
export FLASK_ENV=development
export FLASK_DEBUG=True
export HOST=0.0.0.0
export PORT=5000

# تشغيل التطبيق
echo "تشغيل الخادم على http://0.0.0.0:5000"
python run.py