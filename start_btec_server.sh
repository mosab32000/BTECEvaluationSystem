#!/bin/bash

# سكريبت لبدء تشغيل خادم نظام تقييم BTEC

# التأكد من وجود البيئة الافتراضية وتنشيطها (اختياري)
# if [ -d "venv" ]; then
#     echo "تنشيط البيئة الافتراضية..."
#     source venv/bin/activate
# fi

# تصدير متغيرات البيئة الضرورية
export FLASK_APP=run.py
export FLASK_ENV=${FLASK_ENV:-development}
export PORT=${PORT:-5000}

# التحقق من وجود ملف .env وتحميله
if [ -f .env ]; then
    echo "تحميل متغيرات البيئة من ملف .env..."
    set -a
    source .env
    set +a
fi

# التحقق مما إذا كان الخادم قيد التشغيل بالفعل
if [ -f server.pid ]; then
    PID=$(cat server.pid)
    if ps -p $PID > /dev/null; then
        echo "الخادم قيد التشغيل بالفعل مع PID: $PID"
        echo "لإيقاف الخادم، استخدم: kill $PID"
        exit 1
    else
        echo "إزالة ملف PID القديم..."
        rm server.pid
    fi
fi

# إنشاء مجلد السجلات إذا لم يكن موجودًا
mkdir -p logs

echo "بدء تشغيل خادم نظام تقييم BTEC..."

# في وضع الإنتاج، استخدم gunicorn
if [ "$FLASK_ENV" == "production" ]; then
    echo "تشغيل الخادم في وضع الإنتاج باستخدام gunicorn..."
    gunicorn -w 4 -b 0.0.0.0:$PORT run:app --daemon --pid server.pid --access-logfile logs/access.log --error-logfile logs/error.log
else
    # في وضع التطوير، استخدم خادم Flask المدمج
    echo "تشغيل الخادم في وضع التطوير باستخدام Flask..."
    python run.py > logs/flask.log 2>&1 &
    echo $! > server.pid
fi

echo "تم بدء تشغيل الخادم على المنفذ: $PORT"
echo "PID: $(cat server.pid)"
echo "للتحقق من الخادم، اطلب: http://localhost:$PORT/health"
echo "للوصول إلى واجهة المستخدم، اطلب: http://localhost:$PORT/"
echo "لمتابعة سجلات الخادم، استخدم: tail -f logs/flask.log"
