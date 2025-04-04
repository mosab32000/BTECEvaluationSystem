"""
مسارات المصادقة والتسجيل
"""
import datetime
import logging
from functools import wraps

from flask import Blueprint, current_app, g, jsonify, request
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import (
    create_access_token, create_refresh_token, get_jwt_identity,
    jwt_required, get_jwt
)

from app import db, jwt, cache, limiter
from app.core.security import sanitize_input
from app.database import log_audit, update_metrics
from app.models.user import User

# إعداد المسارات
auth_bp = Blueprint('auth', __name__)
logger = logging.getLogger(__name__)

# إعداد محدد الطلبات
auth_limiter = limiter.shared_limit(
    "20 per minute", 
    scope="auth"
)

@auth_bp.route('/register', methods=['POST'])
@auth_limiter
def register():
    """
    تسجيل مستخدم جديد
    
    طريقة الطلب: POST
    المسار: /api/auth/register
    الحقول المطلوبة:
        - email: البريد الإلكتروني
        - password: كلمة المرور
        - name: الاسم (اختياري)
    """
    try:
        data = request.get_json()
        
        # التحقق من وجود البيانات المطلوبة
        if not data or not data.get('email') or not data.get('password'):
            return jsonify({
                'status': 'error',
                'message': 'البريد الإلكتروني وكلمة المرور مطلوبان'
            }), 400
        
        # التحقق من تنسيق البريد الإلكتروني وطول كلمة المرور
        email = sanitize_input(data.get('email')).lower()
        password = data.get('password')
        name = sanitize_input(data.get('name', ''))
        
        if len(password) < 8:
            return jsonify({
                'status': 'error',
                'message': 'يجب أن تكون كلمة المرور 8 أحرف على الأقل'
            }), 400
        
        # التحقق من عدم وجود المستخدم مسبقاً
        if User.get_by_email(email):
            return jsonify({
                'status': 'error',
                'message': 'البريد الإلكتروني مسجل بالفعل'
            }), 409
        
        # إنشاء المستخدم الجديد
        new_user = User()
        new_user.email = email
        new_user.set_password(password)
        new_user.name = name
        new_user.role = 'user'  # افتراضيًا، جميع المستخدمين الجدد هم من نوع 'user'
        
        db.session.add(new_user)
        db.session.commit()
        
        # تسجيل الحدث
        log_audit(
            event_type="user_register",
            user=email,
            details={
                "id": new_user.id,
                "name": name,
                "timestamp": datetime.datetime.now().isoformat()
            }
        )
        
        # تحديث المقاييس
        update_metrics(active_user=True)
        
        # إنشاء رموز JWT
        access_token = create_access_token(
            identity=new_user.id,
            additional_claims={
                'email': new_user.email,
                'role': new_user.role
            }
        )
        refresh_token = create_refresh_token(
            identity=new_user.id,
            additional_claims={
                'email': new_user.email,
                'role': new_user.role
            }
        )
        
        return jsonify({
            'status': 'success',
            'message': 'تم إنشاء الحساب بنجاح',
            'access_token': access_token,
            'refresh_token': refresh_token,
            'user': {
                'id': new_user.id,
                'email': new_user.email,
                'name': new_user.name,
                'role': new_user.role
            }
        }), 201
        
    except Exception as e:
        logger.error(f"Error in register: {str(e)}")
        db.session.rollback()
        
        log_audit(
            event_type="user_register_error",
            user=data.get('email') if data else "unknown",
            details=str(e)
        )
        
        return jsonify({
            'status': 'error',
            'message': 'حدث خطأ أثناء إنشاء الحساب'
        }), 500

@auth_bp.route('/login', methods=['POST'])
@auth_limiter
def login():
    """
    تسجيل الدخول
    
    طريقة الطلب: POST
    المسار: /api/auth/login
    الحقول المطلوبة:
        - email: البريد الإلكتروني
        - password: كلمة المرور
    """
    try:
        data = request.get_json()
        
        # التحقق من وجود البيانات المطلوبة
        if not data or not data.get('email') or not data.get('password'):
            return jsonify({
                'status': 'error',
                'message': 'البريد الإلكتروني وكلمة المرور مطلوبان'
            }), 400
        
        email = sanitize_input(data.get('email')).lower()
        password = data.get('password')
        
        # التحقق من وجود المستخدم وصحة كلمة المرور
        user = User.get_by_email(email)
        
        if not user or not user.check_password(password):
            # تسجيل محاولة دخول فاشلة
            log_audit(
                event_type="login_failed",
                user=email,
                details={
                    "reason": "Invalid credentials",
                    "timestamp": datetime.datetime.now().isoformat()
                }
            )
            
            return jsonify({
                'status': 'error',
                'message': 'البريد الإلكتروني أو كلمة المرور غير صحيحة'
            }), 401
        
        # التحقق من أن الحساب نشط
        if not user.is_active:
            log_audit(
                event_type="login_failed",
                user=email,
                details={
                    "reason": "Account disabled",
                    "timestamp": datetime.datetime.now().isoformat()
                }
            )
            
            return jsonify({
                'status': 'error',
                'message': 'هذا الحساب غير نشط'
            }), 403
        
        # إنشاء رموز JWT
        access_token = create_access_token(
            identity=user.id,
            additional_claims={
                'email': user.email,
                'role': user.role
            }
        )
        refresh_token = create_refresh_token(
            identity=user.id,
            additional_claims={
                'email': user.email,
                'role': user.role
            }
        )
        
        # تسجيل نجاح تسجيل الدخول
        log_audit(
            event_type="login_success",
            user=email,
            details={
                "user_id": user.id,
                "timestamp": datetime.datetime.now().isoformat()
            }
        )
        
        # تحديث المقاييس
        update_metrics(active_user=True)
        
        return jsonify({
            'status': 'success',
            'message': 'تم تسجيل الدخول بنجاح',
            'access_token': access_token,
            'refresh_token': refresh_token,
            'user': {
                'id': user.id,
                'email': user.email,
                'name': user.name,
                'role': user.role
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Error in login: {str(e)}")
        
        log_audit(
            event_type="login_error",
            user=data.get('email') if data else "unknown",
            details=str(e)
        )
        
        return jsonify({
            'status': 'error',
            'message': 'حدث خطأ أثناء تسجيل الدخول'
        }), 500

@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """
    تحديث رمز الوصول
    
    طريقة الطلب: POST
    المسار: /api/auth/refresh
    الرأس المطلوب:
        - Authorization: Bearer <refresh_token>
    """
    try:
        # الحصول على هوية المستخدم من رمز التحديث
        identity = get_jwt_identity()
        claims = get_jwt()
        
        # التحقق من وجود المستخدم
        user = User.get_by_id(identity)
        
        if not user:
            return jsonify({
                'status': 'error',
                'message': 'المستخدم غير موجود'
            }), 404
        
        # التحقق من أن الحساب نشط
        if not user.is_active:
            return jsonify({
                'status': 'error',
                'message': 'هذا الحساب غير نشط'
            }), 403
        
        # إنشاء رمز وصول جديد
        access_token = create_access_token(
            identity=identity,
            additional_claims={
                'email': user.email,
                'role': user.role
            }
        )
        
        log_audit(
            event_type="token_refresh",
            user=user.email,
            details={
                "user_id": user.id,
                "timestamp": datetime.datetime.now().isoformat()
            }
        )
        
        return jsonify({
            'status': 'success',
            'message': 'تم تحديث رمز الوصول بنجاح',
            'access_token': access_token
        }), 200
        
    except Exception as e:
        logger.error(f"Error in refresh: {str(e)}")
        
        try:
            identity = get_jwt_identity()
            user = User.get_by_id(identity)
            user_email = user.email if user else "unknown"
        except:
            user_email = "unknown"
        
        log_audit(
            event_type="token_refresh_error",
            user=user_email,
            details=str(e)
        )
        
        return jsonify({
            'status': 'error',
            'message': 'حدث خطأ أثناء تحديث رمز الوصول'
        }), 500

@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_user_info():
    """
    الحصول على معلومات المستخدم الحالي
    
    طريقة الطلب: GET
    المسار: /api/auth/me
    الرأس المطلوب:
        - Authorization: Bearer <access_token>
    """
    try:
        # الحصول على هوية المستخدم من رمز الوصول
        identity = get_jwt_identity()
        
        # الحصول على معلومات المستخدم
        user = User.get_by_id(identity)
        
        if not user:
            return jsonify({
                'status': 'error',
                'message': 'المستخدم غير موجود'
            }), 404
        
        return jsonify({
            'status': 'success',
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        logger.error(f"Error in get_user_info: {str(e)}")
        
        return jsonify({
            'status': 'error',
            'message': 'حدث خطأ أثناء الحصول على معلومات المستخدم'
        }), 500

@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    """
    تسجيل الخروج
    
    طريقة الطلب: POST
    المسار: /api/auth/logout
    الرأس المطلوب:
        - Authorization: Bearer <access_token>
    """
    try:
        # الحصول على هوية المستخدم من رمز الوصول
        jti = get_jwt()['jti']
        identity = get_jwt_identity()
        
        # الحصول على معلومات المستخدم
        user = User.get_by_id(identity)
        
        # إضافة رمز JWT إلى القائمة السوداء
        # هذا المثال يفترض أنك تستخدم Redis لتخزين رموز JWT التي تم تسجيل الخروج منها
        # يمكنك تنفيذ مقاربة مختلفة حسب احتياجاتك
        if getattr(current_app, 'config', {}).get('CACHE_TYPE') == 'RedisCache':
            # استخدام Redis
            cache.set(f'blacklist:{jti}', 'true', timeout=current_app.config.get('JWT_ACCESS_TOKEN_EXPIRES').total_seconds())
        
        # تسجيل الخروج
        log_audit(
            event_type="logout",
            user=user.email if user else str(identity),
            details={
                "user_id": identity,
                "timestamp": datetime.datetime.now().isoformat()
            }
        )
        
        return jsonify({
            'status': 'success',
            'message': 'تم تسجيل الخروج بنجاح'
        }), 200
        
    except Exception as e:
        logger.error(f"Error in logout: {str(e)}")
        
        return jsonify({
            'status': 'error',
            'message': 'حدث خطأ أثناء تسجيل الخروج'
        }), 500

@auth_bp.route('/change-password', methods=['POST'])
@jwt_required()
def change_password():
    """
    تغيير كلمة المرور
    
    طريقة الطلب: POST
    المسار: /api/auth/change-password
    الرأس المطلوب:
        - Authorization: Bearer <access_token>
    الحقول المطلوبة:
        - current_password: كلمة المرور الحالية
        - new_password: كلمة المرور الجديدة
    """
    try:
        data = request.get_json()
        
        # التحقق من وجود البيانات المطلوبة
        if not data or not data.get('current_password') or not data.get('new_password'):
            return jsonify({
                'status': 'error',
                'message': 'كلمة المرور الحالية والجديدة مطلوبتان'
            }), 400
        
        current_password = data.get('current_password')
        new_password = data.get('new_password')
        
        # التحقق من طول كلمة المرور الجديدة
        if len(new_password) < 8:
            return jsonify({
                'status': 'error',
                'message': 'يجب أن تكون كلمة المرور الجديدة 8 أحرف على الأقل'
            }), 400
        
        # الحصول على هوية المستخدم من رمز الوصول
        identity = get_jwt_identity()
        
        # الحصول على معلومات المستخدم
        user = User.get_by_id(identity)
        
        if not user:
            return jsonify({
                'status': 'error',
                'message': 'المستخدم غير موجود'
            }), 404
        
        # التحقق من صحة كلمة المرور الحالية
        if not user.check_password(current_password):
            return jsonify({
                'status': 'error',
                'message': 'كلمة المرور الحالية غير صحيحة'
            }), 401
        
        # تغيير كلمة المرور
        user.set_password(new_password)
        db.session.commit()
        
        # تسجيل تغيير كلمة المرور
        log_audit(
            event_type="password_change",
            user=user.email,
            details={
                "user_id": user.id,
                "timestamp": datetime.datetime.now().isoformat()
            }
        )
        
        return jsonify({
            'status': 'success',
            'message': 'تم تغيير كلمة المرور بنجاح'
        }), 200
        
    except Exception as e:
        logger.error(f"Error in change_password: {str(e)}")
        db.session.rollback()
        
        return jsonify({
            'status': 'error',
            'message': 'حدث خطأ أثناء تغيير كلمة المرور'
        }), 500

# إعداد التعامل مع رموز JWT
@jwt.token_in_blocklist_loader
def check_if_token_is_revoked(jwt_header, jwt_payload):
    """التحقق مما إذا كان الرمز في القائمة السوداء"""
    jti = jwt_payload['jti']
    
    if getattr(current_app, 'config', {}).get('CACHE_TYPE') == 'RedisCache':
        # استخدام Redis
        return cache.get(f'blacklist:{jti}') is not None
    
    return False