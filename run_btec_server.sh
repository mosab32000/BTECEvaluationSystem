#!/bin/bash
# هذا البرنامج يقوم بتشغيل خادم تقييم BTEC على المنفذ 3000

# التأكد من قتل أي عمليات سابقة تستخدم المنفذ 3000
echo "Stopping any existing processes on port 3000..."
lsof -i :3000 -t | xargs kill -9 2>/dev/null || true

# تشغيل التطبيق
echo "Starting BTEC Evaluation System on port 3000..."
export FLASK_APP=backend.wsgi
export FLASK_ENV=development
export PYTHONPATH=$(pwd)
python -m flask run --host=0.0.0.0 --port=3000