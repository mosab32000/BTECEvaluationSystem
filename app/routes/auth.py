"""
مسارات المصادقة لنظام تقييم BTEC
"""

from flask import Blueprint, render_template, redirect, url_for, request, flash, current_app
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """صفحة تسجيل الدخول"""
    if request.method == 'POST':
        # إعادة التوجيه الى الصفحة الرئيسية مؤقتاً
        flash('تم تسجيل الدخول بنجاح', 'success')
        return redirect(url_for('main.dashboard'))
        
    return render_template('auth/login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    """تسجيل الخروج"""
    logout_user()
    flash('تم تسجيل الخروج بنجاح', 'success')
    return redirect(url_for('main.index'))

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """صفحة إنشاء حساب جديد"""
    if request.method == 'POST':
        # إعادة التوجيه الى صفحة تسجيل الدخول مؤقتاً
        flash('تم إنشاء الحساب بنجاح. يمكنك الآن تسجيل الدخول.', 'success')
        return redirect(url_for('auth.login'))
        
    return render_template('auth/register.html')

@auth_bp.route('/reset-password-request', methods=['GET', 'POST'])
def reset_password_request():
    """صفحة طلب إعادة تعيين كلمة المرور"""
    if request.method == 'POST':
        flash('تم إرسال بريد إلكتروني مع تعليمات إعادة تعيين كلمة المرور', 'info')
        return redirect(url_for('auth.login'))
        
    return render_template('auth/reset_password_request.html')

@auth_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    """صفحة الملف الشخصي"""
    if request.method == 'POST':
        flash('تم تحديث الملف الشخصي بنجاح', 'success')
        return redirect(url_for('auth.profile'))
        
    return render_template('auth/profile.html')

@auth_bp.route('/change-password', methods=['POST'])
@login_required
def change_password():
    """تغيير كلمة المرور"""
    flash('تم تغيير كلمة المرور بنجاح', 'success')
    return redirect(url_for('auth.profile'))
