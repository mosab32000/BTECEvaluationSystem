"""
المسارات الرئيسية في نظام تقييم BTEC
"""

from flask import render_template, redirect, url_for, request, jsonify
from app.routes import main_bp
import logging

logger = logging.getLogger(__name__)

@main_bp.route('/')
def index():
    """الصفحة الرئيسية"""
    logger.debug("عرض الصفحة الرئيسية")
    return render_template('index.html')

@main_bp.route('/about')
def about():
    """صفحة نبذة عن النظام"""
    return render_template('about.html')

@main_bp.route('/health')
def health():
    """
    نقطة نهاية للتحقق من صحة النظام
    """
    from datetime import datetime
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0"
    })