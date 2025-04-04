"""
وحدة الأمان لنظام تقييم BTEC
"""
import os
import base64
import re
import logging
import html

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from flask import request, current_app
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity, get_jwt

class SecureVault:
    """
    صندوق آمن لتشفير وفك تشفير البيانات الحساسة
    """
    def __init__(self):
        self.key = self._get_or_create_key()
        self.cipher_suite = Fernet(self.key)
    
    def encrypt(self, text: str) -> str:
        """
        تشفير نص
        """
        if not text:
            return ""
        
        # تشفير النص
        encrypted_text = self.cipher_suite.encrypt(text.encode('utf-8'))
        
        # تحويل النص المشفر إلى سلسلة Base64
        return base64.urlsafe_b64encode(encrypted_text).decode('utf-8')
    
    def decrypt(self, encrypted_text: str) -> str:
        """
        فك تشفير نص مشفر
        """
        if not encrypted_text:
            return ""
        
        try:
            # تحويل النص المشفر من Base64
            decoded_text = base64.urlsafe_b64decode(encrypted_text)
            
            # فك تشفير النص
            decrypted_text = self.cipher_suite.decrypt(decoded_text)
            
            return decrypted_text.decode('utf-8')
        except Exception as e:
            logging.error(f"خطأ في فك تشفير النص: {str(e)}")
            return ""
    
    def _get_or_create_key(self):
        """
        الحصول على مفتاح التشفير أو إنشاء واحد جديد
        """
        encryption_key = os.environ.get('ENCRYPTION_KEY')
        
        if not encryption_key:
            # إنشاء مفتاح جديد
            logging.warning("لم يتم العثور على ENCRYPTION_KEY. إنشاء مفتاح جديد...")
            key = Fernet.generate_key()
            logging.info(f"تم إنشاء مفتاح تشفير جديد: {key.decode()}")
            return key
        
        # استخدام مفتاح البيئة
        if len(encryption_key) < 32:
            # مفتاح قصير جدًا، إنشاء مفتاح أقوى باستخدام PBKDF2
            salt = b'btec-eval-system-salt'  # يجب أن يكون ثابتًا للحصول على نفس المفتاح
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=100000
            )
            key = base64.urlsafe_b64encode(kdf.derive(encryption_key.encode()))
            return key
        
        # التأكد من أن المفتاح مشفر بشكل صحيح بـ Base64
        try:
            padding = '=' * (4 - len(encryption_key) % 4)
            padded_key = encryption_key + padding
            decoded_key = base64.urlsafe_b64decode(padded_key)
            encoded_key = base64.urlsafe_b64encode(decoded_key)
            return encoded_key
        except Exception as e:
            logging.error(f"خطأ في تهيئة مفتاح التشفير: {str(e)}")
            # استخدام مفتاح افتراضي (غير آمن للإنتاج)
            return Fernet.generate_key()

def sanitize_input(text: str) -> str:
    """
    تنقية المدخلات النصية من المحتويات الضارة
    """
    if not text:
        return ""
    
    # تنقية HTML والأكواد الضارة
    sanitized = html.escape(text)
    
    # إزالة أكواد JavaScript
    sanitized = re.sub(r'<script.*?>.*?</script>', '', sanitized, flags=re.DOTALL)
    
    # إزالة أكواد CSS ضارة
    sanitized = re.sub(r'<style.*?>.*?</style>', '', sanitized, flags=re.DOTALL)
    
    # إزالة تعليقات HTML
    sanitized = re.sub(r'<!--.*?-->', '', sanitized, flags=re.DOTALL)
    
    return sanitized

from functools import wraps
from flask_jwt_extended import verify_jwt_in_request, get_jwt

def token_required(allowed_roles: list = None):
    """
    مزخرف للتحقق من وجود رمز JWT صحيح ومن الأدوار المسموح بها
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # التحقق من وجود رمز JWT صالح
            try:
                verify_jwt_in_request()
            except Exception as e:
                logging.warning(f"فشل التحقق من الرمز: {str(e)}")
                return {
                    'status': 'error',
                    'message': 'رمز مصادقة غير صالح أو منتهي الصلاحية'
                }, 401
            
            # التحقق من الأدوار إذا تم تحديدها
            if allowed_roles:
                claims = get_jwt()
                user_role = claims.get('role', '')
                
                if user_role not in allowed_roles:
                    logging.warning(f"محاولة وصول غير مصرح بها: {user_role} ليس من الأدوار المسموح بها {allowed_roles}")
                    return {
                        'status': 'error',
                        'message': 'غير مصرح لك بالوصول إلى هذا المورد'
                    }, 403
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def configure_security_headers():
    """
    تكوين رؤوس الأمان للاستجابة
    """
    # قائمة رؤوس الأمان المراد تطبيقها
    security_headers = {
        'Content-Security-Policy': "default-src 'self'; script-src 'self' 'unsafe-inline' cdn.jsdelivr.net cdnjs.cloudflare.com; style-src 'self' 'unsafe-inline' cdn.jsdelivr.net cdnjs.cloudflare.com fonts.googleapis.com; img-src 'self' data: blob:; font-src 'self' fonts.gstatic.com fonts.googleapis.com cdnjs.cloudflare.com; connect-src 'self' api.openai.com;",
        'X-Content-Type-Options': 'nosniff',
        'X-Frame-Options': 'SAMEORIGIN',
        'X-XSS-Protection': '1; mode=block',
        'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
        'Referrer-Policy': 'strict-origin-when-cross-origin'
    }
    
    return security_headers
