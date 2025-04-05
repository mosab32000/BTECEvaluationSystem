#!/bin/bash

# سكريبت إيقاف خادم نظام تقييم BTEC

# الانتقال إلى المجلد الرئيسي للمشروع
cd "$(dirname "$0")/.."

# تحديد مسار ملف معرف العملية
PID_FILE="./server.pid"

# فحص إذا كان ملف معرف العملية موجودًا
if [ ! -f "$PID_FILE" ]; then
    echo "لم يتم العثور على ملف معرف العملية. يبدو أن الخادم ليس قيد التشغيل."
    exit 1
fi

# قراءة معرف العملية
PID=$(cat "$PID_FILE")

# فحص إذا كانت العملية ما زالت تعمل
if ! ps -p "$PID" > /dev/null; then
    echo "الخادم ليس قيد التشغيل (PID: $PID)."
    rm -f "$PID_FILE"
    exit 1
fi

# إيقاف العملية
echo "إيقاف خادم نظام تقييم BTEC (PID: $PID)..."
kill "$PID"

# انتظار إيقاف العملية
for i in {1..5}; do
    if ! ps -p "$PID" > /dev/null; then
        break
    fi
    echo "انتظار إيقاف الخادم... ($i/5)"
    sleep 1
done

# إجبار العملية على الإيقاف إذا لم تستجب
if ps -p "$PID" > /dev/null; then
    echo "الخادم لم يستجب، إيقاف إجباري..."
    kill -9 "$PID"
    sleep 1
fi

# إزالة ملف معرف العملية
rm -f "$PID_FILE"
echo "تم إيقاف خادم نظام تقييم BTEC بنجاح."
