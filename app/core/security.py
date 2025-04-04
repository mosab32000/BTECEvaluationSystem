"""
وحدة الأمان لنظام تقييم BTEC
"""

import os
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from functools import wraps
from flask import request, jsonify, current_app
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
from app.models import User
import re
import html

class SecureVault:
    """
    صندوق آمن لتشفير وفك تشفير البيانات الحساسة
    """
    def __init__(self):
        # الحصول على مفتاح التشفير
        key = os.environ.get('ENCRYPTION_KEY')
        if not key:
            current_app.logger.warning("لم يتم تعيين ENCRYPTION_KEY، استخدام قيمة افتراضية")
            key = current_app.config.get('ENCRYPTION_KEY', 'default-encryption-key')
        
        # إنشاء مفتاح مشتق باستخدام PBKDF2
        salt = b'btec-evaluation-system-salt'  # يجب أن يكون ثابتًا لإعادة إنشاء نفس المفتاح
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        derived_key = base64.urlsafe_b64encode(kdf.derive(key.encode()))
        
        # إنشاء مثيل Fernet
        self.cipher = Fernet(derived_key)
    
    def encrypt(self, text: str) -> str:
        """
        تشفير نص
        """
        if not text:
            return ''
        
        encrypted_data = self.cipher.encrypt(text.encode('utf-8'))
        return base64.urlsafe_b64encode(encrypted_data).decode('utf-8')
    
    def decrypt(self, encrypted_text: str) -> str:
        """
        فك تشفير نص مشفر
        """
        if not encrypted_text:
            return ''
        
        try:
            encrypted_data = base64.urlsafe_b64decode(encrypted_text)
            decrypted_data = self.cipher.decrypt(encrypted_data)
            return decrypted_data.decode('utf-8')
        except Exception as e:
            current_app.logger.error(f"خطأ في فك التشفير: {str(e)}")
            return ''

def sanitize_input(text: str) -> str:
    """
    تنقية المدخلات النصية من المحتويات الضارة
    """
    if not text:
        return ''
    
    # إزالة علامات HTML
    clean_text = html.escape(text)
    
    # تنظيف حقن JavaScript
    clean_text = re.sub(r'javascript:', '', clean_text, flags=re.IGNORECASE)
    
    # تنظيف حقن SQL
    clean_text = re.sub(r'(--)|(/\*|\*/)|(\b(select|insert|update|delete|drop|alter|create|truncate)\b)', 
                       lambda match: '', clean_text, flags=re.IGNORECASE)
    
    return clean_text

def validate_jwt(token: str) -> tuple:
    """
    التحقق من صحة رمز JWT
    """
    try:
        # التحقق من توكن JWT
        verify_jwt_in_request(token)
        current_user_id = get_jwt_identity()
        
        # التحقق من وجود المستخدم
        user = User.query.get(current_user_id)
        
        if not user:
            return (False, None, "المستخدم غير موجود")
        
        if not user.is_active:
            return (False, None, "حساب المستخدم غير نشط")
        
        return (True, user, "تم التحقق بنجاح")
    
    except Exception as e:
        return (False, None, str(e))

def token_required(allowed_roles: list = None):
    """
    مزخرف للتحقق من وجود رمز JWT صحيح ومن الأدوار المسموح بها
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # التحقق من وجود توكن
            try:
                verify_jwt_in_request()
                current_user_id = get_jwt_identity()
                
                # التحقق من وجود المستخدم
                user = User.query.get(current_user_id)
                
                if not user:
                    return jsonify(error="مستخدم غير موجود", message="المستخدم غير موجود"), 404
                
                if not user.is_active:
                    return jsonify(error="حساب غير نشط", message="حسابك غير نشط حالياً، يرجى التواصل مع الإدارة"), 403
                
                # التحقق من الأدوار إذا تم تحديدها
                if allowed_roles and user.role not in allowed_roles:
                    return jsonify(error="صلاحيات غير كافية", message="ليس لديك صلاحية للوصول إلى هذا المورد"), 403
                
                # تمرير المستخدم إلى الدالة
                return f(user, *args, **kwargs)
            
            except Exception as e:
                return jsonify(error="خطأ في المصادقة", message=str(e)), 401
        
        return decorated_function
    return decorator
