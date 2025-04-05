"""
مسارات الصفحات الرئيسية في نظام تقييم BTEC
"""

import os
from datetime import datetime

from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app, send_from_directory
from flask_login import login_required, current_user

from app.extensions import db, cache

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """الصفحة الرئيسية"""
    return render_template('index.html', title='نظام تقييم BTEC')

@main_bp.route('/about')
def about():
    """صفحة حول النظام"""
    return render_template('about.html', title='حول النظام')

@main_bp.route('/dashboard')
@login_required
def dashboard():
    """لوحة التحكم"""
    # إحصائيات للوحة التحكم
    stats = {
        'user_count': 0,
        'evaluation_count': 0,
        'classroom_count': 0,
        'task_count': 0
    }
    
    # استيراد النماذج اللازمة محليًا لتجنب الاستيرادات الدائرية
    from app.models.user import User
    from app.models.evaluation import Evaluation
    from app.models.classroom import Classroom
    from app.models.task import Task
    
    # حساب الإحصائيات
    stats['user_count'] = User.query.count()
    stats['evaluation_count'] = Evaluation.query.count()
    stats['classroom_count'] = Classroom.query.count()
    stats['task_count'] = Task.query.count()
    
    # الحصول على قائمة التقييمات الأخيرة
    if current_user.is_admin or current_user.is_teacher:
        # المسؤولون والمعلمون يرون كل التقييمات
        recent_evaluations = Evaluation.query.order_by(Evaluation.created_at.desc()).limit(5).all()
    else:
        # الطلاب يرون تقييماتهم فقط
        recent_evaluations = Evaluation.query.filter_by(student_id=current_user.id).order_by(Evaluation.created_at.desc()).limit(5).all()
    
    return render_template('dashboard.html', 
                          title='لوحة التحكم', 
                          stats=stats,
                          recent_evaluations=recent_evaluations)

@main_bp.route('/profile')
@login_required
def profile():
    """الملف الشخصي للمستخدم"""
    return render_template('profile.html', title='الملف الشخصي')

@main_bp.route('/contact')
def contact():
    """صفحة الاتصال"""
    return render_template('contact.html', title='اتصل بنا')

@main_bp.route('/favicon.ico')
def favicon():
    """تقديم الأيقونة المفضلة"""
    return send_from_directory(os.path.join(current_app.root_path, 'static', 'img'),
                              'favicon.ico', mimetype='image/vnd.microsoft.icon')

@main_bp.route('/robots.txt')
def robots():
    """تقديم ملف robots.txt"""
    return send_from_directory(os.path.join(current_app.root_path, 'static'),
                              'robots.txt', mimetype='text/plain')

@main_bp.route('/sitemap.xml')
def sitemap():
    """تقديم ملف sitemap.xml"""
    return send_from_directory(os.path.join(current_app.root_path, 'static'),
                              'sitemap.xml', mimetype='application/xml')

@main_bp.route('/static/<path:filename>')
def static_files(filename):
    """تقديم الملفات الثابتة"""
    return send_from_directory(os.path.join(current_app.root_path, 'static'), filename)

@main_bp.app_errorhandler(404)
def page_not_found(e):
    """معالجة خطأ 404 - الصفحة غير موجودة"""
    return render_template('errors/404.html'), 404

@main_bp.app_errorhandler(500)
def server_error(e):
    """معالجة خطأ 500 - خطأ في الخادم"""
    current_app.logger.error(f'خطأ في الخادم: {str(e)}')
    return render_template('errors/500.html'), 500