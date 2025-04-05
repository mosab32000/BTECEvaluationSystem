"""
مسارات المصادقة في نظام تقييم BTEC
"""
import logging
from datetime import datetime
from flask import Blueprint, request, jsonify, render_template, redirect, url_for, flash, session
from flask_login import login_user, logout_user, login_required, current_user
from flask_jwt_extended import create_access_token, create_refresh_token
from werkzeug.security import generate_password_hash, check_password_hash

from app import db
from app.models.user import User

# إنشاء مخطط مسارات المصادقة
bp = Blueprint('auth', __name__, url_prefix='/auth')

# إعداد التسجيل
logger = logging.getLogger(__name__)

@bp.route('/register', methods=['GET', 'POST'])
def register():
    """تسجيل مستخدم جديد"""
    # إذا كان المستخدم مسجل الدخول بالفعل
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    # إذا كان الطلب POST (إرسال النموذج)
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        name = request.form.get('name')
        
        # التحقق من البيانات
        if not email or not password or not name:
            flash('جميع الحقول مطلوبة.', 'danger')
            return render_template('auth/register.html')
        
        # التحقق مما إذا كان المستخدم موجوداً بالفعل
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('البريد الإلكتروني مستخدم بالفعل.', 'danger')
            return render_template('auth/register.html')
        
        # إنشاء مستخدم جديد
        user = User(
            email=email,
            name=name,
            password_hash=generate_password_hash(password),
            role='user',
            created_at=datetime.utcnow()
        )
        
        # حفظ المستخدم في قاعدة البيانات
        try:
            db.session.add(user)
            db.session.commit()
            
            # تسجيل الدخول للمستخدم الجديد
            login_user(user)
            
            flash('تم التسجيل بنجاح وتسجيل الدخول!', 'success')
            return redirect(url_for('index'))
        except Exception as e:
            db.session.rollback()
            logger.error(f"خطأ في تسجيل المستخدم: {str(e)}")
            flash('حدث خطأ أثناء التسجيل. يرجى المحاولة مرة أخرى.', 'danger')
    
    # عرض صفحة التسجيل
    return render_template('auth/register.html')

@bp.route('/login', methods=['GET', 'POST'])
def login():
    """تسجيل الدخول"""
    # إذا كان المستخدم مسجل الدخول بالفعل
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    # إذا كان الطلب POST (إرسال النموذج)
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        remember = 'remember' in request.form
        
        # التحقق من البيانات
        if not email or not password:
            flash('البريد الإلكتروني وكلمة المرور مطلوبان.', 'danger')
            return render_template('auth/login.html')
        
        # البحث عن المستخدم
        user = User.query.filter_by(email=email).first()
        
        # التحقق من صحة بيانات المستخدم
        if not user or not user.check_password(password):
            flash('البريد الإلكتروني أو كلمة المرور غير صحيحة.', 'danger')
            return render_template('auth/login.html')
        
        # التحقق من حالة المستخدم
        if not user.is_active:
            flash('هذا الحساب غير نشط. يرجى التواصل مع المسؤول.', 'danger')
            return render_template('auth/login.html')
        
        # تسجيل الدخول
        login_user(user, remember=remember)
        
        # تحديث وقت آخر تسجيل دخول
        user.last_login = datetime.utcnow()
        db.session.commit()
        
        flash('تم تسجيل الدخول بنجاح!', 'success')
        
        # إعادة التوجيه إلى الصفحة المطلوبة قبل تسجيل الدخول أو الصفحة الرئيسية
        next_page = request.args.get('next')
        if not next_page or not next_page.startswith('/'):
            next_page = url_for('index')
            
        return redirect(next_page)
    
    # عرض صفحة تسجيل الدخول
    return render_template('auth/login.html')

@bp.route('/logout')
@login_required
def logout():
    """تسجيل الخروج"""
    logout_user()
    flash('تم تسجيل الخروج بنجاح.', 'info')
    return redirect(url_for('index'))

@bp.route('/reset-password', methods=['GET', 'POST'])
def reset_password_request():
    """طلب إعادة تعيين كلمة المرور"""
    # إذا كان المستخدم مسجل الدخول بالفعل
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    # إذا كان الطلب POST (إرسال النموذج)
    if request.method == 'POST':
        email = request.form.get('email')
        
        # التحقق من البيانات
        if not email:
            flash('البريد الإلكتروني مطلوب.', 'danger')
            return render_template('auth/reset_password_request.html')
        
        # البحث عن المستخدم
        user = User.query.filter_by(email=email).first()
        
        # حتى لو لم يتم العثور على المستخدم، نعرض رسالة نجاح للأمان
        flash('تم إرسال تعليمات إعادة تعيين كلمة المرور إلى بريدك الإلكتروني.', 'info')
        
        # هنا يمكن إضافة رمز لإرسال رسالة بريد إلكتروني مع رابط إعادة تعيين كلمة المرور
        # (يتطلب إعداد خدمة بريد إلكتروني)
        
        return redirect(url_for('auth.login'))
    
    # عرض صفحة طلب إعادة تعيين كلمة المرور
    return render_template('auth/reset_password_request.html')

@bp.route('/api/login', methods=['POST'])
def api_login():
    """واجهة برمجة التطبيقات (API) لتسجيل الدخول"""
    data = request.get_json()
    
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({'success': False, 'message': 'البريد الإلكتروني وكلمة المرور مطلوبان.'}), 400
    
    # البحث عن المستخدم
    user = User.query.filter_by(email=data.get('email')).first()
    
    # التحقق من صحة بيانات المستخدم
    if not user or not user.check_password(data.get('password')):
        return jsonify({'success': False, 'message': 'البريد الإلكتروني أو كلمة المرور غير صحيحة.'}), 401
    
    # التحقق من حالة المستخدم
    if not user.is_active:
        return jsonify({'success': False, 'message': 'هذا الحساب غير نشط.'}), 403
    
    # تحديث وقت آخر تسجيل دخول
    user.last_login = datetime.utcnow()
    db.session.commit()
    
    # إنشاء رموز JWT
    access_token = create_access_token(identity=user.uuid)
    refresh_token = create_refresh_token(identity=user.uuid)
    
    return jsonify({
        'success': True,
        'access_token': access_token,
        'refresh_token': refresh_token,
        'user': user.to_dict()
    }), 200

@bp.route('/api/register', methods=['POST'])
def api_register():
    """واجهة برمجة التطبيقات (API) لتسجيل مستخدم جديد"""
    data = request.get_json()
    
    if not data or not data.get('email') or not data.get('password') or not data.get('name'):
        return jsonify({'success': False, 'message': 'جميع الحقول مطلوبة.'}), 400
    
    # التحقق مما إذا كان المستخدم موجوداً بالفعل
    existing_user = User.query.filter_by(email=data.get('email')).first()
    if existing_user:
        return jsonify({'success': False, 'message': 'البريد الإلكتروني مستخدم بالفعل.'}), 409
    
    # إنشاء مستخدم جديد
    user = User(
        email=data.get('email'),
        name=data.get('name'),
        password_hash=generate_password_hash(data.get('password')),
        role='user',
        created_at=datetime.utcnow()
    )
    
    # حفظ المستخدم في قاعدة البيانات
    try:
        db.session.add(user)
        db.session.commit()
        
        # إنشاء رموز JWT
        access_token = create_access_token(identity=user.uuid)
        refresh_token = create_refresh_token(identity=user.uuid)
        
        return jsonify({
            'success': True,
            'message': 'تم التسجيل بنجاح.',
            'access_token': access_token,
            'refresh_token': refresh_token,
            'user': user.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        logger.error(f"خطأ في تسجيل المستخدم: {str(e)}")
        return jsonify({'success': False, 'message': 'حدث خطأ أثناء التسجيل.'}), 500