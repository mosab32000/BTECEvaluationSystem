"""
نقطة الدخول الرئيسية لتطبيق نظام تقييم BTEC
"""
import os
import logging
from flask import Flask, render_template, jsonify

# ضبط تسجيل الأحداث
logging.basicConfig(level=logging.INFO,
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# استيراد التطبيق
from app import create_app

# إنشاء تطبيق Flask
app = create_app()

@app.route('/health')
def health():
    """
    نقطة نهاية للتحقق من صحة النظام
    """
    return jsonify({
        'status': 'ok',
        'message': 'نظام تقييم BTEC يعمل بشكل جيد'
    })

@app.route('/<path:path>')
def catch_all(path):
    """
    التقاط جميع المسارات غير المعالجة وتوجيهها إلى القالب الأساسي
    """
    return render_template('index.html')

@app.errorhandler(404)
def page_not_found(e):
    """
    معالج الخطأ 404 - الصفحة غير موجودة
    """
    return render_template('index.html')

if __name__ == "__main__":
    # تشغيل التطبيق
    host = os.environ.get('HOST', '0.0.0.0')
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    
    logger.info(f"تشغيل تطبيق نظام تقييم BTEC على {host}:{port} (وضع التصحيح: {debug})")
    app.run(host=host, port=port, debug=debug)