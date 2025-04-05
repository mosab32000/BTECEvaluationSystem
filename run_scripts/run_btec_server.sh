#!/bin/bash
# سكريبت لتشغيل خادم نظام تقييم BTEC

# وضع إعداد فشل السكريبت عند حدوث أي خطأ
set -e

# إنشاء المجلدات الضرورية
mkdir -p logs
mkdir -p uploads
mkdir -p static/uploads
mkdir -p data

# تعيين متغيرات بيئة التشغيل
export FLASK_APP=wsgi.py
export FLASK_ENV=${FLASK_ENV:-development}
export PORT=${PORT:-5000}

# عرض معلومات بدء التشغيل
echo "بدء تشغيل خادم نظام تقييم BTEC..."
echo "البيئة: $FLASK_ENV"
echo "المنفذ: $PORT"

# التحقق من الاتصال بقاعدة البيانات
echo "التحقق من اتصال قاعدة البيانات..."
python3 check_database.py

# تشغيل خادم BTEC
echo "بدء تشغيل الخادم..."
python3 run_btec_server.py
