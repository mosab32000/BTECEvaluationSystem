"""
وحدة الأمان في نظام تقييم BTEC
توفر وظائف للتشفير والتوثيق والمصادقة وإدارة الهوية
"""
import os
import base64
import secrets
import hashlib
from datetime import datetime, timedelta
import uuid

import jwt
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from flask import current_app
from flask_jwt_extended import create_access_token, create_refresh_token
from werkzeug.security import generate_password_hash, check_password_hash

def generate_encryption_key(password, salt=None):
    """
    توليد مفتاح تشفير من كلمة مرور وملح
    
    Args:
        password: كلمة المرور
        salt: الملح (اختياري)
        
    Returns:
        tuple: (المفتاح المشفر، الملح)
    """
    if salt is None:
        salt = os.urandom(16)
    
    # استخدام PBKDF2 لاشتقاق مفتاح
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000
    )
    
    # اشتقاق المفتاح من كلمة المرور
    key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
    
    return key, salt

def encrypt_data(data, key=None):
    """
    تشفير البيانات
    
    Args:
        data: البيانات المراد تشفيرها
        key: مفتاح التشفير (اختياري)
        
    Returns:
        str: البيانات المشفرة
    """
    # إذا لم يتم توفير مفتاح، استخدام المفتاح من التطبيق
    if key is None:
        key = current_app.config.get('ENCRYPTION_KEY')
        if not key:
            raise ValueError('مفتاح التشفير غير موجود')
    
    # إنشاء مفتاح Fernet
    if not isinstance(key, bytes):
        key = key.encode()
    
    if len(base64.urlsafe_b64decode(key + b'=' * (-len(key) % 4))) != 32:
        key = base64.urlsafe_b64encode(hashlib.sha256(key).digest())
    
    f = Fernet(key)
    
    # تشفير البيانات
    if isinstance(data, str):
        data = data.encode()
    
    return f.encrypt(data).decode()

def decrypt_data(encrypted_data, key=None):
    """
    فك تشفير البيانات
    
    Args:
        encrypted_data: البيانات المشفرة
        key: مفتاح التشفير (اختياري)
        
    Returns:
        str: البيانات بعد فك التشفير
    """
    # إذا لم يتم توفير مفتاح، استخدام المفتاح من التطبيق
    if key is None:
        key = current_app.config.get('ENCRYPTION_KEY')
        if not key:
            raise ValueError('مفتاح التشفير غير موجود')
    
    # إنشاء مفتاح Fernet
    if not isinstance(key, bytes):
        key = key.encode()
    
    if len(base64.urlsafe_b64decode(key + b'=' * (-len(key) % 4))) != 32:
        key = base64.urlsafe_b64encode(hashlib.sha256(key).digest())
    
    f = Fernet(key)
    
    # فك تشفير البيانات
    if isinstance(encrypted_data, str):
        encrypted_data = encrypted_data.encode()
    
    return f.decrypt(encrypted_data).decode()

def generate_tokens(user_id):
    """
    توليد رموز الوصول والتحديث
    
    Args:
        user_id: معرف المستخدم
        
    Returns:
        tuple: (رمز الوصول، رمز التحديث)
    """
    # إضافة المعلومات الإضافية
    access_claims = {
        'type': 'access',
        'jti': str(uuid.uuid4())
    }
    
    refresh_claims = {
        'type': 'refresh',
        'jti': str(uuid.uuid4())
    }
    
    # توليد الرموز
    access_token = create_access_token(
        identity=user_id,
        additional_claims=access_claims
    )
    
    refresh_token = create_refresh_token(
        identity=user_id,
        additional_claims=refresh_claims
    )
    
    return access_token, refresh_token

def generate_token(data, expiry=None, token_type='general'):
    """
    توليد رمز مميز
    
    Args:
        data: البيانات المراد تضمينها في الرمز
        expiry: مدة الصلاحية (اختياري)
        token_type: نوع الرمز (اختياري)
        
    Returns:
        str: الرمز المميز
    """
    if expiry is None:
        expiry = timedelta(hours=24)
    
    # حساب وقت انتهاء الصلاحية
    exp = datetime.utcnow() + expiry
    
    # إنشاء البيانات
    payload = {
        'exp': exp,
        'iat': datetime.utcnow(),
        'type': token_type,
        'jti': str(uuid.uuid4()),
        'data': data
    }
    
    # توليد الرمز
    token = jwt.encode(
        payload,
        current_app.config.get('SECRET_KEY'),
        algorithm='HS256'
    )
    
    return token

def verify_token(token, token_type='general'):
    """
    التحقق من صحة الرمز المميز
    
    Args:
        token: الرمز المميز
        token_type: نوع الرمز (اختياري)
        
    Returns:
        dict: بيانات الرمز إذا كان صالحًا، أو None إذا كان غير صالح
    """
    try:
        # فك تشفير الرمز
        payload = jwt.decode(
            token,
            current_app.config.get('SECRET_KEY'),
            algorithms=['HS256']
        )
        
        # التحقق من نوع الرمز
        if payload.get('type') != token_type:
            return None
        
        return payload.get('data')
    
    except jwt.ExpiredSignatureError:
        # الرمز منتهي الصلاحية
        return None
    except jwt.InvalidTokenError:
        # الرمز غير صالح
        return None

def generate_verification_token(user_id):
    """
    توليد رمز للتحقق من البريد الإلكتروني
    
    Args:
        user_id: معرف المستخدم
        
    Returns:
        str: رمز التحقق
    """
    data = {
        'user_id': user_id,
        'purpose': 'email_verification'
    }
    
    return generate_token(data, expiry=timedelta(days=7), token_type='verification')

def generate_reset_token(user_id):
    """
    توليد رمز لإعادة تعيين كلمة المرور
    
    Args:
        user_id: معرف المستخدم
        
    Returns:
        str: رمز إعادة التعيين
    """
    data = {
        'user_id': user_id,
        'purpose': 'password_reset'
    }
    
    return generate_token(data, expiry=timedelta(hours=24), token_type='reset')

def generate_secure_filename(filename):
    """
    توليد اسم ملف آمن
    
    Args:
        filename: اسم الملف الأصلي
        
    Returns:
        str: اسم الملف الآمن
    """
    from werkzeug.utils import secure_filename
    
    # الحصول على الامتداد
    ext = ''
    if '.' in filename:
        ext = '.' + filename.rsplit('.', 1)[1].lower()
    
    # توليد اسم آمن
    name = secure_filename(filename)
    if ext and name.endswith(ext):
        name = name[:-len(ext)]
    
    # إضافة معرف فريد
    unique_id = secrets.token_hex(8)
    timestamp = int(datetime.utcnow().timestamp())
    
    # إنشاء الاسم النهائي
    return f"{name}_{timestamp}_{unique_id}{ext}"

def hash_file(file_path):
    """
    حساب هاش SHA-256 لملف
    
    Args:
        file_path: مسار الملف
        
    Returns:
        str: هاش الملف
    """
    # فتح الملف وقراءة المحتوى تدريجيًا
    h = hashlib.sha256()
    
    with open(file_path, 'rb') as file:
        chunk = 0
        while chunk := file.read(8192):
            h.update(chunk)
    
    return h.hexdigest()

def hash_data(data):
    """
    حساب هاش SHA-256 للبيانات
    
    Args:
        data: البيانات المراد حساب الهاش لها
        
    Returns:
        str: هاش البيانات
    """
    h = hashlib.sha256()
    
    if isinstance(data, str):
        data = data.encode()
    
    h.update(data)
    
    return h.hexdigest()

def generate_api_key():
    """
    توليد مفتاح API
    
    Returns:
        str: مفتاح API
    """
    prefix = 'btec'
    key = secrets.token_hex(16)
    return f"{prefix}_{key}"