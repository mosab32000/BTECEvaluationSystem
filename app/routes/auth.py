"""
مسارات المصادقة والتحقق
"""

from flask import Blueprint, request, jsonify, session
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import (
    create_access_token, create_refresh_token, 
    jwt_required, get_jwt_identity
)
from app.models import User
from app import db
import datetime

auth = Blueprint('auth', __name__)

@auth.route('/register', methods=['POST'])
def register():
    """
    تسجيل مستخدم جديد
    """
    # الحصول على بيانات التسجيل من الطلب
    data = request.get_json()
    
    if not data:
        return jsonify(error="بيانات غير صالحة", message="لم يتم توفير البيانات المطلوبة"), 400
    
    # تحقق من وجود البيانات المطلوبة
    if not all(k in data for k in ['email', 'password', 'name']):
        return jsonify(error="بيانات ناقصة", message="يرجى توفير البريد الإلكتروني وكلمة المرور والاسم"), 400
    
    # تحقق من عدم وجود مستخدم بنفس البريد الإلكتروني
    if User.query.filter_by(email=data['email']).first():
        return jsonify(error="البريد الإلكتروني موجود", message="البريد الإلكتروني مستخدم بالفعل"), 400
    
    # إنشاء مستخدم جديد
    new_user = User(
        email=data['email'],
        name=data['name'],
        password_hash=generate_password_hash(data['password']),
        role='user',
        is_active=True,
        created_at=datetime.datetime.utcnow()
    )
    
    # حفظ المستخدم في قاعدة البيانات
    db.session.add(new_user)
    db.session.commit()
    
    # إنشاء توكن المصادقة
    access_token = create_access_token(identity=new_user.id)
    refresh_token = create_refresh_token(identity=new_user.id)
    
    return jsonify(
        message="تم إنشاء المستخدم بنجاح",
        user={
            'id': new_user.id,
            'email': new_user.email,
            'name': new_user.name,
            'role': new_user.role
        },
        token=access_token,
        refresh_token=refresh_token
    ), 201

@auth.route('/login', methods=['POST'])
def login():
    """
    تسجيل الدخول للمستخدمين
    """
    # الحصول على بيانات تسجيل الدخول
    data = request.get_json()
    
    if not data:
        return jsonify(error="بيانات غير صالحة", message="لم يتم توفير البيانات المطلوبة"), 400
    
    # تحقق من وجود البيانات المطلوبة
    if not all(k in data for k in ['email', 'password']):
        return jsonify(error="بيانات ناقصة", message="يرجى توفير البريد الإلكتروني وكلمة المرور"), 400
    
    # البحث عن المستخدم
    user = User.query.filter_by(email=data['email']).first()
    
    # التحقق من وجود المستخدم وصحة كلمة المرور
    if not user or not check_password_hash(user.password_hash, data['password']):
        return jsonify(error="بيانات غير صحيحة", message="البريد الإلكتروني أو كلمة المرور غير صحيحة"), 401
    
    # التحقق من أن المستخدم نشط
    if not user.is_active:
        return jsonify(error="حساب غير نشط", message="حسابك غير نشط حالياً، يرجى التواصل مع الإدارة"), 403
    
    # تحديث وقت آخر تسجيل دخول
    user.last_login = datetime.datetime.utcnow()
    db.session.commit()
    
    # إنشاء توكن المصادقة
    access_token = create_access_token(identity=user.id)
    refresh_token = create_refresh_token(identity=user.id)
    
    # حفظ بيانات المستخدم في الجلسة
    session['user_id'] = user.id
    session['user_email'] = user.email
    session['user_name'] = user.name
    session['user_role'] = user.role
    
    return jsonify(
        message="تم تسجيل الدخول بنجاح",
        user={
            'id': user.id,
            'email': user.email,
            'name': user.name,
            'role': user.role
        },
        token=access_token,
        refresh_token=refresh_token
    ), 200

@auth.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """
    تجديد توكن المصادقة
    """
    current_user_id = get_jwt_identity()
    access_token = create_access_token(identity=current_user_id)
    
    return jsonify(token=access_token), 200

@auth.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    """
    الحصول على الملف الشخصي للمستخدم الحالي
    """
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user:
        return jsonify(error="مستخدم غير موجود", message="المستخدم غير موجود"), 404
    
    return jsonify(
        user={
            'id': user.id,
            'email': user.email,
            'name': user.name,
            'role': user.role,
            'is_active': user.is_active,
            'last_login': user.last_login.isoformat() if user.last_login else None,
            'created_at': user.created_at.isoformat()
        }
    ), 200

@auth.route('/logout', methods=['POST'])
def logout():
    """
    تسجيل الخروج
    """
    # إزالة بيانات المستخدم من الجلسة
    session.pop('user_id', None)
    session.pop('user_email', None)
    session.pop('user_name', None)
    session.pop('user_role', None)
    
    return jsonify(message="تم تسجيل الخروج بنجاح"), 200
