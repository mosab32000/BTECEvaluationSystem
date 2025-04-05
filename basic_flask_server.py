#!/usr/bin/env python3
"""
خادم Flask بسيط جدًا لنظام تقييم BTEC
"""

import os
from flask import Flask, send_file, jsonify

app = Flask(__name__)

@app.route('/')
def index():
    """الصفحة الرئيسية"""
    return send_file('index.html')

@app.route('/health')
def health():
    """التحقق من صحة النظام"""
    return jsonify({"status": "ok"})

if __name__ == '__main__':
    print("Starting BTEC Basic Server on port 5000...")
    app.run(host='0.0.0.0', port=5000, debug=True)