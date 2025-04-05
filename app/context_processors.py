"""
معالجات السياق للقوالب
"""
import os
from datetime import datetime

def global_template_vars():
    """تعريف المتغيرات العامة للقوالب"""
    return {
        'app_name': 'BTEC Evaluation System',
        'app_version': '1.0.0',
        'current_year': datetime.now().year,
        'is_production': os.environ.get('FLASK_ENV') == 'production',
        'is_rtl': True,  # تمكين الدعم الكامل للغة العربية (RTL)
        'app_description': 'نظام تقييم BTEC - منصة تقييم متطورة مدعومة بالذكاء الاصطناعي'
    }