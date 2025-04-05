#!/bin/bash

echo "بدء تشغيل نظام تقييم BTEC..."

# التأكد من وجود المجلدات الضرورية
mkdir -p logs
mkdir -p data
mkdir -p app/static/{css,js,img}
mkdir -p app/templates/{auth,admin,evaluation}

# تحديد المتغيرات البيئية
export FLASK_APP=app
export FLASK_ENV=development
export FLASK_DEBUG=1

# تشغيل التطبيق
python wsgi.py