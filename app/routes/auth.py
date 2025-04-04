"""
مسارات المصادقة في نظام تقييم BTEC
"""
import datetime
import logging
from functools import wraps

from flask import Blueprint, jsonify, request, current_app
from flask_jwt_extended import (
    create_access_token, create_refresh_token, get_jwt_identity, jwt_required,
    get_jwt, verify_jwt_in_request
)
from werkzeug.security import check_password_hash, generate_password_hash

from app import db
from app.models.user import User, BlacklistedToken
from app.core.security import generate_tokens, verify_token, generate_verification_token

logger = logging.getLogger(__name__)

# إنشاء blueprint للمصادقة
auth_bp = Blueprint('auth', __name__)

# الزخارف المساعدة
def admin_required(fn):
    """
    زخرفة للتحقق من أن المستخدم مسؤول
    """
    @wraps(fn)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if user and user.is_admin():
            return fn(*args, **kwargs)
        else:
            return jsonify(
                status='error',
                message='يتطلب هذا الإجراء صلاحيات المسؤول'
            ), 403
    
    return wrapper

def instructor_required(fn):
    """
    زخرفة للتحقق من أن المستخدم مدرس
    """
    @wraps(fn)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if user and (user.is_instructor() or user.is_admin()):
            return fn(*args, **kwargs)
        else:
            return jsonify(
                status='error',
                message='يتطلب هذا الإجراء صلاحيات المدرس'
            ), 403
    
    return wrapper

# وظائف المساعدة
def check_if_token_is_revoked(jwt_header, jwt_payload):
    """
    التحقق مما إذا كان الرمز المميز محظورًا
    
    Args:
        jwt_header: رأس JWT
        jwt_payload: حمولة JWT
        
    Returns:
        bool: ما إذا كان الرمز المميز محظورًا
    """
    jti = jwt_payload['jti']
    return BlacklistedToken.is_blacklisted(jti)

# مسارات المصادقة
@auth_bp.route('/register', methods=['POST'])
def register():
    """
    تسجيل مستخدم جديد
    """
    try:
        data = request.get_json()
        
        # التحقق من البيانات
        required_fields = ['email', 'password', 'name']
        for field in required_fields:
            if field not in data:
                return jsonify(
                    status='error',
                    message=f'الحقل {field} مطلوب'
                ), 400
        
        email = data.get('email')
        password = data.get('password')
        name = data.get('name')
        
        # التحقق من أن البريد الإلكتروني غير مستخدم
        if User.query.filter_by(email=email).first():
            return jsonify(
                status='error',
                message='البريد الإلكتروني مستخدم بالفعل'
            ), 400
        
        # إنشاء المستخدم
        user = User()
        user.email = email
        user.password = password  # يستخدم خاصية @password.setter لتجزئة كلمة المرور
        user.name = name
        user.role = data.get('role', 'student')
        user.institution = data.get('institution')
        user.position = data.get('position')
        
        # التأكد من أن المسؤولين فقط يمكنهم إنشاء مدرسين أو مسؤولين
        if user.role in ['admin', 'instructor']:
            try:
                # التحقق من أن المستخدم الحالي مسؤول
                verify_jwt_in_request()
                current_user_id = get_jwt_identity()
                current_user = User.query.get(current_user_id)
                
                if not current_user or not current_user.is_admin():
                    user.role = 'student'  # إعادة تعيين الدور إلى طالب
            except:
                user.role = 'student'  # إعادة تعيين الدور إلى طالب
        
        # حفظ المستخدم
        db.session.add(user)
        db.session.commit()
        
        # إرسال إشعار تفعيل للمستخدم (إذا لزم الأمر)
        if current_app.config.get('REQUIRE_EMAIL_VERIFICATION', False):
            verification_token = generate_verification_token(user.id)
            # TODO: إرسال بريد إلكتروني للتحقق
        
        return jsonify(
            status='success',
            message='تم تسجيل المستخدم بنجاح',
            user=user.to_dict()
        ), 201
    
    except Exception as e:
        logger.error(f"خطأ في تسجيل المستخدم: {str(e)}")
        db.session.rollback()
        return jsonify(
            status='error',
            message='حدث خطأ أثناء تسجيل المستخدم',
            error=str(e)
        ), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    """
    تسجيل الدخول
    """
    try:
        data = request.get_json()
        
        # التحقق من البيانات
        if not data or not data.get('email') or not data.get('password'):
            return jsonify(
                status='error',
                message='البريد الإلكتروني وكلمة المرور مطلوبان'
            ), 400
        
        email = data.get('email')
        password = data.get('password')
        
        # التحقق من بيانات المستخدم
        user = User.query.filter_by(email=email).first()
        
        if not user or not user.verify_password(password):
            return jsonify(
                status='error',
                message='البريد الإلكتروني أو كلمة المرور غير صحيحة'
            ), 401
        
        if not user.is_active:
            return jsonify(
                status='error',
                message='الحساب غير نشط'
            ), 401
        
        # توليد الرموز المميزة
        access_token, refresh_token = generate_tokens(user.id)
        
        # تحديث وقت آخر تسجيل دخول
        user.update_last_login()
        
        return jsonify(
            status='success',
            message='تم تسجيل الدخول بنجاح',
            access_token=access_token,
            refresh_token=refresh_token,
            user=user.to_dict()
        ), 200
    
    except Exception as e:
        logger.error(f"خطأ في تسجيل الدخول: {str(e)}")
        return jsonify(
            status='error',
            message='حدث خطأ أثناء تسجيل الدخول',
            error=str(e)
        ), 500

@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    """
    تسجيل الخروج
    """
    try:
        jti = get_jwt()['jti']
        user_id = get_jwt_identity()
        
        # إضافة الرمز المميز إلى القائمة السوداء
        token_type = get_jwt()['type']
        expires = datetime.datetime.fromtimestamp(get_jwt()['exp'])
        
        blacklisted_token = BlacklistedToken(
            jti=jti,
            token_type=token_type,
            user_id=user_id,
            expires=expires
        )
        
        db.session.add(blacklisted_token)
        db.session.commit()
        
        return jsonify(
            status='success',
            message='تم تسجيل الخروج بنجاح'
        ), 200
    
    except Exception as e:
        logger.error(f"خطأ في تسجيل الخروج: {str(e)}")
        db.session.rollback()
        return jsonify(
            status='error',
            message='حدث خطأ أثناء تسجيل الخروج',
            error=str(e)
        ), 500

@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """
    تحديث الرمز المميز للوصول
    """
    try:
        user_id = get_jwt_identity()
        
        # توليد رمز وصول جديد
        access_token = create_access_token(
            identity=user_id,
            additional_claims={
                'type': 'access'
            }
        )
        
        return jsonify(
            status='success',
            message='تم تحديث الرمز المميز بنجاح',
            access_token=access_token
        ), 200
    
    except Exception as e:
        logger.error(f"خطأ في تحديث الرمز المميز: {str(e)}")
        return jsonify(
            status='error',
            message='حدث خطأ أثناء تحديث الرمز المميز',
            error=str(e)
        ), 500

@auth_bp.route('/verify/<token>', methods=['GET'])
def verify_email(token):
    """
    التحقق من البريد الإلكتروني
    
    Args:
        token: الرمز المميز للتحقق
    """
    try:
        # التحقق من صحة الرمز المميز
        payload = verify_token(token, token_type='verification')
        
        if not payload:
            return jsonify(
                status='error',
                message='الرمز المميز غير صالح أو منتهي الصلاحية'
            ), 400
        
        # تحديث حالة التحقق للمستخدم
        user_id = payload.get('user_id')
        user = User.query.get(user_id)
        
        if not user:
            return jsonify(
                status='error',
                message='المستخدم غير موجود'
            ), 404
        
        user.is_verified = True
        db.session.commit()
        
        return jsonify(
            status='success',
            message='تم التحقق من البريد الإلكتروني بنجاح'
        ), 200
    
    except Exception as e:
        logger.error(f"خطأ في التحقق من البريد الإلكتروني: {str(e)}")
        db.session.rollback()
        return jsonify(
            status='error',
            message='حدث خطأ أثناء التحقق من البريد الإلكتروني',
            error=str(e)
        ), 500

@auth_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    """
    الحصول على الملف الشخصي للمستخدم
    """
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify(
                status='error',
                message='المستخدم غير موجود'
            ), 404
        
        return jsonify(
            status='success',
            user=user.to_dict(include_private=True)
        ), 200
    
    except Exception as e:
        logger.error(f"خطأ في الحصول على الملف الشخصي: {str(e)}")
        return jsonify(
            status='error',
            message='حدث خطأ أثناء الحصول على الملف الشخصي',
            error=str(e)
        ), 500

@auth_bp.route('/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    """
    تحديث الملف الشخصي للمستخدم
    """
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify(
                status='error',
                message='المستخدم غير موجود'
            ), 404
        
        data = request.get_json()
        
        # تحديث البيانات
        if 'name' in data:
            user.name = data['name']
        
        if 'institution' in data:
            user.institution = data['institution']
        
        if 'position' in data:
            user.position = data['position']
        
        if 'password' in data and data['password']:
            # التحقق من كلمة المرور الحالية
            current_password = data.get('current_password')
            if not current_password or not user.verify_password(current_password):
                return jsonify(
                    status='error',
                    message='كلمة المرور الحالية غير صحيحة'
                ), 400
            
            # تحديث كلمة المرور
            user.password = data['password']
        
        db.session.commit()
        
        return jsonify(
            status='success',
            message='تم تحديث الملف الشخصي بنجاح',
            user=user.to_dict(include_private=True)
        ), 200
    
    except Exception as e:
        logger.error(f"خطأ في تحديث الملف الشخصي: {str(e)}")
        db.session.rollback()
        return jsonify(
            status='error',
            message='حدث خطأ أثناء تحديث الملف الشخصي',
            error=str(e)
        ), 500

@auth_bp.route('/users', methods=['GET'])
@admin_required
def get_users():
    """
    الحصول على قائمة المستخدمين (للمسؤولين فقط)
    """
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        role = request.args.get('role')
        
        # إعداد الاستعلام
        query = User.query
        
        if role:
            query = query.filter_by(role=role)
        
        # تنفيذ الاستعلام مع التصفح
        users = query.paginate(page=page, per_page=per_page)
        
        return jsonify(
            status='success',
            users=[user.to_dict() for user in users.items],
            total=users.total,
            pages=users.pages,
            page=page,
            per_page=per_page
        ), 200
    
    except Exception as e:
        logger.error(f"خطأ في الحصول على قائمة المستخدمين: {str(e)}")
        return jsonify(
            status='error',
            message='حدث خطأ أثناء الحصول على قائمة المستخدمين',
            error=str(e)
        ), 500

@auth_bp.route('/users/<int:user_id>', methods=['GET'])
@admin_required
def get_user(user_id):
    """
    الحصول على بيانات مستخدم (للمسؤولين فقط)
    
    Args:
        user_id: معرف المستخدم
    """
    try:
        user = User.query.get(user_id)
        
        if not user:
            return jsonify(
                status='error',
                message='المستخدم غير موجود'
            ), 404
        
        return jsonify(
            status='success',
            user=user.to_dict(include_private=True)
        ), 200
    
    except Exception as e:
        logger.error(f"خطأ في الحصول على بيانات المستخدم: {str(e)}")
        return jsonify(
            status='error',
            message='حدث خطأ أثناء الحصول على بيانات المستخدم',
            error=str(e)
        ), 500

@auth_bp.route('/users/<int:user_id>', methods=['PUT'])
@admin_required
def update_user(user_id):
    """
    تحديث بيانات مستخدم (للمسؤولين فقط)
    
    Args:
        user_id: معرف المستخدم
    """
    try:
        user = User.query.get(user_id)
        
        if not user:
            return jsonify(
                status='error',
                message='المستخدم غير موجود'
            ), 404
        
        data = request.get_json()
        
        # تحديث البيانات
        if 'name' in data:
            user.name = data['name']
        
        if 'email' in data:
            # التحقق من أن البريد الإلكتروني غير مستخدم
            existing_user = User.query.filter_by(email=data['email']).first()
            if existing_user and existing_user.id != user_id:
                return jsonify(
                    status='error',
                    message='البريد الإلكتروني مستخدم بالفعل'
                ), 400
            
            user.email = data['email']
        
        if 'role' in data:
            user.role = data['role']
        
        if 'is_active' in data:
            user.is_active = data['is_active']
        
        if 'is_verified' in data:
            user.is_verified = data['is_verified']
        
        if 'institution' in data:
            user.institution = data['institution']
        
        if 'position' in data:
            user.position = data['position']
        
        if 'password' in data and data['password']:
            user.password = data['password']
        
        db.session.commit()
        
        return jsonify(
            status='success',
            message='تم تحديث بيانات المستخدم بنجاح',
            user=user.to_dict(include_private=True)
        ), 200
    
    except Exception as e:
        logger.error(f"خطأ في تحديث بيانات المستخدم: {str(e)}")
        db.session.rollback()
        return jsonify(
            status='error',
            message='حدث خطأ أثناء تحديث بيانات المستخدم',
            error=str(e)
        ), 500

@auth_bp.route('/users/<int:user_id>', methods=['DELETE'])
@admin_required
def delete_user(user_id):
    """
    حذف مستخدم (للمسؤولين فقط)
    
    Args:
        user_id: معرف المستخدم
    """
    try:
        user = User.query.get(user_id)
        
        if not user:
            return jsonify(
                status='error',
                message='المستخدم غير موجود'
            ), 404
        
        # الحماية من حذف المسؤول الوحيد
        if user.is_admin():
            admin_count = User.query.filter_by(role='admin').count()
            if admin_count <= 1:
                return jsonify(
                    status='error',
                    message='لا يمكن حذف المسؤول الوحيد'
                ), 400
        
        db.session.delete(user)
        db.session.commit()
        
        return jsonify(
            status='success',
            message='تم حذف المستخدم بنجاح'
        ), 200
    
    except Exception as e:
        logger.error(f"خطأ في حذف المستخدم: {str(e)}")
        db.session.rollback()
        return jsonify(
            status='error',
            message='حدث خطأ أثناء حذف المستخدم',
            error=str(e)
        ), 500