"""
تشغيل تطبيق نظام تقييم BTEC
"""

import os
import sys
import logging
import argparse
from dotenv import load_dotenv

# تضمين الدليل الحالي في مسار البحث
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# تحميل متغيرات البيئة
load_dotenv()

from app import create_app

app = create_app()

def parse_args():
    """
    تحليل وسائط سطر الأوامر
    
    Returns:
        argparse.Namespace: الوسائط المحللة
    """
    parser = argparse.ArgumentParser(description='تشغيل نظام تقييم BTEC')
    parser.add_argument('--host', default='0.0.0.0', help='المضيف للاستماع عليه')
    parser.add_argument('--port', type=int, default=5000, help='منفذ التشغيل')
    parser.add_argument('--debug', action='store_true', help='وضع التصحيح')
    parser.add_argument('--reload', action='store_true', help='تمكين إعادة التحميل التلقائي')
    return parser.parse_args()

def configure_logging():
    """
    إعداد التسجيل
    """
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    log_level = os.environ.get('LOG_LEVEL', 'INFO').upper()
    
    # إعداد التسجيل للتطبيق
    logging.basicConfig(
        level=getattr(logging, log_level),
        format=log_format,
        handlers=[
            logging.FileHandler(os.environ.get('LOG_FILE', 'app.log')),
            logging.StreamHandler()
        ]
    )

if __name__ == '__main__':
    # إعداد التسجيل
    configure_logging()
    
    # تحليل الوسائط
    args = parse_args()
    
    # تكوين وضع التشغيل
    debug = args.debug or os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    use_reloader = args.reload or debug
    
    # تسجيل بدء التشغيل
    app.logger.info(f'بدء تشغيل التطبيق على {args.host}:{args.port} مع debug={debug}')
    
    # تشغيل التطبيق
    app.run(
        host=args.host,
        port=args.port,
        debug=debug,
        use_reloader=use_reloader
    )