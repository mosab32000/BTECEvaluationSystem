#!/bin/bash

# هذا السكريبت يقوم بتشغيل خادم نظام تقييم BTEC

# التأكد من وجود الملفات والمجلدات الضرورية
mkdir -p logs static/css static/js

# إنشاء المفتاح السري إذا لم يكن موجودًا
if [ ! -f .env ]; then
    echo "إنشاء ملف .env"
    python -c "import secrets; print(f'SECRET_KEY={secrets.token_hex(32)}')" > .env
    python -c "import secrets; print(f'JWT_SECRET_KEY={secrets.token_hex(32)}')" >> .env
    python -c "from cryptography.fernet import Fernet; print(f'ENCRYPTION_KEY={Fernet.generate_key().decode()}')" >> .env
    echo "FLASK_ENV=development" >> .env
    echo "FLASK_CONFIG=development" >> .env
    echo "DATABASE_URL=sqlite:///btec.db" >> .env
fi

# إنشاء قاعدة البيانات إذا لم تكن موجودة
python -c "from app import create_app; from app.extensions import db; app = create_app(); app.app_context().push(); db.create_all()"

# تشغيل الخادم
echo "بدء تشغيل خادم BTEC..."
python wsgi.py
