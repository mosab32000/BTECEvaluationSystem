#!/bin/bash

# سكريبت لإيقاف خادم نظام تقييم BTEC

if [ -f server.pid ]; then
    PID=$(cat server.pid)
    if ps -p $PID > /dev/null; then
        echo "إيقاف الخادم مع PID: $PID..."
        kill $PID
        sleep 2
        
        # التحقق مما إذا كان الخادم ما زال قيد التشغيل
        if ps -p $PID > /dev/null; then
            echo "الخادم لا يستجيب، إجباره على الإغلاق..."
            kill -9 $PID
        fi
        
        echo "تم إيقاف الخادم بنجاح"
    else
        echo "الخادم ليس قيد التشغيل، إزالة ملف PID القديم..."
    fi
    
    rm server.pid
else
    echo "لم يتم العثور على ملف PID، الخادم ليس قيد التشغيل"
fi
