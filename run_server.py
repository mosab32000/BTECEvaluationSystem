#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ملف تشغيل خادم نظام تقييم BTEC
"""

import os
import sys
import time
import signal
import logging
import subprocess
import atexit
from datetime import datetime
from dotenv import load_dotenv

# تهيئة السجلات
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(os.path.join(os.path.dirname(__file__), 'logs', 'server.log'), mode='a')
    ]
)
logger = logging.getLogger('btec_server')

# تحميل متغيرات البيئة
load_dotenv()

# إنشاء المجلدات الضرورية
os.makedirs(os.path.join(os.path.dirname(__file__), 'logs'), exist_ok=True)
os.makedirs(os.path.join(os.path.dirname(__file__), 'uploads'), exist_ok=True)
os.makedirs(os.path.join(os.path.dirname(__file__), 'static', 'uploads'), exist_ok=True)

def ensure_environment():
    """ضمان وجود متغيرات البيئة الضرورية"""
    # قائمة المتغيرات المطلوبة
    required_vars = [
        "SECRET_KEY",
        "JWT_SECRET_KEY",
        "WTF_CSRF_SECRET_KEY",
        "DATABASE_URL"
    ]
    
    # التحقق من وجود المتغيرات
    missing_vars = []
    for var in required_vars:
        if var not in os.environ:
            missing_vars.append(var)
    
    # إنشاء ملف .env إذا لم يكن موجوداً
    if missing_vars:
        logger.warning(f"المتغيرات التالية مفقودة: {', '.join(missing_vars)}")
        logger.info("جاري تشغيل script إعداد قاعدة البيانات...")
        
        try:
            setup_result = subprocess.run(
                [sys.executable, 'init_db.py'],
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            logger.info("تم إعداد قاعدة البيانات بنجاح")
            logger.debug(setup_result.stdout)
        except subprocess.CalledProcessError as e:
            logger.error(f"فشل في إعداد قاعدة البيانات: {e}")
            logger.error(e.stderr)
            sys.exit(1)

def run_server():
    """تشغيل خادم Flask"""
    server_pid_file = os.path.join(os.path.dirname(__file__), 'server.pid')
    
    # التحقق مما إذا كان الخادم يعمل بالفعل
    if os.path.exists(server_pid_file):
        with open(server_pid_file, 'r') as f:
            pid = f.read().strip()
            if pid:
                try:
                    pid = int(pid)
                    os.kill(pid, 0)  # اختبار ما إذا كانت العملية موجودة
                    logger.warning(f"الخادم يعمل بالفعل مع PID {pid}")
                    return
                except (OSError, ValueError):
                    # العملية غير موجودة أو PID غير صالح
                    logger.info("تم العثور على ملف PID قديم، سيتم إنشاء خادم جديد")
    
    # تحديد نوع البيئة
    flask_env = os.environ.get("FLASK_ENV", "development")
    
    # اختيار طريقة التشغيل بناءً على نوع البيئة
    if flask_env == "production":
        # استخدام Gunicorn في بيئة الإنتاج
        cmd = [
            "gunicorn",
            "--config=gunicorn_config.py",
            "wsgi:app"
        ]
    else:
        # استخدام خادم Flask المضمّن في بيئة التطوير
        cmd = [
            sys.executable,
            "wsgi.py"
        ]
    
    # فتح ملف لحفظ مخرجات الخادم
    log_file = open(os.path.join(os.path.dirname(__file__), 'logs', 'server_output.log'), 'a')
    
    # كتابة رسالة بدء تشغيل جديدة في ملف السجل
    log_file.write(f"\n{'='*50}\n")
    log_file.write(f"بدء تشغيل خادم BTEC في {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    log_file.write(f"{'='*50}\n\n")
    log_file.flush()
    
    # بدء تشغيل الخادم
    logger.info(f"بدء تشغيل خادم BTEC في وضع {flask_env}...")
    server_process = subprocess.Popen(
        cmd,
        stdout=log_file,
        stderr=log_file,
        text=True
    )
    
    # حفظ PID في ملف
    with open(server_pid_file, 'w') as f:
        f.write(str(server_process.pid))
    
    logger.info(f"تم بدء تشغيل الخادم بنجاح مع PID {server_process.pid}")
    
    # تنظيف عند الخروج
    def cleanup():
        if server_process.poll() is None:  # إذا كانت العملية ما زالت تعمل
            logger.info("إيقاف الخادم...")
            server_process.terminate()
            try:
                server_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                logger.warning("لم يستجب الخادم، سيتم إجباره على الإيقاف...")
                server_process.kill()
        
        # إغلاق ملف السجل
        log_file.close()
        
        # إزالة ملف PID
        if os.path.exists(server_pid_file):
            os.remove(server_pid_file)
        
        logger.info("تم إيقاف الخادم وتنظيف الموارد")
    
    # تسجيل دالة التنظيف
    atexit.register(cleanup)
    
    # التعامل مع إشارات النظام
    def signal_handler(sig, frame):
        logger.info(f"تم استلام إشارة {sig}, إيقاف الخادم...")
        cleanup()
        sys.exit(0)
    
    # تسجيل معالج الإشارات
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # الانتظار حتى يتم إيقاف الخادم
    try:
        while True:
            # التحقق من حالة العملية
            if server_process.poll() is not None:
                logger.error(f"توقف الخادم بشكل غير متوقع مع رمز الخروج {server_process.returncode}")
                # إعادة تشغيل الخادم
                logger.info("إعادة تشغيل الخادم...")
                time.sleep(2)
                server_process = subprocess.Popen(
                    cmd,
                    stdout=log_file,
                    stderr=log_file,
                    text=True
                )
                with open(server_pid_file, 'w') as f:
                    f.write(str(server_process.pid))
                logger.info(f"تم إعادة تشغيل الخادم مع PID {server_process.pid}")
            
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("تم إيقاف الخادم بواسطة المستخدم")
        cleanup()
        sys.exit(0)

if __name__ == "__main__":
    # ضمان وجود متغيرات البيئة اللازمة
    ensure_environment()
    
    # تشغيل الخادم
    run_server()