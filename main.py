"""
نقطة الدخول الرئيسية لتطبيق نظام تقييم BTEC
"""

import os
import logging
from app import create_app

# تهيئة السجل
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# إنشاء وتهيئة التطبيق
app = create_app()

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    logger.info(f"Starting BTEC Evaluation System server on port {port}")
    app.run(host="0.0.0.0", port=port, debug=True)