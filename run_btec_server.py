#!/usr/bin/env python3
"""
سكريبت لتشغيل خادم نظام تقييم BTEC بشكل مستمر
"""
import os
import subprocess
import signal
import sys
import time
import atexit

def setup_environment():
    """إعداد متغيرات البيئة"""
    os.environ['FLASK_APP'] = 'app.py'
    os.environ['FLASK_ENV'] = 'production'
    os.environ['FLASK_DEBUG'] = '0'

def init_database():
    """تهيئة قاعدة البيانات"""
    print("تهيئة قاعدة البيانات...")
    subprocess.run(["python", "init_db.py"], check=True)

def start_server():
    """بدء تشغيل الخادم"""
    print("تشغيل خادم التطبيق...")
    cmd = ["gunicorn", "-c", "gunicorn_config.py", "app:create_app()"]
    server_process = subprocess.Popen(cmd)
    
    # تسجيل وظيفة لإيقاف الخادم عند الخروج
    def cleanup():
        if server_process.poll() is None:
            print("إيقاف الخادم...")
            server_process.terminate()
            server_process.wait(timeout=5)
    
    atexit.register(cleanup)
    
    # معالجة إشارات الخروج
    def signal_handler(sig, frame):
        print("تم استلام إشارة إيقاف...")
        cleanup()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    return server_process

def main():
    """الدالة الرئيسية"""
    setup_environment()
    init_database()
    server_process = start_server()
    
    print(f"تم بدء تشغيل خادم BTEC (PID: {server_process.pid})")
    print("الخادم يعمل الآن. اضغط Ctrl+C للإيقاف.")
    
    try:
        # الانتظار بشكل دوري للتحقق من حالة الخادم
        while True:
            if server_process.poll() is not None:
                print(f"انتهى الخادم بكود الخروج: {server_process.returncode}")
                # إعادة تشغيل الخادم إذا توقف
                print("إعادة تشغيل الخادم...")
                server_process = start_server()
                print(f"تم إعادة تشغيل الخادم (PID: {server_process.pid})")
            time.sleep(5)
    except KeyboardInterrupt:
        print("تم إيقاف التشغيل بواسطة المستخدم")

if __name__ == "__main__":
    main()
