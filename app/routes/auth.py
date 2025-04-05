"""
مسارات المصادقة في نظام تقييم BTEC
"""

import logging
from flask import render_template, redirect, url_for, request, flash, session, jsonify
from werkzeug.security import generate_password_hash, check_password_hash

from app.routes import auth_bp
from app.models.user import User

logger = logging.getLogger(__name__)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """صفحة التسجيل"""
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        name = request.form.get('name')
        
        # التحقق من صحة البيانات
        if not email or not password or not confirm_password or not name:
            flash('جميع الحقول مطلوبة', 'error')
            return render_template('auth/register.html')
        
        if password != confirm_password:
            flash('كلمات المرور غير متطابقة', 'error')
            return render_template('auth/register.html')
        
        # التحقق مما إذا كان البريد الإلكتروني مستخدمًا بالفعل
        existing_user = User.get_by_email(email)
        if existing_user:
            flash('البريد الإلكتروني مستخدم بالفعل', 'error')
            return render_template('auth/register.html')
        
        # إنشاء مستخدم جديد
        user = User(email=email, name=name, role='student')
        user.set_password(password)
        if user.save():
            flash('تم التسجيل بنجاح. يمكنك الآن تسجيل الدخول.', 'success')
            return redirect(url_for('auth.login'))
        else:
            flash('حدث خطأ أثناء التسجيل. يرجى المحاولة مرة أخرى.', 'error')
    
    return render_template('auth/register.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """صفحة تسجيل الدخول"""
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        # التحقق من صحة البيانات
        if not email or not password:
            flash('البريد الإلكتروني وكلمة المرور مطلوبين', 'error')
            return render_template('auth/login.html')
        
        # التحقق من صحة بيانات المستخدم
        user = User.get_by_email(email)
        if not user or not user.check_password(password):
            flash('البريد الإلكتروني أو كلمة المرور غير صحيحة', 'error')
            return render_template('auth/login.html')
        
        # التحقق من حالة المستخدم
        if not user.is_active:
            flash('حسابك غير نشط. يرجى الاتصال بالمسؤول.', 'error')
            return render_template('auth/login.html')
        
        # تسجيل الدخول
        session['user_id'] = user.id
        session['user_role'] = user.role
        session['user_name'] = user.name
        
        # توجيه المستخدم حسب الدور
        if user.role == 'admin':
            return redirect(url_for('admin.index'))
        else:
            return redirect(url_for('evaluation.index'))
    
    return render_template('auth/login.html')

@auth_bp.route('/logout')
def logout():
    """تسجيل الخروج"""
    session.clear()
    flash('تم تسجيل الخروج بنجاح', 'success')
    return redirect(url_for('main.index'))

@auth_bp.route('/profile', methods=['GET', 'POST'])
def profile():
    """صفحة الملف الشخصي"""
    # التحقق من تسجيل الدخول
    if 'user_id' not in session:
        flash('يجب تسجيل الدخول للوصول إلى هذه الصفحة', 'error')
        return redirect(url_for('auth.login'))
    
    user = User.get_by_id(session['user_id'])
    if not user:
        session.clear()
        flash('حدث خطأ في جلستك. يرجى تسجيل الدخول مرة أخرى.', 'error')
        return redirect(url_for('auth.login'))
    
    if request.method == 'POST':
        name = request.form.get('name')
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        
        # تحديث الاسم
        if name and name != user.name:
            user.name = name
            session['user_name'] = name
        
        # تحديث كلمة المرور إذا تم تقديمها
        if current_password and new_password and confirm_password:
            if not user.check_password(current_password):
                flash('كلمة المرور الحالية غير صحيحة', 'error')
                return render_template('auth/profile.html', user=user)
            
            if new_password != confirm_password:
                flash('كلمات المرور الجديدة غير متطابقة', 'error')
                return render_template('auth/profile.html', user=user)
            
            user.set_password(new_password)
        
        # حفظ التغييرات
        if user.save():
            flash('تم تحديث الملف الشخصي بنجاح', 'success')
        else:
            flash('حدث خطأ أثناء تحديث الملف الشخصي', 'error')
    
    return render_template('auth/profile.html', user=user)

@auth_bp.route('/api/login', methods=['POST'])
def api_login():
    """واجهة API لتسجيل الدخول"""
    data = request.get_json()
    if not data:
        return jsonify({'error': 'البيانات المطلوبة غير موجودة'}), 400
    
    email = data.get('email')
    password = data.get('password')
    
    if not email or not password:
        return jsonify({'error': 'البريد الإلكتروني وكلمة المرور مطلوبين'}), 400
    
    user = User.get_by_email(email)
    if not user or not user.check_password(password):
        return jsonify({'error': 'البريد الإلكتروني أو كلمة المرور غير صحيحة'}), 401
    
    if not user.is_active:
        return jsonify({'error': 'حسابك غير نشط'}), 403
    
    # إنشاء رمز جلسة أو JWT هنا إذا لزم الأمر
    
    return jsonify({
        'message': 'تم تسجيل الدخول بنجاح',
        'user': user.to_dict()
    })