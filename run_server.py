"""
ملف تشغيل خادم نظام تقييم BTEC
"""
import os
import logging
import secrets
from pathlib import Path

from flask import Flask, jsonify, render_template

# إعداد التسجيل
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def ensure_environment():
    """ضمان وجود متغيرات البيئة الضرورية"""
    # ضمان وجود مفتاح سري
    if 'SECRET_KEY' not in os.environ:
        os.environ['SECRET_KEY'] = secrets.token_hex(32)
        logger.info("تم إنشاء SECRET_KEY")
    
    # ضمان وجود مفتاح JWT
    if 'JWT_SECRET_KEY' not in os.environ:
        os.environ['JWT_SECRET_KEY'] = secrets.token_hex(32)
        logger.info("تم إنشاء JWT_SECRET_KEY")
    
    # ضمان وجود مفتاح تشفير
    if 'ENCRYPTION_KEY' not in os.environ:
        os.environ['ENCRYPTION_KEY'] = secrets.token_urlsafe(32)
        logger.info("تم إنشاء ENCRYPTION_KEY")

    # إعداد وضع التصحيح
    if 'FLASK_DEBUG' not in os.environ:
        os.environ['FLASK_DEBUG'] = 'True'
    
    # إعداد مجلد التحميلات
    upload_dir = Path('uploads')
    if not upload_dir.exists():
        upload_dir.mkdir(parents=True)
        logger.info("تم إنشاء مجلد uploads")
    
    # إعداد مجلد السجلات
    logs_dir = Path('logs')
    if not logs_dir.exists():
        logs_dir.mkdir(parents=True)
        logger.info("تم إنشاء مجلد logs")

def run_server():
    """تشغيل خادم Flask"""
    # ضمان وجود متغيرات البيئة
    ensure_environment()
    
    try:
        # استيراد التطبيق
        from app import create_app
        
        # إنشاء تطبيق Flask
        app = create_app()
        
        # تعيين متغيرات التشغيل
        host = os.environ.get('HOST', '0.0.0.0')
        port = int(os.environ.get('PORT', 5000))
        debug = os.environ.get('FLASK_DEBUG', 'True').lower() == 'true'
        
        # تشغيل التطبيق
        logger.info(f"بدء تشغيل خادم نظام تقييم BTEC على {host}:{port} (وضع التصحيح: {debug})")
        app.run(host=host, port=port, debug=debug)
        
    except Exception as e:
        logger.error(f"خطأ أثناء تشغيل الخادم: {str(e)}")
        raise

if __name__ == "__main__":
    run_server()