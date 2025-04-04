"""
نقطة الدخول الرئيسية لتطبيق نظام تقييم BTEC
"""
import os
import logging
from flask import Flask, jsonify, render_template, send_from_directory, request
from app import create_app

# إعداد السجل
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s [%(levelname)s] - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('server.log')
    ]
)

# إنشاء تطبيق Flask
app = create_app(os.getenv('FLASK_ENV', 'development'))

@app.route('/health')
def health():
    """
    نقطة نهاية للتحقق من صحة النظام
    """
    return jsonify({
        'status': 'success',
        'message': 'BTEC Evaluation System is running'
    })

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def catch_all(path):
    """
    التقاط جميع المسارات غير المعالجة وتوجيهها إلى القالب الأساسي
    """
    if path.startswith('static/'):
        return send_from_directory('.', path)
    
    if path.startswith('api/'):
        return jsonify({
            'status': 'error',
            'message': 'API endpoint not found'
        }), 404
    
    return render_template('index.html')

@app.errorhandler(404)
def page_not_found(e):
    """
    معالج الخطأ 404 - الصفحة غير موجودة
    """
    if request.path.startswith('/api/'):
        return jsonify({
            'status': 'error',
            'message': 'API endpoint not found'
        }), 404
    
    return render_template('index.html')

if __name__ == '__main__':
    # تشغيل الخادم على المنفذ 5000
    app.run(host='0.0.0.0', port=5000, debug=True)