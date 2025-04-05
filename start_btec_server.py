#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
سكريبت إطلاق خادم نظام تقييم BTEC بشكل متين
"""

import os
import sys
import logging
import subprocess
import time
import signal
import atexit

# إعداد التسجيل
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('server.log', 'w')
    ]
)
logger = logging.getLogger('btec_launcher')

def main():
    """الدالة الرئيسية للإطلاق"""
    logger.info("بدء تشغيل خادم نظام تقييم BTEC...")
    
    # إيقاف أي نسخة سابقة من الخادم
    try:
        subprocess.run(["pkill", "-f", "simple_btec_server.py"], check=False)
        time.sleep(1)
    except Exception as e:
        logger.warning(f"خطأ أثناء محاولة إيقاف العمليات السابقة: {e}")
    
    # تشغيل الخادم
    logger.info("إطلاق الخادم...")
    
    try:
        process = subprocess.Popen(
            ["python", "simple_btec_server.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True
        )
        
        # الانتظار لبدء الخادم
        time.sleep(2)
        
        logger.info(f"تم تشغيل الخادم بنجاح. PID: {process.pid}")
        
        # حفظ PID في ملف
        with open("server.pid", "w") as f:
            f.write(str(process.pid))
        
        # التحقق من صحة الخادم
        health_check = subprocess.run(
            ["curl", "-s", "http://localhost:5000/api/health"],
            capture_output=True,
            text=True,
            check=False
        )
        
        if health_check.returncode == 0:
            logger.info(f"تم التحقق من صحة الخادم: {health_check.stdout.strip()}")
            logger.info("الخادم جاهز للاستخدام على العنوان: http://localhost:5000/")
            return 0
        else:
            logger.error(f"فشل في التحقق من صحة الخادم. رمز الخروج: {health_check.returncode}")
            return 1
    
    except Exception as e:
        logger.error(f"حدث خطأ أثناء تشغيل الخادم: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())