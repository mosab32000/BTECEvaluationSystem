"""
وحدة مسارات الصفحة الرئيسية لنظام تقييم BTEC
"""

from flask import Blueprint, render_template, redirect, url_for, current_app
from flask_login import current_user, login_required

from app.extensions import cache

main_blueprint = Blueprint('main', __name__)


@main_blueprint.route('/')
@cache.cached(timeout=60)
def index():
    """الصفحة الرئيسية"""
    return render_template('index.html')


@main_blueprint.route('/about')
def about():
    """صفحة حول النظام"""
    return render_template('about.html')


@main_blueprint.route('/features')
def features():
    """صفحة ميزات النظام"""
    return render_template('features.html')


@main_blueprint.route('/contact')
def contact():
    """صفحة الاتصال"""
    return render_template('contact.html')


@main_blueprint.route('/dashboard')
@login_required
def dashboard_redirect():
    """إعادة توجيه إلى لوحة التحكم الخاصة بالمستخدم"""
    if current_user.role == 'admin':
        return redirect(url_for('admin.dashboard'))
    elif current_user.role == 'teacher':
        return redirect(url_for('dashboard.teacher'))
    elif current_user.role == 'student':
        return redirect(url_for('dashboard.student'))
    else:
        return redirect(url_for('dashboard.user'))


@main_blueprint.route('/health')
def health():
    """
    نقطة نهاية للتحقق من صحة النظام
    """
    return {
        'status': 'ok',
        'version': current_app.config.get('VERSION', '1.0.0'),
        'env': current_app.config.get('FLASK_ENV', 'production')
    }