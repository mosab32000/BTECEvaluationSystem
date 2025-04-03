#!/bin/bash
# هذا البرنامج يقوم بتشغيل خادم تقييم BTEC على المنفذ 8000

# التأكد من قتل أي عمليات سابقة تستخدم المنفذ 8000
echo "Stopping any existing processes on port 8000..."
lsof -i :8000 -t | xargs kill -9 2>/dev/null || true

# تشغيل التطبيق
echo "Starting BTEC Evaluation System on port 8000..."
python backend/wsgi.py