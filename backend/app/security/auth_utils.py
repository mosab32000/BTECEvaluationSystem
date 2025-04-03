"""
وحدة المصادقة الأساسية لنظام تقييم BTEC
توفر أدوات للمصادقة وإدارة الجلسات
"""

import os
import jwt
import logging
import datetime
from typing import Dict, Any, Optional
from flask import request, jsonify, current_app
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps

# إعداد السجل
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def generate_token(user_id: int, email: str, role: str = 'user', expiry_hours: int = 24) -> str:
    """
    إنشاء رمز JWT
    
    Args:
        user_id: معرف المستخدم
        email: البريد الإلكتروني للمستخدم
        role: دور المستخدم (user, teacher, admin)
        expiry_hours: عدد ساعات صلاحية الرمز
        
    Returns:
        رمز JWT
    """
    jwt_secret = os.environ.get('JWT_SECRET_KEY') or current_app.config.get('JWT_SECRET_KEY')
    if not jwt_secret:
        logger.warning("JWT_SECRET_KEY غير معرف. سيتم استخدام مفتاح افتراضي غير آمن.")
        jwt_secret = "insecure_default_key_replace_in_production"
    
    payload = {
        'sub': user_id,
        'email': email,
        'role': role,
        'iat': datetime.datetime.utcnow(),
        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=expiry_hours)
    }
    
    token = jwt.encode(payload, jwt_secret, algorithm='HS256')
    logger.info(f"تم إنشاء رمز JWT للمستخدم: {email}")
    
    return token

def validate_token(token: str) -> Dict[str, Any]:
    """
    التحقق من صحة رمز JWT
    
    Args:
        token: رمز JWT
        
    Returns:
        معلومات المستخدم إذا كان الرمز صالحًا، أو قاموس خطأ
    """
    jwt_secret = os.environ.get('JWT_SECRET_KEY') or current_app.config.get('JWT_SECRET_KEY')
    if not jwt_secret:
        logger.warning("JWT_SECRET_KEY غير معرف. سيتم استخدام مفتاح افتراضي غير آمن.")
        jwt_secret = "insecure_default_key_replace_in_production"
    
    try:
        payload = jwt.decode(token, jwt_secret, algorithms=['HS256'])
        return {
            'valid': True,
            'user_id': payload['sub'],
            'email': payload['email'],
            'role': payload.get('role', 'user')
        }
    except jwt.ExpiredSignatureError:
        logger.warning("رمز JWT منتهي الصلاحية")
        return {'valid': False, 'error': 'Token expired'}
    except jwt.InvalidTokenError as e:
        logger.warning(f"رمز JWT غير صالح: {str(e)}")
        return {'valid': False, 'error': f'Invalid token: {str(e)}'}

def hash_password(password: str) -> str:
    """
    تشفير كلمة المرور
    
    Args:
        password: كلمة المرور
        
    Returns:
        كلمة المرور المشفرة
    """
    return generate_password_hash(password)

def verify_password(hashed_password: str, password: str) -> bool:
    """
    التحقق من صحة كلمة المرور
    
    Args:
        hashed_password: كلمة المرور المشفرة
        password: كلمة المرور المدخلة
        
    Returns:
        True إذا كانت كلمة المرور صحيحة، False خلاف ذلك
    """
    return check_password_hash(hashed_password, password)

def token_required(f):
    """
    زخرفة للتحقق من وجود رمز JWT صالح
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        # البحث عن الرمز في الترويسة
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            if auth_header.startswith('Bearer '):
                token = auth_header.split(' ')[1]
        
        if not token:
            logger.warning("عدم وجود رمز JWT في الطلب")
            return jsonify({'message': 'Authentication token is missing!'}), 401
        
        # التحقق من صحة الرمز
        token_data = validate_token(token)
        
        if not token_data['valid']:
            logger.warning(f"رمز JWT غير صالح: {token_data.get('error')}")
            return jsonify({'message': f'Invalid authentication token: {token_data.get("error")}'}), 401
        
        # إضافة معرف المستخدم إلى الـ kwargs
        kwargs['user_id'] = token_data['user_id']
        
        return f(*args, **kwargs)
    
    return decorated

def admin_required(f):
    """
    زخرفة للتحقق من وجود رمز JWT صالح ودور المسؤول
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        # البحث عن الرمز في الترويسة
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            if auth_header.startswith('Bearer '):
                token = auth_header.split(' ')[1]
        
        if not token:
            logger.warning("عدم وجود رمز JWT في الطلب")
            return jsonify({'message': 'Authentication token is missing!'}), 401
        
        # التحقق من صحة الرمز
        token_data = validate_token(token)
        
        if not token_data['valid']:
            logger.warning(f"رمز JWT غير صالح: {token_data.get('error')}")
            return jsonify({'message': f'Invalid authentication token: {token_data.get("error")}'}), 401
        
        # التحقق من دور المستخدم
        if token_data.get('role') != 'admin':
            logger.warning(f"محاولة الوصول غير المصرح به من المستخدم {token_data.get('email')}")
            return jsonify({'message': 'Admin privileges required!'}), 403
        
        # إضافة معرف المستخدم إلى الـ kwargs
        kwargs['user_id'] = token_data['user_id']
        
        return f(*args, **kwargs)
    
    return decorated

def teacher_required(f):
    """
    زخرفة للتحقق من وجود رمز JWT صالح ودور المعلم أو المسؤول
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        # البحث عن الرمز في الترويسة
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            if auth_header.startswith('Bearer '):
                token = auth_header.split(' ')[1]
        
        if not token:
            logger.warning("عدم وجود رمز JWT في الطلب")
            return jsonify({'message': 'Authentication token is missing!'}), 401
        
        # التحقق من صحة الرمز
        token_data = validate_token(token)
        
        if not token_data['valid']:
            logger.warning(f"رمز JWT غير صالح: {token_data.get('error')}")
            return jsonify({'message': f'Invalid authentication token: {token_data.get("error")}'}), 401
        
        # التحقق من دور المستخدم
        if token_data.get('role') not in ['teacher', 'admin']:
            logger.warning(f"محاولة الوصول غير المصرح به من المستخدم {token_data.get('email')}")
            return jsonify({'message': 'Teacher or admin privileges required!'}), 403
        
        # إضافة معرف المستخدم إلى الـ kwargs
        kwargs['user_id'] = token_data['user_id']
        
        return f(*args, **kwargs)
    
    return decorated

def get_user_id_from_request() -> Optional[int]:
    """
    استخراج معرف المستخدم من الطلب الحالي
    
    Returns:
        معرف المستخدم أو None إذا كان الرمز غير صالح
    """
    token = None
    
    # البحث عن الرمز في الترويسة
    if 'Authorization' in request.headers:
        auth_header = request.headers['Authorization']
        if auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
    
    if not token:
        return None
    
    # التحقق من صحة الرمز
    token_data = validate_token(token)
    
    if not token_data['valid']:
        return None
    
    return token_data['user_id']