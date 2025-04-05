#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
خادم بسيط لعرض نظام تقييم BTEC
"""

import os
import logging
from flask import Flask, render_template, send_from_directory, jsonify

# إعداد التسجيل
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# إنشاء تطبيق Flask
app = Flask(__name__, 
            static_folder='static', 
            template_folder='templates')

# تكوين سري للتطبيق
app.secret_key = os.environ.get('SECRET_KEY', os.urandom(24).hex())

@app.route('/')
def index():
    """الصفحة الرئيسية"""
    return render_template('index.html')

@app.route('/static/<path:path>')
def static_file(path):
    """الملفات الثابتة"""
    return send_from_directory('static', path)

@app.route('/api/health')
def health():
    """التحقق من الصحة"""
    return jsonify({
        'status': 'ok',
        'version': '1.0'
    })

@app.route('/castle-grok')
def castle_grok():
    """صفحة قلعة Grok الأسطورية"""
    return render_template('castle_grok.html')

@app.route('/mudaqqiq')
def mudaqqiq():
    """صفحة منصة مُدقِّق"""
    return render_template('mudaqqiq.html')

# التعامل مع الأخطاء
@app.errorhandler(404)
def page_not_found(e):
    """معالجة خطأ 404 - الصفحة غير موجودة"""
    return render_template('404.html'), 404

@app.errorhandler(500)
def server_error(e):
    """معالجة خطأ 500 - خطأ في الخادم"""
    return render_template('500.html'), 500

# تشغيل التطبيق إذا تم تنفيذ هذا الملف مباشرة
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)