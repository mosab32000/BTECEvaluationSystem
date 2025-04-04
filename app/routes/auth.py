"""
مسارات المصادقة في نظام تقييم BTEC
"""
import logging
from datetime import datetime, timezone, timedelta

from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import (
    create_access_token, create_refresh_token, 
    jwt_required, get_jwt_identity
)

from app import db
from app.models.user import User
from app.database import log_audit

# إنشاء Blueprint للمصادقة
auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/register', methods=['POST'])
def register():
    """
    تسجيل مستخدم جديد
    """
    data = request.json
    
    # التحقق من وجود البيانات المطلوبة
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({
            'status': 'error',
            'message': 'البريد الإلكتروني وكلمة المرور مطلوبان'
        }), 400
    
    # التحقق مما إذا كان المستخدم موجودًا بالفعل
    existing_user = User.query.filter_by(email=data['email']).first()
    if existing_user:
        return jsonify({
            'status': 'error',
            'message': 'البريد الإلكتروني مسجل بالفعل'
        }), 400
    
    # إنشاء المستخدم الجديد
    user = User(
        name=data.get('name', ''),
        email=data['email'],
        password_hash=generate_password_hash(data['password']),
        role='user',
        is_active=True
    )
    
    try:
        # حفظ المستخدم في قاعدة البيانات
        db.session.add(user)
        db.session.commit()
        
        # إنشاء رموز الوصول والتحديث
        access_token = create_access_token(identity=user.id)
        refresh_token = create_refresh_token(identity=user.id)
        
        # تسجيل الحدث
        log_audit('user_register', user.email, {'id': user.id})
        
        # إرجاع النجاح
        return jsonify({
            'status': 'success',
            'message': 'تم التسجيل بنجاح',
            'access_token': access_token,
            'refresh_token': refresh_token,
            'user': user.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        logging.error(f"خطأ في تسجيل المستخدم: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'حدث خطأ أثناء التسجيل'
        }), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    """
    تسجيل دخول المستخدم
    """
    data = request.json
    
    # التحقق من وجود البيانات المطلوبة
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({
            'status': 'error',
            'message': 'البريد الإلكتروني وكلمة المرور مطلوبان'
        }), 400
    
    # البحث عن المستخدم
    user = User.query.filter_by(email=data['email']).first()
    
    # التحقق من وجود المستخدم وصحة كلمة المرور
    if not user or not user.check_password(data['password']):
        return jsonify({
            'status': 'error',
            'message': 'البريد الإلكتروني أو كلمة المرور غير صحيحة'
        }), 401
    
    # التحقق من أن المستخدم نشط
    if not user.is_active:
        return jsonify({
            'status': 'error',
            'message': 'الحساب غير نشط، يرجى التواصل مع المسؤول'
        }), 403
    
    # إنشاء رموز الوصول والتحديث
    access_token = create_access_token(identity=user.id)
    refresh_token = create_refresh_token(identity=user.id)
    
    # تسجيل الحدث
    log_audit('user_login', user.email, {'id': user.id})
    
    # إرجاع النجاح
    return jsonify({
        'status': 'success',
        'message': 'تم تسجيل الدخول بنجاح',
        'access_token': access_token,
        'refresh_token': refresh_token,
        'user': user.to_dict()
    }), 200

@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """
    تجديد رمز الوصول باستخدام رمز التحديث
    """
    current_user_id = get_jwt_identity()
    
    # البحث عن المستخدم
    user = User.query.get(current_user_id)
    
    if not user or not user.is_active:
        return jsonify({
            'status': 'error',
            'message': 'المستخدم غير موجود أو غير نشط'
        }), 401
    
    # إنشاء رمز وصول جديد
    access_token = create_access_token(identity=current_user_id)
    
    # تسجيل الحدث
    log_audit('token_refresh', user.email, {'id': user.id})
    
    # إرجاع النجاح
    return jsonify({
        'status': 'success',
        'message': 'تم تجديد الرمز بنجاح',
        'access_token': access_token
    }), 200

@auth_bp.route('/user', methods=['GET'])
@jwt_required()
def get_user():
    """
    الحصول على معلومات المستخدم الحالي
    """
    current_user_id = get_jwt_identity()
    
    # البحث عن المستخدم
    user = User.query.get(current_user_id)
    
    if not user:
        return jsonify({
            'status': 'error',
            'message': 'المستخدم غير موجود'
        }), 404
    
    # إرجاع معلومات المستخدم
    return jsonify({
        'status': 'success',
        'user': user.to_dict()
    }), 200

@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    """
    تسجيل خروج المستخدم
    """
    current_user_id = get_jwt_identity()
    
    # البحث عن المستخدم
    user = User.query.get(current_user_id)
    
    if user:
        # تسجيل الحدث
        log_audit('user_logout', user.email, {'id': user.id})
    
    # إرجاع النجاح
    return jsonify({
        'status': 'success',
        'message': 'تم تسجيل الخروج بنجاح'
    }), 200

@auth_bp.route('/change-password', methods=['POST'])
@jwt_required()
def change_password():
    """
    تغيير كلمة مرور المستخدم
    """
    current_user_id = get_jwt_identity()
    data = request.json
    
    # التحقق من وجود البيانات المطلوبة
    if not data or not data.get('current_password') or not data.get('new_password'):
        return jsonify({
            'status': 'error',
            'message': 'كلمة المرور الحالية والجديدة مطلوبة'
        }), 400
    
    # البحث عن المستخدم
    user = User.query.get(current_user_id)
    
    if not user:
        return jsonify({
            'status': 'error',
            'message': 'المستخدم غير موجود'
        }), 404
    
    # التحقق من كلمة المرور الحالية
    if not user.check_password(data['current_password']):
        return jsonify({
            'status': 'error',
            'message': 'كلمة المرور الحالية غير صحيحة'
        }), 401
    
    try:
        # تعيين كلمة المرور الجديدة
        user.set_password(data['new_password'])
        db.session.commit()
        
        # تسجيل الحدث
        log_audit('password_change', user.email, {'id': user.id})
        
        # إرجاع النجاح
        return jsonify({
            'status': 'success',
            'message': 'تم تغيير كلمة المرور بنجاح'
        }), 200
    except Exception as e:
        db.session.rollback()
        logging.error(f"خطأ في تغيير كلمة المرور: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'حدث خطأ أثناء تغيير كلمة المرور'
        }), 500
