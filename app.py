"""
نقطة الدخول الرئيسية لتطبيق نظام تقييم BTEC
يقوم بتشغيل التطبيق على المنفذ 5000
"""
import os
import logging
from app import create_app

# إعداد التسجيل
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# إنشاء تطبيق Flask
app = create_app(os.getenv('FLASK_CONFIG') or 'default')

@app.route('/health')
def health():
    """
    نقطة نهاية للتحقق من صحة النظام
    """
    return {
        'status': 'success',
        'message': 'نظام تقييم BTEC يعمل بشكل جيد'
    }

if __name__ == '__main__':
    # تشغيل التطبيق
    host = os.environ.get('HOST', '0.0.0.0')
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', 'True').lower() == 'true'
    
    logger.info(f"تشغيل نظام تقييم BTEC على {host}:{port}")
    app.run(host=host, port=port, debug=debug)