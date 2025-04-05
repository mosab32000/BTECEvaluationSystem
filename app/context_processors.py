"""
معالجات السياق للقوالب
"""
import datetime

def global_template_vars():
    """تعريف المتغيرات العامة للقوالب"""
    return {
        'current_year': datetime.datetime.now().year,
        'app_version': '1.0.0',
        'site_name': 'نظام تقييم BTEC',
        'site_description': 'منصة متكاملة لتقييم مهام BTEC باستخدام الذكاء الاصطناعي وتقنية البلوكتشين',
        'support_email': 'support@btec-eval.com'
    }