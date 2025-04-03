#!/bin/bash

# تشغيل نظام تقييم BTEC

PORT=3000

echo "جاري بدء تشغيل نظام تقييم BTEC على المنفذ $PORT..."

# تشغيل سكريبت إعداد قاعدة البيانات
python init_db.py

# إنشاء مجلد static إذا لم يكن موجوداً ونسخ ملفات الواجهة
mkdir -p static
if [ -f index.html ]; then
    cp index.html static/
    echo "تم نسخ ملف index.html إلى مجلد static"
fi

# قتل أي عمليات سابقة كانت تعمل على نفس المنفذ
fuser -k $PORT/tcp 2>/dev/null

# تشغيل التطبيق
PORT=$PORT python main.py