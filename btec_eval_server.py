#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
نظام تقييم BTEC - خادم الويب الرئيسي
يقدم واجهة بسيطة وجذابة للنظام مع تكامل منصة مُدقِّق وقلعة Grok الأسطورية
"""

import os
import logging
import secrets
from flask import Flask, request, render_template, send_file, send_from_directory, redirect, url_for, jsonify

# إعداد التسجيل
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('server.log', 'a')
    ]
)
logger = logging.getLogger('btec_eval_server')

# إنشاء تطبيق Flask
app = Flask(__name__, 
            static_folder='static',
            static_url_path='/static')

# التأكد من وجود المفتاح السري
if 'SECRET_KEY' not in os.environ:
    os.environ['SECRET_KEY'] = secrets.token_hex(32)
    logger.info("تم إنشاء مفتاح سري جديد")

app.secret_key = os.environ.get('SECRET_KEY')

# الطرق (Routes)

@app.route('/')
def index():
    """الصفحة الرئيسية"""
    return send_file('index.html')

@app.route('/castle-grok')
def castle_grok():
    """صفحة قلعة Grok الأسطورية"""
    return send_file('static/castle_grok.html')

@app.route('/static/<path:path>')
def serve_static(path):
    """تقديم الملفات الثابتة"""
    return send_from_directory('static', path)

@app.route('/api/health')
def health():
    """فحص صحة النظام"""
    return jsonify({"status": "ok", "version": "1.0"})

@app.route('/api/evaluate', methods=['POST'])
def evaluate():
    """تقييم مهمة باستخدام الذكاء الاصطناعي"""
    try:
        data = request.get_json()
        task_title = data.get('task_title', '')
        task_description = data.get('task_description', '')
        
        # محاكاة نتيجة التقييم (في تطبيق حقيقي، هذا سيكون طلب لواجهة برمجة التطبيقات للذكاء الاصطناعي)
        evaluation_result = {
            "score": 85,
            "feedback": "عمل جيد، مع بعض النقاط التي يمكن تحسينها.",
            "strengths": ["الهيكل العام واضح", "التحليل مفصل", "الأمثلة مناسبة"],
            "areas_for_improvement": ["يحتاج إلى توثيق أفضل", "بعض المفاهيم تحتاج إلى شرح أعمق"]
        }
        
        logger.info(f"تم تقييم مهمة: {task_title}")
        return jsonify({"success": True, "result": evaluation_result})
    
    except Exception as e:
        logger.error(f"خطأ في تقييم المهمة: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/chat', methods=['POST'])
def chat():
    """دردشة مع Grok"""
    try:
        data = request.get_json()
        user_message = data.get('message', '')
        
        # محاكاة رد Grok (في تطبيق حقيقي، هذا سيكون طلب لنموذج لغوي كبير)
        grok_response = "أيها البطل الشجاع، أشكرك على رسالتك. سأساعدك في رحلتك التعليمية لإتقان معايير BTEC. تذكر دائماً أن كل تحدٍ هو فرصة للنمو والتعلم."
        
        logger.info(f"تم استلام رسالة من المستخدم: {user_message[:50]}...")
        return jsonify({"success": True, "response": grok_response})
    
    except Exception as e:
        logger.error(f"خطأ في الدردشة: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.errorhandler(404)
def page_not_found(e):
    """معالجة خطأ 404 - الصفحة غير موجودة"""
    return render_template('error.html', error_code=404, error_message="الصفحة غير موجودة"), 404

@app.errorhandler(500)
def server_error(e):
    """معالجة خطأ 500 - خطأ في الخادم"""
    return render_template('error.html', error_code=500, error_message="خطأ في الخادم"), 500

# تشغيل التطبيق
if __name__ == '__main__':
    logger.info("بدء تشغيل خادم نظام تقييم BTEC...")
    
    # ضمان وجود المجلدات الضرورية
    os.makedirs('static', exist_ok=True)
    os.makedirs('templates', exist_ok=True)
    
    # ضمان وجود الملفات الرئيسية
    if not os.path.exists('templates/error.html'):
        with open('templates/error.html', 'w') as f:
            f.write("""<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>خطأ {{ error_code }} - نظام تقييم BTEC</title>
    <style>
        body {
            font-family: 'Cairo', sans-serif;
            background-color: #f8f9fa;
            color: #333;
            margin: 0;
            padding: 0;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            text-align: center;
        }
        
        .error-container {
            max-width: 600px;
            padding: 40px;
            background-color: #fff;
            border-radius: 10px;
            box-shadow: 0 0 20px rgba(0, 0, 0, 0.1);
        }
        
        h1 {
            color: #dc3545;
            font-size: 3em;
            margin-bottom: 10px;
        }
        
        p {
            font-size: 1.2em;
            margin-bottom: 20px;
        }
        
        a {
            display: inline-block;
            padding: 10px 20px;
            background-color: #007bff;
            color: #fff;
            text-decoration: none;
            border-radius: 5px;
            font-weight: bold;
            transition: background-color 0.3s;
        }
        
        a:hover {
            background-color: #0056b3;
        }
    </style>
</head>
<body>
    <div class="error-container">
        <h1>خطأ {{ error_code }}</h1>
        <p>{{ error_message }}</p>
        <a href="/">العودة إلى الصفحة الرئيسية</a>
    </div>
</body>
</html>""")
    
    # تشغيل الخادم
    app.run(host='0.0.0.0', port=5000, debug=True)