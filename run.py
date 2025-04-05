#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
نقطة الدخول المبسطة لتشغيل نظام تقييم BTEC
للاستخدام السريع أثناء التطوير
"""

import os
import sys
import logging
from dotenv import load_dotenv

# تهيئة السجلات
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(os.path.join(os.path.dirname(__file__), 'logs', 'dev.log'), mode='a')
    ]
)
logger = logging.getLogger('btec_dev')

# تحميل متغيرات البيئة
load_dotenv()

# ضمان وجود المجلدات الضرورية
os.makedirs(os.path.join(os.path.dirname(__file__), 'logs'), exist_ok=True)
os.makedirs(os.path.join(os.path.dirname(__file__), 'uploads'), exist_ok=True)
os.makedirs(os.path.join(os.path.dirname(__file__), 'static', 'uploads'), exist_ok=True)

# استيراد تطبيق Flask
from app import create_app
app = create_app()

if __name__ == "__main__":
    # تعيين المنفذ من متغيرات البيئة أو استخدام القيمة الافتراضية
    port = int(os.environ.get("PORT", 5000))
    
    logger.info(f"بدء تشغيل نظام تقييم BTEC على المنفذ {port}")
    
    # تشغيل التطبيق
    app.run(host="0.0.0.0", port=port, debug=True)