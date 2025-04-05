"""
مسارات المصادقة في نظام تقييم BTEC
"""

import os
import logging
from datetime import datetime, timedelta

from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, current_app
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required, current_user
from flask_jwt_extended import (
    create_access_token, create_refresh_token, 
    jwt_required, get_jwt_identity, get_jwt
)

from app.extensions import db, jwt, limiter

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/login', methods=['GET', 'POST'])
@limiter.limit("10 per minute")
def login():
    """صفحة تسجيل الدخول"""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        remember = request.form.get('remember') == 'on'
        
        from app.models.user import User
        
        user = User.query.filter_by(email=email).first()
        
        if user and check_password_hash(user.password_hash, password):
            if not user.is_active:
                flash('تم تعطيل هذا الحساب. يرجى الاتصال بالإدارة.', 'danger')
                current_app.logger.warning(f'محاولة تسجيل دخول لحساب معطل: {email}')
                return render_template('auth/login.html', title='تسجيل الدخول')
            
            login_user(user, remember=remember)
            next_page = request.args.get('next')
            
            if not next_page or not next_page.startswith('/'):
                next_page = url_for('main.dashboard')
            
            flash('تم تسجيل الدخول بنجاح!', 'success')
            current_app.logger.info(f'تسجيل دخول ناجح: {user.email} (ID: {user.id})')
            return redirect(next_page)
        else:
            flash('فشل تسجيل الدخول. يرجى التحقق من البريد الإلكتروني وكلمة المرور.', 'danger')
            current_app.logger.warning(f'محاولة تسجيل دخول فاشلة: {email}')
    
    return render_template('auth/login.html', title='تسجيل الدخول')

@auth_bp.route('/logout')
@login_required
def logout():
    """تسجيل الخروج"""
    current_app.logger.info(f'تسجيل خروج: {current_user.email} (ID: {current_user.id})')
    logout_user()
    flash('تم تسجيل الخروج بنجاح.', 'info')
    return redirect(url_for('main.index'))

@auth_bp.route('/register', methods=['GET', 'POST'])
@limiter.limit("5 per hour")
def register():
    """صفحة التسجيل"""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        name = request.form.get('name')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        from app.models.user import User
        
        # التحقق من عدم تطابق كلمات المرور
        if password != confirm_password:
            flash('كلمات المرور غير متطابقة.', 'danger')
            return render_template('auth/register.html', title='إنشاء حساب')
        
        # التحقق من وجود المستخدم بالفعل
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('هذا البريد الإلكتروني مسجل بالفعل.', 'danger')
            return render_template('auth/register.html', title='إنشاء حساب')
        
        # إنشاء مستخدم جديد
        new_user = User(
            email=email,
            name=name,
            role='student'  # افتراضيًا، يتم إنشاء المستخدمين كطلاب
        )
        new_user.set_password(password)
        
        db.session.add(new_user)
        db.session.commit()
        
        current_app.logger.info(f'تم إنشاء مستخدم جديد: {email} (ID: {new_user.id})')
        flash('تم إنشاء الحساب بنجاح! يمكنك الآن تسجيل الدخول.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/register.html', title='إنشاء حساب')

@auth_bp.route('/reset-password', methods=['GET', 'POST'])
@limiter.limit("3 per hour")
def reset_password_request():
    """طلب إعادة تعيين كلمة المرور"""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        
        from app.models.user import User
        
        user = User.query.filter_by(email=email).first()
        
        if user:
            # هنا سيتم تنفيذ منطق إرسال رابط إعادة تعيين كلمة المرور
            # سنقوم بتنفيذه لاحقًا
            flash('تم إرسال تعليمات إعادة تعيين كلمة المرور إلى بريدك الإلكتروني.', 'info')
            current_app.logger.info(f'طلب إعادة تعيين كلمة المرور: {email}')
        else:
            flash('لم يتم العثور على حساب بهذا البريد الإلكتروني.', 'danger')
            current_app.logger.warning(f'طلب إعادة تعيين كلمة مرور لحساب غير موجود: {email}')
        
        return redirect(url_for('auth.login'))
    
    return render_template('auth/reset_password_request.html', title='نسيت كلمة المرور')

@auth_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    """صفحة الملف الشخصي"""
    if request.method == 'POST':
        name = request.form.get('name')
        
        current_user.name = name
        db.session.commit()
        
        flash('تم تحديث الملف الشخصي بنجاح.', 'success')
        current_app.logger.info(f'تم تحديث الملف الشخصي: {current_user.email} (ID: {current_user.id})')
        return redirect(url_for('auth.profile'))
    
    return render_template('auth/profile.html', title='الملف الشخصي')

@auth_bp.route('/change-password', methods=['POST'])
@login_required
@limiter.limit("5 per hour")
def change_password():
    """تغيير كلمة المرور"""
    current_password = request.form.get('current_password')
    new_password = request.form.get('new_password')
    confirm_password = request.form.get('confirm_password')
    
    # التحقق من عدم تطابق كلمات المرور الجديدة
    if new_password != confirm_password:
        flash('كلمات المرور الجديدة غير متطابقة.', 'danger')
        return redirect(url_for('auth.profile'))
    
    # التحقق من صحة كلمة المرور الحالية
    if not check_password_hash(current_user.password_hash, current_password):
        flash('كلمة المرور الحالية غير صحيحة.', 'danger')
        return redirect(url_for('auth.profile'))
    
    # تحديث كلمة المرور
    current_user.set_password(new_password)
    db.session.commit()
    
    flash('تم تغيير كلمة المرور بنجاح.', 'success')
    current_app.logger.info(f'تم تغيير كلمة المرور: {current_user.email} (ID: {current_user.id})')
    return redirect(url_for('auth.profile'))

#
# API للمصادقة (JWT)
#

@auth_bp.route('/api/login', methods=['POST'])
@limiter.limit("10 per minute")
def api_login():
    """API لتسجيل الدخول والحصول على رموز JWT"""
    if not request.is_json:
        return jsonify({"error": "Missing JSON in request"}), 400
    
    email = request.json.get('email', None)
    password = request.json.get('password', None)
    
    if not email or not password:
        return jsonify({"error": "Missing email or password"}), 400
    
    from app.models.user import User
    
    user = User.query.filter_by(email=email).first()
    
    if not user or not check_password_hash(user.password_hash, password):
        return jsonify({"error": "Invalid credentials"}), 401
    
    if not user.is_active:
        return jsonify({"error": "Account is disabled"}), 403
    
    # إنشاء رموز JWT
    access_token = create_access_token(identity=user.id)
    refresh_token = create_refresh_token(identity=user.id)
    
    current_app.logger.info(f'تسجيل دخول API ناجح: {user.email} (ID: {user.id})')
    
    return jsonify({
        "access_token": access_token,
        "refresh_token": refresh_token,
        "user": {
            "id": user.id,
            "email": user.email,
            "name": user.name,
            "role": user.role
        }
    }), 200

@auth_bp.route('/api/refresh', methods=['POST'])
@jwt_required(refresh=True)
def api_refresh():
    """API لتحديث رمز الوصول باستخدام رمز التحديث"""
    user_id = get_jwt_identity()
    
    from app.models.user import User
    
    user = User.query.get(user_id)
    
    if not user or not user.is_active:
        return jsonify({"error": "Account not found or disabled"}), 403
    
    access_token = create_access_token(identity=user_id)
    
    current_app.logger.info(f'تم تحديث رمز API: {user.email} (ID: {user.id})')
    
    return jsonify({
        "access_token": access_token
    }), 200

@auth_bp.route('/api/me', methods=['GET'])
@jwt_required()
def api_me():
    """API للحصول على معلومات المستخدم الحالي"""
    user_id = get_jwt_identity()
    
    from app.models.user import User
    
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    if not user.is_active:
        return jsonify({"error": "Account is disabled"}), 403
    
    return jsonify({
        "user": {
            "id": user.id,
            "email": user.email,
            "name": user.name,
            "role": user.role
        }
    }), 200

@auth_bp.route('/api/logout', methods=['POST'])
@jwt_required()
def api_logout():
    """API لتسجيل الخروج (إبطال الرمز)"""
    # في الإصدارات الحديثة من flask-jwt-extended يمكن استخدام JWT blacklisting
    # سنقوم بتنفيذه لاحقًا
    
    return jsonify({"message": "Successfully logged out"}), 200

# معالجات أحداث JWT
@jwt.token_in_blocklist_loader
def check_if_token_is_revoked(jwt_header, jwt_payload):
    """التحقق مما إذا كان الرمز قد تم إبطاله"""
    # هنا سيتم تنفيذ منطق التحقق من الرموز المبطلة
    # سنقوم بتنفيذه لاحقًا باستخدام قاعدة بيانات Redis أو جدول في قاعدة البيانات
    
    return False  # افتراضيًا، نعتبر جميع الرموز صالحة

@jwt.expired_token_loader
def expired_token_callback(jwt_header, jwt_payload):
    """معالجة الرموز منتهية الصلاحية"""
    return jsonify({
        'error': 'token_expired',
        'message': 'The token has expired'
    }), 401

@jwt.invalid_token_loader
def invalid_token_callback(error):
    """معالجة الرموز غير الصالحة"""
    return jsonify({
        'error': 'invalid_token',
        'message': 'Signature verification failed'
    }), 401

@jwt.unauthorized_loader
def missing_token_callback(error):
    """معالجة غياب الرمز"""
    return jsonify({
        'error': 'authorization_required',
        'message': 'Authorization is required'
    }), 401

@jwt.revoked_token_loader
def revoked_token_callback(jwt_header, jwt_payload):
    """معالجة الرموز المبطلة"""
    return jsonify({
        'error': 'token_revoked',
        'message': 'The token has been revoked'
    }), 401