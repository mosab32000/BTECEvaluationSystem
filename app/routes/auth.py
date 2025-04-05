"""
مسارات المصادقة في نظام تقييم BTEC
"""
import logging
import json
from datetime import datetime, timedelta
import os

from flask import Blueprint, request, jsonify, render_template, redirect, url_for, flash, current_app, session
from flask_login import login_user, logout_user, login_required, current_user
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash

from app.models.user import User

# تهيئة السجل
logger = logging.getLogger(__name__)

# إنشاء Blueprint
bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/login', methods=['GET', 'POST'])
def login():
    """
    صفحة تسجيل الدخول
    
    Returns:
        Response: استجابة HTTP
    """
    # إذا كان المستخدم مسجل الدخول بالفعل، يتم إعادة توجيهه
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        # الحصول على بيانات تسجيل الدخول
        if request.is_json:
            data = request.get_json()
        else:
            data = request.form
        
        email = data.get('email')
        password = data.get('password')
        remember = data.get('remember', False)
        
        # التحقق من البيانات المطلوبة
        if not email or not password:
            if request.is_json:
                return jsonify({"error": "يرجى تحديد البريد الإلكتروني وكلمة المرور"}), 400
            flash("يرجى تحديد البريد الإلكتروني وكلمة المرور", "error")
            return render_template('auth/login.html')
        
        # البحث عن المستخدم
        user = User.get_by_email(email)
        
        # التحقق من المستخدم وكلمة المرور
        if not user or not user.check_password(password):
            logger.warning(f"محاولة تسجيل دخول فاشلة للبريد الإلكتروني: {email}")
            
            if request.is_json:
                return jsonify({"error": "البريد الإلكتروني أو كلمة المرور غير صحيحة"}), 401
            
            flash("البريد الإلكتروني أو كلمة المرور غير صحيحة", "error")
            return render_template('auth/login.html')
        
        # التحقق من حالة المستخدم
        if not user.is_active:
            logger.warning(f"محاولة تسجيل دخول لحساب غير مفعل: {email}")
            
            if request.is_json:
                return jsonify({"error": "هذا الحساب غير مفعل"}), 403
            
            flash("هذا الحساب غير مفعل، يرجى الاتصال بالمسؤول", "error")
            return render_template('auth/login.html')
        
        # تسجيل الدخول
        login_user(user, remember=remember)
        logger.info(f"تم تسجيل دخول المستخدم: {email}")
        
        # إنشاء JWT token للAPI
        access_token = create_access_token(identity=user.id)
        refresh_token = create_refresh_token(identity=user.id)
        
        # حفظ التوكن في الجلسة للوصول إليه لاحقًا
        session['access_token'] = access_token
        
        # الرد بناءً على نوع الطلب
        if request.is_json:
            return jsonify({
                "message": "تم تسجيل الدخول بنجاح",
                "access_token": access_token,
                "refresh_token": refresh_token,
                "user": user.to_dict()
            }), 200
        
        # إعادة التوجيه إلى الصفحة التي كان يحاول الوصول إليها أو الصفحة الرئيسية
        next_page = request.args.get('next')
        if not next_page or not next_page.startswith('/'):
            next_page = url_for('index')
        
        flash("تم تسجيل الدخول بنجاح", "success")
        return redirect(next_page)
    
    # عرض صفحة تسجيل الدخول
    return render_template('auth/login.html')

@bp.route('/logout')
@login_required
def logout():
    """
    تسجيل الخروج
    
    Returns:
        Response: استجابة HTTP
    """
    if current_user.is_authenticated:
        logger.info(f"تم تسجيل خروج المستخدم: {current_user.email}")
    
    logout_user()
    
    # إزالة التوكن من الجلسة
    if 'access_token' in session:
        session.pop('access_token')
    
    if request.is_json:
        return jsonify({"message": "تم تسجيل الخروج بنجاح"}), 200
    
    flash("تم تسجيل الخروج بنجاح", "info")
    return redirect(url_for('auth.login'))

@bp.route('/register', methods=['GET', 'POST'])
def register():
    """
    صفحة التسجيل (إنشاء حساب جديد)
    
    Returns:
        Response: استجابة HTTP
    """
    # إذا كان المستخدم مسجل الدخول بالفعل، يتم إعادة توجيهه
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        # الحصول على بيانات التسجيل
        if request.is_json:
            data = request.get_json()
        else:
            data = request.form
        
        name = data.get('name')
        email = data.get('email')
        password = data.get('password')
        password_confirm = data.get('password_confirm')
        
        # التحقق من البيانات المطلوبة
        if not name or not email or not password or not password_confirm:
            if request.is_json:
                return jsonify({"error": "يرجى تعبئة جميع الحقول المطلوبة"}), 400
            flash("يرجى تعبئة جميع الحقول المطلوبة", "error")
            return render_template('auth/register.html')
        
        # التحقق من تطابق كلمات المرور
        if password != password_confirm:
            if request.is_json:
                return jsonify({"error": "كلمات المرور غير متطابقة"}), 400
            flash("كلمات المرور غير متطابقة", "error")
            return render_template('auth/register.html')
        
        # التحقق من عدم وجود المستخدم مسبقًا
        existing_user = User.get_by_email(email)
        if existing_user:
            if request.is_json:
                return jsonify({"error": "البريد الإلكتروني مستخدم بالفعل"}), 400
            flash("البريد الإلكتروني مستخدم بالفعل", "error")
            return render_template('auth/register.html')
        
        # إنشاء مستخدم جديد
        user = User(
            email=email,
            name=name,
            role='student',  # الدور الافتراضي هو طالب
            is_active=True   # نشط افتراضيًا
        )
        user.set_password(password)
        
        if user.save():
            logger.info(f"تم إنشاء حساب جديد: {email}")
            
            if request.is_json:
                return jsonify({"message": "تم إنشاء الحساب بنجاح"}), 201
            
            flash("تم إنشاء الحساب بنجاح، يمكنك الآن تسجيل الدخول", "success")
            return redirect(url_for('auth.login'))
        else:
            logger.error(f"فشل في إنشاء حساب جديد: {email}")
            
            if request.is_json:
                return jsonify({"error": "فشل في إنشاء الحساب"}), 500
            
            flash("فشل في إنشاء الحساب، يرجى المحاولة مرة أخرى", "error")
            return render_template('auth/register.html')
    
    # عرض صفحة التسجيل
    return render_template('auth/register.html')

@bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    """
    صفحة الملف الشخصي
    
    Returns:
        Response: استجابة HTTP
    """
    if request.method == 'POST':
        # تحديث بيانات الملف الشخصي
        if request.is_json:
            data = request.get_json()
        else:
            data = request.form
        
        name = data.get('name')
        current_password = data.get('current_password')
        new_password = data.get('new_password')
        
        # تحديث الاسم
        if name and name != current_user.name:
            current_user.name = name
        
        # تحديث كلمة المرور
        if current_password and new_password:
            if not current_user.check_password(current_password):
                if request.is_json:
                    return jsonify({"error": "كلمة المرور الحالية غير صحيحة"}), 400
                flash("كلمة المرور الحالية غير صحيحة", "error")
                return render_template('auth/profile.html')
            
            current_user.set_password(new_password)
        
        # حفظ التغييرات
        if current_user.save():
            logger.info(f"تم تحديث الملف الشخصي للمستخدم: {current_user.email}")
            
            if request.is_json:
                return jsonify({"message": "تم تحديث الملف الشخصي بنجاح", "user": current_user.to_dict()}), 200
            
            flash("تم تحديث الملف الشخصي بنجاح", "success")
        else:
            logger.error(f"فشل في تحديث الملف الشخصي للمستخدم: {current_user.email}")
            
            if request.is_json:
                return jsonify({"error": "فشل في تحديث الملف الشخصي"}), 500
            
            flash("فشل في تحديث الملف الشخصي، يرجى المحاولة مرة أخرى", "error")
    
    # عرض صفحة الملف الشخصي
    return render_template('auth/profile.html')

# مسارات API للمصادقة
@bp.route('/api/login', methods=['POST'])
def api_login():
    """
    تسجيل الدخول عبر API
    
    Returns:
        Response: استجابة HTTP
    """
    data = request.get_json()
    
    if not data:
        return jsonify({"error": "بيانات JSON غير صالحة"}), 400
    
    email = data.get('email')
    password = data.get('password')
    
    if not email or not password:
        return jsonify({"error": "يرجى تحديد البريد الإلكتروني وكلمة المرور"}), 400
    
    user = User.get_by_email(email)
    
    if not user or not user.check_password(password):
        return jsonify({"error": "البريد الإلكتروني أو كلمة المرور غير صحيحة"}), 401
    
    if not user.is_active:
        return jsonify({"error": "هذا الحساب غير مفعل"}), 403
    
    # إنشاء JWT tokens
    access_token = create_access_token(identity=user.id)
    refresh_token = create_refresh_token(identity=user.id)
    
    logger.info(f"تم إنشاء توكن للمستخدم عبر API: {email}")
    
    return jsonify({
        "message": "تم تسجيل الدخول بنجاح",
        "access_token": access_token,
        "refresh_token": refresh_token,
        "user": user.to_dict()
    }), 200

@bp.route('/api/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """
    تجديد توكن الوصول
    
    Returns:
        Response: استجابة HTTP
    """
    current_user_id = get_jwt_identity()
    user = User.get_by_id(current_user_id)
    
    if not user:
        return jsonify({"error": "المستخدم غير موجود"}), 404
    
    if not user.is_active:
        return jsonify({"error": "هذا الحساب غير مفعل"}), 403
    
    # إنشاء توكن وصول جديد
    access_token = create_access_token(identity=current_user_id)
    
    logger.info(f"تم تجديد توكن للمستخدم: {user.email}")
    
    return jsonify({
        "message": "تم تجديد التوكن بنجاح",
        "access_token": access_token
    }), 200

@bp.route('/api/user', methods=['GET'])
@jwt_required()
def get_user():
    """
    الحصول على معلومات المستخدم الحالي
    
    Returns:
        Response: استجابة HTTP
    """
    current_user_id = get_jwt_identity()
    user = User.get_by_id(current_user_id)
    
    if not user:
        return jsonify({"error": "المستخدم غير موجود"}), 404
    
    return jsonify({
        "user": user.to_dict()
    }), 200

@bp.route('/api/register', methods=['POST'])
def api_register():
    """
    التسجيل عبر API
    
    Returns:
        Response: استجابة HTTP
    """
    data = request.get_json()
    
    if not data:
        return jsonify({"error": "بيانات JSON غير صالحة"}), 400
    
    name = data.get('name')
    email = data.get('email')
    password = data.get('password')
    
    if not name or not email or not password:
        return jsonify({"error": "يرجى تعبئة جميع الحقول المطلوبة"}), 400
    
    existing_user = User.get_by_email(email)
    if existing_user:
        return jsonify({"error": "البريد الإلكتروني مستخدم بالفعل"}), 400
    
    user = User(
        email=email,
        name=name,
        role='student',
        is_active=True
    )
    user.set_password(password)
    
    if user.save():
        logger.info(f"تم إنشاء حساب جديد عبر API: {email}")
        
        # للتبسيط، قم بتسجيل الدخول تلقائيًا بعد التسجيل
        access_token = create_access_token(identity=user.id)
        refresh_token = create_refresh_token(identity=user.id)
        
        return jsonify({
            "message": "تم إنشاء الحساب بنجاح",
            "access_token": access_token,
            "refresh_token": refresh_token,
            "user": user.to_dict()
        }), 201
    else:
        logger.error(f"فشل في إنشاء حساب جديد عبر API: {email}")
        return jsonify({"error": "فشل في إنشاء الحساب"}), 500