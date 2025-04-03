"""
ملف تشغيل خادم نظام تقييم BTEC
"""

import os
from backend.app import create_app
from flask import jsonify
from dotenv import load_dotenv

# تحميل المتغيرات البيئية من ملف .env
load_dotenv()

app = create_app()

# إضافة نقطة صحة API لفحص الخادم
@app.route('/health')
def health():
    return jsonify({'status': 'healthy'}), 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=port, debug=True)