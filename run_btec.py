#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
سكربت بسيط لتشغيل خادم نظام تقييم BTEC
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
        logging.FileHandler('run_server.log', 'w')
    ]
)
logger = logging.getLogger('btec_runner')

def cleanup(pid=None):
    """إيقاف العمليات عند الخروج"""
    if pid:
        try:
            os.kill(pid, signal.SIGTERM)
            logger.info(f"تم إيقاف الخادم (PID: {pid})")
        except OSError:
            pass

def main():
    """الدالة الرئيسية لتشغيل خادم نظام تقييم BTEC"""
    logger.info("بدء تشغيل خادم نظام تقييم BTEC...")
    
    # التأكد من وجود ملف btec_eval_server.py
    if not os.path.exists('btec_eval_server.py'):
        logger.error("ملف btec_eval_server.py غير موجود!")
        return 1
    
    # إيقاف أي نسخة سابقة من الخادم
    try:
        subprocess.run(["pkill", "-f", "python btec_eval_server.py"], check=False)
        time.sleep(1)  # الانتظار للتأكد من إيقاف العمليات
    except Exception as e:
        logger.warning(f"خطأ أثناء محاولة إيقاف العمليات السابقة: {e}")
    
    # تشغيل خادم نظام تقييم BTEC
    try:
        logger.info("تشغيل خادم نظام تقييم BTEC...")
        process = subprocess.Popen(
            ["python", "btec_eval_server.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            bufsize=1
        )
        
        # تسجيل عملية التنظيف عند الخروج
        atexit.register(cleanup, process.pid)
        
        # الانتظار لبدء الخادم
        logger.info("الانتظار لبدء تشغيل الخادم...")
        time.sleep(3)
        
        # التحقق من حالة الخادم
        subprocess.run(["curl", "-s", "http://localhost:5000/api/health"], check=False)
        logger.info("تم تشغيل خادم نظام تقييم BTEC بنجاح!")
        
        # طباعة المخرجات من العملية
        for line in process.stdout:
            print(line, end='')
            sys.stdout.flush()
        
        # الانتظار لانتهاء العملية
        return_code = process.wait()
        logger.info(f"انتهى تشغيل الخادم برمز الخروج: {return_code}")
        return return_code
    
    except KeyboardInterrupt:
        logger.info("تم إيقاف الخادم بواسطة المستخدم.")
        return 0
    except Exception as e:
        logger.error(f"خطأ أثناء تشغيل الخادم: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())