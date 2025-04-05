#!/bin/bash

# سكربت تشغيل نظام تقييم BTEC مع منصة مُدقِّق وقلعة Grok الأسطورية

echo "بدء تشغيل نظام تقييم BTEC الموحد..."

# التحقق من وجود ملف .env
if [ ! -f .env ]; then
    echo "إنشاء ملف .env افتراضي..."
    echo "SECRET_KEY=$(python -c 'import secrets; print(secrets.token_hex(32))')" > .env
    echo "FLASK_APP=btec_eval_server.py" >> .env
    echo "FLASK_ENV=development" >> .env
fi

# ضمان وجود المجلدات الضرورية
mkdir -p static templates logs

# تشغيل خادم نظام تقييم BTEC
echo "تشغيل خادم نظام تقييم BTEC..."
python btec_eval_server.py
