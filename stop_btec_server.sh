#!/bin/bash
# سكريبت لإيقاف خادم نظام تقييم BTEC

# البحث عن عملية gunicorn وإيقافها
if pgrep -f "gunicorn.*app:create_app" > /dev/null; then
    echo "إيقاف خادم BTEC..."
    pkill -f "gunicorn.*app:create_app"
    echo "تم إيقاف الخادم بنجاح."
else
    echo "لا توجد عملية خادم BTEC نشطة."
fi
