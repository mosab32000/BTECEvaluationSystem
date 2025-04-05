"""
معالجات السياق لنظام تقييم BTEC
تستخدم لحقن متغيرات عامة في قوالب Jinja
"""

from datetime import datetime

def inject_globals():
    """
    حقن متغيرات عامة في جميع قوالب Jinja
    
    Returns:
        dict: قاموس المتغيرات العامة
    """
    return {
        "now": datetime.utcnow(),
        "app_name": "نظام تقييم BTEC",
        "app_version": "1.0.0",
        "app_description": "منصة متقدمة للتقييم الأكاديمي تستخدم الذكاء الاصطناعي"
    }
