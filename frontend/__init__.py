"""
وحدة واجهة المستخدم الأمامية لنظام تقييم BTEC
"""

from flask import Blueprint, render_template, redirect, url_for, session, request, flash, jsonify
import os
import json

# إنشاء blueprint للواجهة الأمامية
frontend = Blueprint('frontend', __name__,
                     template_folder='templates',
                     static_folder='static',
                     static_url_path='/frontend/static')

@frontend.route('/')
def index():
    """الصفحة الرئيسية"""
    return render_template('index.html')

@frontend.route('/login')
def login():
    """صفحة تسجيل الدخول"""
    # إذا كان المستخدم مسجل الدخول بالفعل، إعادة توجيهه إلى لوحة التحكم
    if session.get('user_id'):
        return redirect(url_for('frontend.dashboard'))
    return render_template('login.html')

@frontend.route('/register')
def register():
    """صفحة التسجيل"""
    # إذا كان المستخدم مسجل الدخول بالفعل، إعادة توجيهه إلى لوحة التحكم
    if session.get('user_id'):
        return redirect(url_for('frontend.dashboard'))
    return render_template('register.html')

@frontend.route('/dashboard')
def dashboard():
    """صفحة لوحة التحكم"""
    # التحقق من تسجيل الدخول
    if not session.get('user_id'):
        flash('يرجى تسجيل الدخول للوصول إلى لوحة التحكم', 'error')
        return redirect(url_for('frontend.login'))
    return render_template('dashboard.html')

@frontend.route('/evaluate')
def evaluate():
    """صفحة تقييم مهمة جديدة"""
    # التحقق من تسجيل الدخول
    if not session.get('user_id'):
        flash('يرجى تسجيل الدخول للوصول إلى صفحة التقييم', 'error')
        return redirect(url_for('frontend.login'))
    return render_template('evaluate.html')

@frontend.route('/evaluations')
def evaluations():
    """صفحة عرض جميع التقييمات"""
    # التحقق من تسجيل الدخول
    if not session.get('user_id'):
        flash('يرجى تسجيل الدخول للوصول إلى التقييمات', 'error')
        return redirect(url_for('frontend.login'))
    return render_template('evaluations.html')

@frontend.route('/evaluation/<int:evaluation_id>')
def evaluation_detail(evaluation_id):
    """صفحة عرض تفاصيل تقييم محدد"""
    # التحقق من تسجيل الدخول
    if not session.get('user_id'):
        flash('يرجى تسجيل الدخول للوصول إلى تفاصيل التقييم', 'error')
        return redirect(url_for('frontend.login'))
    return render_template('evaluation_detail.html')

@frontend.route('/verify')
def verify():
    """صفحة التحقق من صحة تقييم"""
    return render_template('verify.html')

@frontend.route('/admin')
def admin_dashboard():
    """لوحة التحكم الإدارية"""
    # التحقق من تسجيل الدخول ومن أن المستخدم هو مدير
    if not session.get('user_id'):
        flash('يرجى تسجيل الدخول للوصول إلى لوحة التحكم الإدارية', 'error')
        return redirect(url_for('frontend.login'))
    
    # في الإصدار النهائي، يجب التحقق من صلاحيات المستخدم
    # مثال: if not current_user.is_admin:
    #           flash('ليس لديك صلاحية للوصول إلى لوحة التحكم الإدارية', 'error')
    #           return redirect(url_for('frontend.dashboard'))
    
    return render_template('admin_dashboard.html')

@frontend.route('/logout')
def logout():
    """تسجيل الخروج"""
    # حذف معرف المستخدم من الجلسة
    session.pop('user_id', None)
    flash('تم تسجيل الخروج بنجاح', 'success')
    return redirect(url_for('frontend.index'))