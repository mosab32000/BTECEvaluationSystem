"""
ملف تشغيل خادم نظام تقييم BTEC
"""

import os
from app import create_app
from flask import jsonify
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("server.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

app = create_app()

@app.route("/health/check")
def health():
    """
    نقطة نهاية للتحقق من صحة النظام
    """
    return jsonify({
        "status": "healthy",
        "service": "BTEC_REBEL_SYSTEM"
    })

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    logger.info(f"Starting BTEC Evaluation System server on port {port}")
    app.run(host="0.0.0.0", port=port, debug=True)