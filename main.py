"""
نقطة الدخول الرئيسية لتطبيق نظام تقييم BTEC
يقوم بتشغيل التطبيق على المنفذ 3000
"""

import os
import logging
from flask import Flask, render_template, send_from_directory
from dotenv import load_dotenv

# إعداد التسجيل
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger(__name__)

# تحميل متغيرات البيئة
load_dotenv()

# إنشاء تطبيق Flask
app = Flask(__name__, static_folder='static')
app.secret_key = os.environ.get("SECRET_KEY") or "you-will-never-guess"

@app.route('/')
def index():
    """الصفحة الرئيسية"""
    return send_from_directory('static', 'index.html')

@app.route('/health')
def health():
    """التحقق من صحة النظام"""
    return {"status": "healthy", "name": "BTEC Evaluation System"}

@app.route('/static/<path:path>')
def static_files(path):
    """عرض الملفات الثابتة"""
    return send_from_directory('static', path)

if __name__ == '__main__':
    # تشغيل التطبيق
    port = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=port, debug=True)