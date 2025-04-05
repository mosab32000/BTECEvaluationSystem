"""
ملف تشغيل خادم نظام تقييم BTEC
"""
import os
import sys
import logging
import subprocess
import time
import signal
import atexit
from pathlib import Path
from dotenv import load_dotenv

# إعداد التسجيل
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('server.log')
    ]
)

logger = logging.getLogger(__name__)

# تحميل متغيرات البيئة
if os.path.exists('.env'):
    load_dotenv()
    logger.info("تم تحميل ملف .env")

def ensure_environment():
    """ضمان وجود متغيرات البيئة الضرورية"""
    # التأكد من متغيرات البيئة الأساسية
    required_vars = ['DATABASE_URL', 'SECRET_KEY', 'JWT_SECRET_KEY']
    missing_vars = [var for var in required_vars if not os.environ.get(var)]
    
    if missing_vars:
        logger.error(f"متغيرات البيئة المفقودة: {', '.join(missing_vars)}")
        logger.error("يرجى إنشاء ملف .env مع المتغيرات المطلوبة")
        sys.exit(1)
    
    # التأكد من وجود المجلدات الضرورية
    for folder in ['logs', 'static', 'templates']:
        os.makedirs(folder, exist_ok=True)

def run_server():
    """تشغيل خادم Flask"""
    try:
        # تهيئة قاعدة البيانات إذا كانت غير موجودة
        if not Path('instance').exists() or not any(Path('instance').iterdir()):
            logger.info("إعداد قاعدة البيانات...")
            subprocess.run([sys.executable, 'init_db.py'], check=True)
        
        # تشغيل التطبيق
        logger.info("بدء تشغيل خادم Flask...")
        
        # حفظ PID لإغلاق التطبيق لاحقاً
        with open('server.pid', 'w') as f:
            f.write(str(os.getpid()))
        
        # تسجيل دالة التنظيف
        def cleanup():
            if os.path.exists('server.pid'):
                os.remove('server.pid')
            logger.info("تم إغلاق الخادم")
        
        atexit.register(cleanup)
        
        # معالج إشارات النظام
        def signal_handler(sig, frame):
            logger.info(f"تم استلام الإشارة {sig}، جاري إغلاق الخادم...")
            sys.exit(0)
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        # تنفيذ أمر التشغيل
        port = int(os.environ.get('PORT', 5000))
        subprocess.run([
            sys.executable, 'run.py'
        ], check=True)
        
    except subprocess.CalledProcessError as e:
        logger.error(f"فشل تشغيل الخادم: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"حدث خطأ أثناء تنفيذ الخادم: {e}")
        sys.exit(1)

if __name__ == "__main__":
    ensure_environment()
    run_server()