#!/bin/bash

# سكريبت تشغيل نظام تقييم BTEC مع منصة مُدقِّق وقلعة Grok الأسطورية
# تشغيل النظام المتكامل بكل مكوناته

echo "بدء تشغيل نظام تقييم BTEC المتكامل مع منصة مُدقِّق وقلعة Grok الأسطورية..."

# التحقق من وجود ملف .env
if [ ! -f .env ]; then
    echo "إنشاء ملف .env افتراضي..."
    echo "SECRET_KEY=$(python -c 'import secrets; print(secrets.token_hex(32))')" > .env
    echo "FLASK_APP=app.py" >> .env
    echo "FLASK_ENV=development" >> .env
    echo "DATABASE_URL=sqlite:///btec_system.db" >> .env
    echo "JWT_SECRET_KEY=$(python -c 'import secrets; print(secrets.token_hex(32))')" >> .env
    echo "MUDAQQIQ_URL=http://localhost:5001" >> .env
fi

# التحقق من وجود قاعدة البيانات وإنشائها إذا لم تكن موجودة
if [ ! -f btec_system.db ]; then
    echo "إنشاء قاعدة البيانات..."
    python init_db.py
fi

# بدء تشغيل خادم مُدقِّق في الخلفية
echo "بدء تشغيل منصة مُدقِّق..."
python run_mudaqqiq_server.py &
MUDAQQIQ_PID=$!

# انتظار بدء تشغيل خادم مُدقِّق
echo "انتظار بدء تشغيل منصة مُدقِّق..."
sleep 3

# بدء تشغيل خادم نظام تقييم BTEC
echo "بدء تشغيل نظام تقييم BTEC..."
python run_btec_server.py

# عند إنهاء الخادم الرئيسي، قم بإنهاء خادم مُدقِّق أيضًا
echo "إنهاء منصة مُدقِّق..."
kill $MUDAQQIQ_PID

echo "تم إنهاء النظام المتكامل."