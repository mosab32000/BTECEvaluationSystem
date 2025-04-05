"""
وحدة التكامل بين نظام تقييم BTEC ومنصة مُدقِّق
"""
import os
import sys
from flask import Blueprint, render_template, redirect, url_for, current_app, flash, jsonify

# إنشاء مخطط التكامل
btec_mudaqqiq = Blueprint('btec_mudaqqiq', __name__, 
                          template_folder='templates/mudaqqiq_integration',
                          static_folder='static/mudaqqiq',
                          static_url_path='/static/mudaqqiq')

@btec_mudaqqiq.route('/')
def index():
    """صفحة البداية لتكامل مُدقِّق"""
    return render_template('mudaqqiq_integration/index.html')

@btec_mudaqqiq.route('/dashboard')
def dashboard():
    """لوحة تحكم مُدقِّق ضمن نظام BTEC"""
    return render_template('mudaqqiq_integration/dashboard.html')

@btec_mudaqqiq.route('/launch')
def launch_mudaqqiq():
    """إطلاق منصة مُدقِّق بشكل مستقل"""
    try:
        # هنا يمكن إضافة منطق لبدء تشغيل خادم مُدقِّق
        # أو إعادة التوجيه إلى عنوان خادم مُدقِّق إذا كان يعمل بالفعل
        mudaqqiq_url = os.environ.get('MUDAQQIQ_URL', 'http://localhost:5001')
        return redirect(mudaqqiq_url)
    except Exception as e:
        current_app.logger.error(f"خطأ في إطلاق مُدقِّق: {str(e)}")
        flash("تعذر إطلاق منصة مُدقِّق. يرجى التحقق من سجلات النظام.", "error")
        return redirect(url_for('btec_mudaqqiq.index'))

@btec_mudaqqiq.route('/stats')
def api_stats():
    """واجهة برمجة التطبيقات للحصول على إحصائيات مُدقِّق"""
    try:
        # هنا يمكن استدعاء API الخاص بـ مُدقِّق للحصول على الإحصائيات
        stats = {
            'projects_count': 0,
            'users_count': 0,
            'reviews_count': 0,
            'status': 'ok'
        }
        return jsonify(stats)
    except Exception as e:
        current_app.logger.error(f"خطأ في الحصول على إحصائيات مُدقِّق: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)})

@btec_mudaqqiq.route('/castle_grok')
def castle_grok():
    """الوصول إلى قلعة Grok الأسطورية"""
    try:
        # هنا يمكن إضافة منطق للتحقق من الوصول أو المصادقة إذا لزم الأمر
        mudaqqiq_url = os.environ.get('MUDAQQIQ_URL', 'http://localhost:5001')
        return redirect(f"{mudaqqiq_url}/castle_grok")
    except Exception as e:
        current_app.logger.error(f"خطأ في الوصول إلى قلعة Grok: {str(e)}")
        flash("تعذر الوصول إلى قلعة Grok الأسطورية. يرجى التحقق من سجلات النظام.", "error")
        return redirect(url_for('btec_mudaqqiq.index'))

def register_mudaqqiq_integration(app):
    """
    تسجيل مخطط تكامل مُدقِّق في تطبيق Flask
    
    Args:
        app: تطبيق Flask الرئيسي
    """
    app.register_blueprint(btec_mudaqqiq, url_prefix='/mudaqqiq')
    
    # إضافة روابط القائمة الرئيسية إذا كانت موجودة في التطبيق
    if hasattr(app, 'add_main_menu_item'):
        app.add_main_menu_item('منصة مُدقِّق', 'btec_mudaqqiq.index', 'fas fa-magnifying-glass-chart', order=50)
        app.add_main_menu_item('قلعة Grok الأسطورية', 'btec_mudaqqiq.castle_grok', 'fas fa-castle', order=51)