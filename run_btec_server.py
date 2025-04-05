#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
نقطة الدخول الرئيسية لتشغيل خادم نظام تقييم BTEC
تهدف هذه النقطة إلى تشغيل الخادم بشكل مستمر على Replit
"""

import os
import sys
import time
import signal
import logging
import secrets
import atexit
import subprocess
from datetime import datetime
from dotenv import load_dotenv
from gunicorn.app.wsgiapp import WSGIApplication

# تهيئة السجلات
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('logs/btec_server.log', 'a')
    ]
)
logger = logging.getLogger('btec_server')

# تحميل متغيرات البيئة
load_dotenv()

# ضمان وجود المجلدات الضرورية
os.makedirs('logs', exist_ok=True)
os.makedirs('uploads', exist_ok=True)
os.makedirs('static/uploads', exist_ok=True)
os.makedirs('data', exist_ok=True)

def ensure_secret_key(env_var, length=32):
    """التأكد من وجود المفتاح السري، وإنشاء واحد جديد إذا لم يكن موجوداً"""
    if env_var not in os.environ:
        key = secrets.token_hex(length)
        os.environ[env_var] = key
        logger.info(f"تم إنشاء {env_var} جديد")
        
        # حفظ المفتاح في ملف .env إذا كان موجوداً
        if os.path.exists('.env'):
            with open('.env', 'a') as f:
                f.write(f"\n{env_var}={key}")
            logger.info(f"تم حفظ {env_var} في ملف .env")

def ensure_encryption_key():
    """التأكد من وجود مفتاح التشفير، وإنشاء واحد جديد إذا لم يكن موجوداً"""
    if "ENCRYPTION_KEY" not in os.environ:
        key = secrets.token_hex(16)  # 32 حرف (16 بايت)
        os.environ["ENCRYPTION_KEY"] = key
        logger.info("تم إنشاء مفتاح تشفير جديد")
        
        # حفظ المفتاح في ملف .env إذا كان موجوداً
        if os.path.exists('.env'):
            with open('.env', 'a') as f:
                f.write(f"\nENCRYPTION_KEY={key}")
            logger.info("تم حفظ مفتاح التشفير في ملف .env")

def check_database_connection():
    """التحقق من اتصال قاعدة البيانات"""
    logger.info("التحقق من اتصال قاعدة البيانات...")
    
    try:
        # تشغيل برنامج التحقق من قاعدة البيانات
        result = subprocess.run(
            [sys.executable, 'check_database.py'],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        logger.info("تم التحقق من قاعدة البيانات بنجاح")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"فشل التحقق من قاعدة البيانات: {e}")
        logger.error(e.stderr)
        return False

def setup_environment():
    """إعداد متغيرات البيئة الضرورية"""
    logger.info("إعداد متغيرات البيئة الضرورية...")
    
    # التأكد من وجود المفاتيح السرية
    ensure_secret_key("SECRET_KEY")
    ensure_secret_key("JWT_SECRET_KEY")
    ensure_secret_key("WTF_CSRF_SECRET_KEY")
    
    # التأكد من وجود مفتاح التشفير
    ensure_encryption_key()
    
    # التأكد من متغيرات البيئة الأخرى
    if "FLASK_ENV" not in os.environ:
        os.environ["FLASK_ENV"] = "development"
    
    if "PORT" not in os.environ:
        os.environ["PORT"] = "5000"
    
    if "FLASK_APP" not in os.environ:
        os.environ["FLASK_APP"] = "wsgi.py"
    
    logger.info("تم إعداد متغيرات البيئة بنجاح")

def init_database():
    """تهيئة قاعدة البيانات وإنشاء الجداول"""
    logger.info("تهيئة قاعدة البيانات...")
    
    try:
        # تشغيل برنامج تهيئة قاعدة البيانات
        result = subprocess.run(
            [sys.executable, 'init_db.py'],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        logger.info("تم تهيئة قاعدة البيانات بنجاح")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"فشل في تهيئة قاعدة البيانات: {e}")
        logger.error(e.stderr)
        return False

def start_server():
    """بدء تشغيل الخادم"""
    logger.info("بدء تشغيل خادم نظام تقييم BTEC...")
    
    # تحديد ملف PID للخادم
    pid_file = 'server.pid'
    
    # التحقق مما إذا كان الخادم يعمل بالفعل
    if os.path.exists(pid_file):
        try:
            with open(pid_file, 'r') as f:
                pid = int(f.read().strip())
            # التحقق مما إذا كانت العملية موجودة
            os.kill(pid, 0)
            logger.info(f"الخادم يعمل بالفعل مع PID {pid}")
            return
        except (FileNotFoundError, ValueError, OSError):
            # العملية غير موجودة أو ملف PID غير صالح
            logger.info("الملف PID غير صالح، سيتم إنشاء خادم جديد")
    
    # تحديد بيئة التشغيل
    env = os.environ.get("FLASK_ENV", "development")
    
    # فتح ملف لحفظ مخرجات الخادم
    log_file = open('logs/server_output.log', 'a')
    
    # كتابة رسالة بدء تشغيل جديدة في ملف السجل
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_file.write(f"\n{'='*50}\n")
    log_file.write(f"بدء تشغيل خادم BTEC في {timestamp} (بيئة: {env})\n")
    log_file.write(f"{'='*50}\n\n")
    log_file.flush()
    
    # بدء تشغيل الخادم باستخدام Gunicorn
    logger.info(f"بدء تشغيل خادم Gunicorn في بيئة {env}...")
    
    # تنظيف الموارد عند الخروج
    def cleanup():
        log_file.close()
        if os.path.exists(pid_file):
            os.remove(pid_file)
        logger.info("تم تنظيف الموارد وإيقاف الخادم")
    
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
    
    try:
        # تكوين تطبيق Gunicorn
        class GunicornApp(WSGIApplication):
            def init(self, parser, opts, args):
                # تعيين الخيارات
                self.cfg.set("bind", f"0.0.0.0:{os.environ.get('PORT', '5000')}")
                self.cfg.set("workers", "2")
                self.cfg.set("threads", "2")
                self.cfg.set("accesslog", "-")
                self.cfg.set("errorlog", "-")
                self.cfg.set("reload", env == "development")
                self.cfg.set("timeout", "120")
                self.cfg.set("worker_class", "sync")
                self.cfg.set("proc_name", "btec_server")
                self.cfg.set("loglevel", "info")
                
                # حفظ PID في ملف
                self.cfg.set("pidfile", pid_file)
                
                return args
            
            def load(self):
                # استيراد تطبيق Flask
                from wsgi import app
                return app
        
        # تشغيل Gunicorn بالخيارات المحددة
        GunicornApp().run()
        
    except Exception as e:
        logger.error(f"خطأ أثناء تشغيل الخادم: {e}")
        cleanup()
        return False
    
    return True

def main():
    """الدالة الرئيسية"""
    logger.info("بدء تشغيل نظام تقييم BTEC...")
    
    # إعداد متغيرات البيئة
    setup_environment()
    
    # التحقق من اتصال قاعدة البيانات
    if not check_database_connection():
        logger.error("فشل الاتصال بقاعدة البيانات، إنهاء العملية")
        sys.exit(1)
    
    # تهيئة قاعدة البيانات
    if not init_database():
        logger.error("فشل تهيئة قاعدة البيانات، إنهاء العملية")
        sys.exit(1)
    
    # بدء تشغيل الخادم
    start_server()

if __name__ == "__main__":
    main()