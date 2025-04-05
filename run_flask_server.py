"""
نقطة الدخول الرئيسية لتطبيق نظام تقييم BTEC - نسخة مبسطة
"""

import os
import logging
from dotenv import load_dotenv
from flask import Flask, render_template, jsonify, send_from_directory

# تحميل متغيرات البيئة من ملف .env
load_dotenv()

# إعداد التسجيل
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger('__main__')

# إنشاء تطبيق Flask
app = Flask(__name__, 
    static_folder='app/static',
    template_folder='app/templates'
)

# تعيين المفتاح السري
app.secret_key = os.environ.get('SECRET_KEY', os.urandom(24))

@app.route('/health')
def health():
    """
    نقطة نهاية للتحقق من صحة النظام
    """
    return jsonify({"status": "ok"})

@app.route('/')
def index():
    """
    الصفحة الرئيسية
    """
    return render_template('index.html')

@app.route('/login')
def login():
    """
    صفحة تسجيل الدخول
    """
    return render_template('auth/login.html')

@app.route('/register')
def register():
    """
    صفحة إنشاء حساب جديد
    """
    return render_template('auth/register.html')

@app.route('/api/info')
def api_info():
    """
    معلومات عن واجهة برمجة التطبيقات
    """
    return jsonify({
        "name": "BTEC Evaluation System API",
        "version": "1.0.0",
        "description": "واجهة برمجة التطبيقات لنظام تقييم BTEC"
    })

@app.route('/static/<path:path>')
def serve_static(path):
    """
    خدمة الملفات الثابتة
    """
    return send_from_directory('app/static', path)

"""
Script to run the Flask server for BTEC Evaluation System
"""

def main():
    """
    Run the Flask development server
    """
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', '1') == '1'
    
    logger.info(f"بدء تشغيل نظام تقييم BTEC على المنفذ {port}...")
    app.run(host="0.0.0.0", port=port, debug=debug)

if __name__ == '__main__':
    main()
