"""
نقطة الدخول الرئيسية لتطبيق نظام تقييم BTEC
يقوم بتشغيل التطبيق على المنفذ 3000
"""

import os
from dotenv import load_dotenv
import logging
from app import create_app

# تهيئة السجل
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# تحميل المتغيرات البيئية
load_dotenv()

# إنشاء وتهيئة التطبيق
app = create_app()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 3000))
    logger.info(f"Starting BTEC Evaluation System on port {port}...")
    app.run(host='0.0.0.0', port=port, debug=True)