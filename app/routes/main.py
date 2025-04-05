"""
المسارات الرئيسية لنظام تقييم BTEC
"""

from flask import Blueprint, render_template, current_app, redirect, url_for, request, jsonify, flash
from flask_login import login_required, current_user

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """الصفحة الرئيسية"""
    return render_template('index.html')

@main_bp.route('/about')
def about():
    """صفحة حول النظام"""
    return render_template('about.html')

@main_bp.route('/contact')
def contact():
    """صفحة اتصل بنا"""
    return render_template('contact.html')

@main_bp.route('/dashboard')
@login_required
def dashboard():
    """لوحة التحكم"""
    # بيانات إحصائية وهمية للعرض
    stats = {
        'user_count': 150,
        'evaluation_count': 450,
        'classroom_count': 12,
        'task_count': 78
    }
    
    # قائمة التقييمات الأخيرة
    recent_evaluations = []
    
    return render_template('dashboard.html', stats=stats, recent_evaluations=recent_evaluations)
