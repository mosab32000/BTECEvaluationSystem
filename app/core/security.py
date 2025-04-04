"""
وحدة الأمان وتشفير البيانات والمصادقة
"""
import base64
import datetime
import hashlib
import json
import logging
import os
import re
import secrets
from typing import Dict, List, Optional, Tuple, Union

from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from flask import current_app, g, request
from flask_jwt_extended import get_jwt, verify_jwt_in_request
from functools import wraps

logger = logging.getLogger(__name__)

class SecureVault:
    """
    فئة لتشفير وفك تشفير البيانات باستخدام Fernet
    """
    def __init__(self, key_str: str = None):
        """
        تهيئة فئة التشفير
        
        Args:
            key_str: مفتاح التشفير (اختياري، يمكن استخدام المتغير البيئي)
        """
        self.key = None
        self.cipher_suite = None
        
        # استخدام المفتاح المقدم أو البحث عن متغير بيئي
        key_str = key_str or os.environ.get("DATA_ENCRYPTION_KEY")
        if not key_str:
            logger.warning("No encryption key provided, generating a new one. THIS SHOULD NOT HAPPEN IN PRODUCTION.")
            key = Fernet.generate_key()
            key_str = key.decode('utf-8')
            logger.warning(f"New encryption key generated. Set this in your environment: DATA_ENCRYPTION_KEY={key_str}")
        
        try:
            self.key = key_str.encode('utf-8')
            self.cipher_suite = Fernet(self.key)
            logger.info("Encryption key loaded and validated.")
        except (ValueError, TypeError) as e:
            logger.critical(f"Invalid encryption key format: {e}")
            raise ValueError("Invalid encryption key format")
    
    def encrypt(self, text: str) -> str:
        """
        تشفير نص
        
        Args:
            text: النص المراد تشفيره
            
        Returns:
            str: النص المشفر
        """
        try:
            if not text:
                return ""
            if not isinstance(text, str):
                text = str(text)
            
            encrypted_text = self.cipher_suite.encrypt(text.encode('utf-8'))
            return encrypted_text.decode('utf-8')
        except Exception as e:
            logger.error(f"Encryption error: {e}")
            raise
    
    def decrypt(self, encrypted_text: str) -> str:
        """
        فك تشفير نص
        
        Args:
            encrypted_text: النص المشفر
            
        Returns:
            str: النص الأصلي
        """
        try:
            if not encrypted_text:
                return ""
            
            decrypted_text = self.cipher_suite.decrypt(encrypted_text.encode('utf-8'))
            return decrypted_text.decode('utf-8')
        except InvalidToken:
            logger.error("Invalid token for decryption (key mismatch or corrupted data)")
            raise
        except Exception as e:
            logger.error(f"Decryption error: {e}")
            raise


# دالة لمساعدة اشتقاق مفتاح من نص
def _derive_key_from_string(key_str: str, salt: bytes = None) -> bytes:
    """
    اشتقاق مفتاح تشفير من سلسلة نصية
    
    Args:
        key_str: النص المستخدم لاشتقاق المفتاح
        salt: ملح إضافي (اختياري)
        
    Returns:
        bytes: مفتاح التشفير المشتق
    """
    if not salt:
        # استخدام قيمة ثابتة للملح لإنتاج نفس المفتاح للنص نفسه
        salt = b'BTEC_EVALUATION_SYSTEM_SALT'
    
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,  # طول المفتاح المطلوب لـ Fernet
        salt=salt,
        iterations=100000,
    )
    
    key = base64.urlsafe_b64encode(kdf.derive(key_str.encode('utf-8')))
    return key


# تنظيف المدخلات
def sanitize_input(text: str) -> str:
    """
    تنظيف المدخلات من الرموز الخاصة التي قد تسبب ثغرات XSS
    
    Args:
        text: النص المراد تنظيفه
        
    Returns:
        str: النص المنظف
    """
    if not text:
        return ""
    
    # استبدال العلامات HTML
    text = text.replace('&', '&amp;')
    text = text.replace('<', '&lt;')
    text = text.replace('>', '&gt;')
    text = text.replace('"', '&quot;')
    text = text.replace("'", '&#39;')
    
    # إزالة أي رموز JavaScript محتملة
    text = re.sub(r'javascript:', '', text, flags=re.IGNORECASE)
    text = re.sub(r'on\w+\s*=', '', text, flags=re.IGNORECASE)
    
    return text


# مزخرف للتحقق من الرموز المميزة والأدوار
def token_required(allowed_roles: List[str] = None):
    """
    مزخرف للتحقق من صلاحية رمز JWT والأدوار المسموح بها
    
    Args:
        allowed_roles: قائمة الأدوار المسموح بها
        
    Returns:
        function: دالة مزخرفة
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            try:
                # التحقق من وجود رمز JWT صالح
                verify_jwt_in_request()
                
                # الحصول على معلومات الرمز
                claims = get_jwt()
                
                # التحقق من الأدوار إذا تم تحديدها
                if allowed_roles:
                    user_role = claims.get('role', '')
                    if user_role not in allowed_roles:
                        return {
                            'status': 'error',
                            'message': 'غير مصرح لك بالوصول إلى هذا المورد'
                        }, 403
                
                # إضافة معلومات المستخدم إلى g للاستخدام في الدوال الأخرى
                g.user_id = claims.get('sub')
                g.user_email = claims.get('email')
                g.user_role = claims.get('role')
                
                return f(*args, **kwargs)
            except Exception as e:
                logger.error(f"Token validation error: {e}")
                return {
                    'status': 'error',
                    'message': 'مشكلة في المصادقة'
                }, 401
        return decorated_function
    return decorator


# إنشاء كلمة مرور قوية عشوائيًا
def generate_secure_password(length: int = 12) -> str:
    """
    إنشاء كلمة مرور قوية عشوائيًا
    
    Args:
        length: طول كلمة المرور
        
    Returns:
        str: كلمة المرور العشوائية
    """
    if length < 8:
        length = 8  # الحد الأدنى لطول كلمة المرور
    
    # أحرف متنوعة لكلمة مرور قوية
    chars = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*()_-+=?'
    
    # التأكد من أن كلمة المرور تحتوي على الأقل على حرف صغير وحرف كبير ورقم ورمز خاص
    password = []
    password.append(secrets.choice('abcdefghijklmnopqrstuvwxyz'))
    password.append(secrets.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ'))
    password.append(secrets.choice('0123456789'))
    password.append(secrets.choice('!@#$%^&*()_-+=?'))
    
    # إضافة باقي الأحرف العشوائية
    for i in range(length - 4):
        password.append(secrets.choice(chars))
    
    # خلط الأحرف
    secrets.SystemRandom().shuffle(password)
    
    return ''.join(password)