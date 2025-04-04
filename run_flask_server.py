"""
نقطة الدخول الرئيسية لتطبيق نظام تقييم BTEC - نسخة مبسطة
"""

import os
import logging
from flask import Flask, jsonify, send_from_directory, send_file
from flask_cors import CORS

# إعداد التسجيل
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# إنشاء تطبيق Flask
app = Flask(__name__, static_folder='static')

# تكوين التطبيق
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'default-secret-key')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', 'default-jwt-key')

# إعداد التصفية المتقاطعة (CORS)
CORS(app, resources={r"/api/*": {"origins": "*"}})

# إضافة نقطة نهاية للتحقق من صحة النظام
@app.route('/health')
def health():
    return jsonify({'status': 'ok'})

@app.route('/')
def index():
    return send_file('index.html')

@app.route('/login')
def login():
    return jsonify({
        'message': 'صفحة تسجيل الدخول قيد التطوير',
        'status': 'under_development'
    })

@app.route('/register')
def register():
    return jsonify({
        'message': 'صفحة التسجيل الجديد قيد التطوير',
        'status': 'under_development'
    })

@app.route('/api/info')
def api_info():
    return jsonify({
        'name': 'BTEC Evaluation System API',
        'status': 'running',
        'version': '1.0.0'
    })

@app.route('/static/<path:path>')
def serve_static(path):
    return send_from_directory('static', path)

if __name__ == '__main__':
    # الحصول على المنفذ من البيئة أو استخدام 3000 كقيمة افتراضية
    port = int(os.environ.get('PORT', 3000))
    logger.info(f"بدء تشغيل نظام تقييم BTEC على المنفذ {port}...")
    
    app.run(host='0.0.0.0', port=port, debug=True)