"""
مسارات المصادقة في نظام تقييم BTEC
"""
import logging
import json
from datetime import datetime, timedelta
import os

from flask import Blueprint, request, jsonify, render_template, redirect
from flask import url_for, session, flash, current_app
from flask_login import login_user, logout_user, login_required, current_user
from flask_jwt_extended import create_access_token, create_refresh_token
from werkzeug.security import check_password_hash, generate_password_hash

from app.models.user import User

# تهيئة السجل
logger = logging.getLogger(__name__)

# إنشاء blueprint للمصادقة
bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/register', methods=['GET', 'POST'])
def register():
    """صفحة التسجيل"""
    if request.method == 'POST':
        # الحصول على بيانات النموذج
        email = request.form.get('email')
        password = request.form.get('password')
        name = request.form.get('name')
        
        # التحقق من صحة البيانات
        error = None
        if not email:
            error = 'البريد الإلكتروني مطلوب'
        elif not password:
            error = 'كلمة المرور مطلوبة'
        
        # التحقق من وجود المستخدم
        user = User.get_by_email(email)
        if user:
            error = 'البريد الإلكتروني مستخدم بالفعل'
        
        if error is None:
            # إنشاء مستخدم جديد
            new_user = User()
            new_user.email = email
            new_user.set_password(password)
            new_user.name = name
            new_user.role = 'student'  # الدور الافتراضي
            
            # حفظ المستخدم
            if new_user.save():
                logger.info(f"تم تسجيل مستخدم جديد: {email}")
                flash('تم إنشاء الحساب بنجاح! يمكنك الآن تسجيل الدخول.', 'success')
                return redirect(url_for('auth.login'))
            else:
                error = 'حدث خطأ أثناء إنشاء الحساب'
        
        flash(error, 'error')
    
    return render_template('auth/register.html')

@bp.route('/login', methods=['GET', 'POST'])
def login():
    """صفحة تسجيل الدخول"""
    if request.method == 'POST':
        # الحصول على بيانات النموذج
        email = request.form.get('email')
        password = request.form.get('password')
        remember = request.form.get('remember', 'false') == 'true'
        
        # التحقق من صحة البيانات
        error = None
        if not email:
            error = 'البريد الإلكتروني مطلوب'
        elif not password:
            error = 'كلمة المرور مطلوبة'
        
        # التحقق من المستخدم وكلمة المرور
        user = User.get_by_email(email)
        if user is None:
            error = 'بريد إلكتروني غير صحيح'
        elif not user.check_password(password):
            error = 'كلمة مرور غير صحيحة'
        elif not user.is_active:
            error = 'هذا الحساب معطل'
        
        if error is None:
            # تسجيل الدخول
            login_user(user, remember=remember)
            logger.info(f"تم تسجيل دخول المستخدم: {email}")
            
            next_page = request.args.get('next')
            if not next_page or not next_page.startswith('/'):
                next_page = url_for('index')
            
            flash('تم تسجيل الدخول بنجاح!', 'success')
            return redirect(next_page)
        
        flash(error, 'error')
    
    return render_template('auth/login.html')

@bp.route('/logout')
@login_required
def logout():
    """تسجيل الخروج"""
    logout_user()
    flash('تم تسجيل الخروج بنجاح!', 'success')
    return redirect(url_for('index'))

@bp.route('/profile')
@login_required
def profile():
    """صفحة الملف الشخصي"""
    return render_template('auth/profile.html')

@bp.route('/api/login', methods=['POST'])
def api_login():
    """واجهة API لتسجيل الدخول"""
    data = request.get_json() or {}
    
    if not data.get('email') or not data.get('password'):
        return jsonify({'error': 'البريد الإلكتروني وكلمة المرور مطلوبين'}), 400
    
    user = User.get_by_email(data['email'])
    if user is None or not user.check_password(data['password']):
        return jsonify({'error': 'بيانات تسجيل الدخول غير صحيحة'}), 401
    
    if not user.is_active:
        return jsonify({'error': 'هذا الحساب معطل'}), 403
    
    # إنشاء توكن
    access_token = create_access_token(identity=user.id)
    refresh_token = create_refresh_token(identity=user.id)
    
    logger.info(f"تم تسجيل دخول API للمستخدم: {user.email}")
    
    # إعادة البيانات
    return jsonify({
        'access_token': access_token,
        'refresh_token': refresh_token,
        'user': user.to_dict()
    }), 200

@bp.route('/api/register', methods=['POST'])
def api_register():
    """واجهة API للتسجيل"""
    data = request.get_json() or {}
    
    # التحقق من البيانات المطلوبة
    if not data.get('email') or not data.get('password'):
        return jsonify({'error': 'البريد الإلكتروني وكلمة المرور مطلوبين'}), 400
    
    # التحقق من وجود المستخدم
    user = User.get_by_email(data['email'])
    if user:
        return jsonify({'error': 'البريد الإلكتروني مستخدم بالفعل'}), 400
    
    # إنشاء مستخدم جديد
    new_user = User()
    new_user.email = data['email']
    new_user.set_password(data['password'])
    new_user.name = data.get('name', '')
    new_user.role = 'student'  # الدور الافتراضي
    
    # حفظ المستخدم
    if not new_user.save():
        return jsonify({'error': 'حدث خطأ أثناء إنشاء الحساب'}), 500
    
    logger.info(f"تم تسجيل مستخدم جديد عبر API: {new_user.email}")
    
    # إنشاء توكن
    access_token = create_access_token(identity=new_user.id)
    refresh_token = create_refresh_token(identity=new_user.id)
    
    # إعادة البيانات
    return jsonify({
        'message': 'تم إنشاء الحساب بنجاح',
        'access_token': access_token,
        'refresh_token': refresh_token,
        'user': new_user.to_dict()
    }), 201

@bp.route('/reset-password', methods=['GET', 'POST'])
def reset_password_request():
    """طلب إعادة تعيين كلمة المرور"""
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        if not email:
            flash('البريد الإلكتروني مطلوب', 'error')
            return render_template('auth/reset_password_request.html')
        
        user = User.get_by_email(email)
        if user:
            # في حالة التنفيذ الفعلي، هنا يتم إرسال بريد إلكتروني
            # مع رابط لإعادة تعيين كلمة المرور
            # TODO: تنفيذ إرسال البريد الإلكتروني
            logger.info(f"تم طلب إعادة تعيين كلمة المرور للمستخدم: {email}")
        
        flash('تم إرسال تعليمات إعادة تعيين كلمة المرور إلى بريدك الإلكتروني.', 'info')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/reset_password_request.html')