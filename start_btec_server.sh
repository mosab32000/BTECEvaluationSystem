#!/bin/bash

# بدء تشغيل نظام تقييم BTEC

echo "جاري بدء تشغيل نظام تقييم BTEC..."

# تشغيل سكريبت إعداد قاعدة البيانات
python init_db.py

# إنشاء مجلد static إذا لم يكن موجوداً ونسخ ملفات الواجهة
mkdir -p static
if [ -f index.html ]; then
    cp index.html static/
    echo "تم نسخ ملف index.html إلى مجلد static"
fi

# تشغيل التطبيق بالملف الصحيح
python main.py