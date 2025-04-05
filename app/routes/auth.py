"""
وحدة مسارات المصادقة لنظام تقييم BTEC
"""

from datetime import datetime

from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required, current_user

from app.extensions import db, limiter
from app.models.user import User

auth_blueprint = Blueprint('auth', __name__)


@auth_blueprint.route('/login', methods=['GET', 'POST'])
@limiter.limit("10/minute")
def login():
    """صفحة تسجيل الدخول"""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard_redirect'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        remember = 'remember' in request.form
        
        user = User.query.filter_by(email=email).first()
        
        if user and user.is_active and check_password_hash(user.password_hash, password):
            login_user(user, remember=remember)
            
            user.last_login = datetime.utcnow()
            db.session.commit()
            
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            return redirect(url_for('main.dashboard_redirect'))
        else:
            flash('فشل تسجيل الدخول. يرجى التحقق من بريدك الإلكتروني وكلمة المرور.', 'error')
    
    return render_template('auth/login.html')


@auth_blueprint.route('/logout')
@login_required
def logout():
    """تسجيل الخروج"""
    logout_user()
    session.clear()
    flash('تم تسجيل الخروج بنجاح.', 'success')
    return redirect(url_for('main.index'))


@auth_blueprint.route('/register', methods=['GET', 'POST'])
@limiter.limit("5/hour")
def register():
    """صفحة التسجيل"""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard_redirect'))
    
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        password_confirm = request.form.get('password_confirm')
        
        if password != password_confirm:
            flash('كلمات المرور غير متطابقة.', 'error')
            return render_template('auth/register.html')
        
        user_exists = User.query.filter_by(email=email).first() is not None
        
        if user_exists:
            flash('البريد الإلكتروني مسجل بالفعل.', 'error')
            return render_template('auth/register.html')
        
        new_user = User(
            name=name,
            email=email,
            password_hash=generate_password_hash(password),
            role='student'  # الدور الافتراضي للمستخدمين الجدد
        )
        
        db.session.add(new_user)
        db.session.commit()
        
        flash('تم إنشاء الحساب بنجاح. يمكنك الآن تسجيل الدخول.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/register.html')


@auth_blueprint.route('/forgot-password', methods=['GET', 'POST'])
@limiter.limit("5/hour")
def forgot_password():
    """صفحة نسيت كلمة المرور"""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard_redirect'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        user = User.query.filter_by(email=email).first()
        
        if user:
            # TODO: إرسال بريد إلكتروني لإعادة تعيين كلمة المرور
            flash('تم إرسال تعليمات إعادة تعيين كلمة المرور إلى بريدك الإلكتروني.', 'success')
        else:
            flash('لم يتم العثور على حساب بهذا البريد الإلكتروني.', 'error')
        
        return redirect(url_for('auth.login'))
    
    return render_template('auth/forgot_password.html')


@auth_blueprint.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    """صفحة إعادة تعيين كلمة المرور"""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard_redirect'))
    
    # TODO: التحقق من صلاحية الرمز وتنفيذ إعادة تعيين كلمة المرور
    
    return render_template('auth/reset_password.html')