"""
مسارات الصحة والحالة لنظام تقييم BTEC
"""

from flask import Blueprint, jsonify

health_bp = Blueprint('health', __name__)

@health_bp.route('/health')
def health_check():
    """التحقق من صحة النظام"""
    return jsonify({"status": "ok"})
