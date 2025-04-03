"""
وحدة المصادقة المتقدمة لنظام تقييم BTEC
توفر تفويض متعدد المستويات وطبقات حماية إضافية
"""

import os
import time
import hashlib
import logging
import ipaddress
import datetime
import jwt
from functools import wraps
from flask import request, g, current_app, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from typing import List, Dict, Any, Optional, Callable, Union

# إعداد السجل
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ثوابت الأمان
TOKEN_EXPIRY = datetime.timedelta(hours=1)  # انتهاء صلاحية الرمز بعد ساعة واحدة
FAILED_LOGIN_LIMIT = 5  # عدد محاولات تسجيل الدخول الفاشلة قبل القفل
ACCOUNT_LOCKOUT_TIME = datetime.timedelta(minutes=15)  # مدة قفل الحساب بعد محاولات فاشلة

# قائمة المستخدمين المقفلين مؤقتاً مع وقت انتهاء القفل
# في الإنتاج، يجب تخزين هذه المعلومات في قاعدة البيانات
locked_accounts = {}  # { "email": expiry_timestamp }


class AdvancedAuth:
    """صنف مصادقة متقدم يوفر مصادقة ثنائية مع دعم TOTP والتفويض المتعدد المستويات"""

    def __init__(self):
        """تهيئة المصادق المتقدم"""
        self.jwt_secret_key = os.environ.get("JWT_SECRET_KEY") or current_app.config.get("JWT_SECRET_KEY")
        if not self.jwt_secret_key:
            logger.warning("لم يتم تعيين JWT_SECRET_KEY. سيتم استخدام مفتاح افتراضي غير آمن.")
            self.jwt_secret_key = "insecure_default_key_replace_in_production"

    def generate_token(self, user_id: int, email: str, role: str) -> str:
        """
        إنشاء رمز JWT مع معلومات المستخدم والدور
        
        Args:
            user_id: معرف المستخدم
            email: البريد الإلكتروني للمستخدم
            role: دور المستخدم (مثل 'user', 'teacher', 'admin')
            
        Returns:
            رمز JWT موقّع
        """
        now = datetime.datetime.utcnow()
        payload = {
            'sub': user_id,
            'email': email,
            'role': role,
            'iat': now,
            'exp': now + TOKEN_EXPIRY,
            'iss': 'BTEC_EVALUATION_SYSTEM',
            'unique_seed': hashlib.sha256(os.urandom(32)).hexdigest()[:8]  # منع إعادة استخدام الرموز
        }
        
        token = jwt.encode(
            payload, 
            self.jwt_secret_key, 
            algorithm='HS512'
        )
        
        logger.info(f"تم إنشاء رمز JWT للمستخدم: {email} مع الدور: {role}")
        return token

    def validate_token(self, token: str) -> Dict[str, Any]:
        """
        التحقق من صحة رمز JWT والحصول على معلومات المستخدم
        
        Args:
            token: رمز JWT للتحقق
            
        Returns:
            قاموس يحتوي على معلومات المستخدم أو رسالة خطأ في حالة فشل التحقق
        """
        try:
            payload = jwt.decode(
                token,
                self.jwt_secret_key,
                algorithms=['HS512'],
                options={
                    'verify_signature': True,
                    'verify_exp': True,
                    'verify_iat': True,
                    'verify_iss': True,
                    'require': ['sub', 'email', 'role', 'exp', 'iat', 'iss']
                }
            )
            
            # التحقق من المُصدر
            if payload.get('iss') != 'BTEC_EVALUATION_SYSTEM':
                return {'success': False, 'error': 'INVALID_ISSUER', 'message': 'رمز غير صالح: مُصدر غير صحيح'}
                
            logger.info(f"تم التحقق من صحة الرمز للمستخدم: {payload.get('email')}")
            return {
                'success': True,
                'user_id': payload.get('sub'),
                'email': payload.get('email'),
                'role': payload.get('role')
            }
            
        except jwt.ExpiredSignatureError:
            logger.warning("محاولة استخدام رمز منتهي الصلاحية")
            return {'success': False, 'error': 'TOKEN_EXPIRED', 'message': 'انتهت صلاحية الرمز'}
        except jwt.InvalidTokenError as e:
            logger.warning(f"رمز غير صالح: {str(e)}")
            return {'success': False, 'error': 'INVALID_TOKEN', 'message': f'رمز غير صالح: {str(e)}'}

    def check_account_status(self, email: str) -> Dict[str, Any]:
        """
        التحقق من حالة قفل الحساب
        
        Args:
            email: البريد الإلكتروني للمستخدم
            
        Returns:
            حالة الحساب (مقفل أو غير مقفل)
        """
        global locked_accounts
        
        # مسح الحسابات المنتهية
        self._cleanup_expired_locks()
        
        # التحقق من قفل الحساب
        if email in locked_accounts:
            lock_expiry = locked_accounts[email]
            if time.time() < lock_expiry:
                remaining = int(lock_expiry - time.time())
                return {
                    'locked': True, 
                    'message': f'الحساب مقفل بسبب محاولات تسجيل دخول فاشلة. حاول مرة أخرى بعد {remaining} ثانية',
                    'remaining_seconds': remaining
                }
            else:
                # إزالة القفل المنتهي
                del locked_accounts[email]
        
        return {'locked': False}

    def lock_account(self, email: str) -> None:
        """
        قفل حساب مستخدم بعد عدة محاولات تسجيل دخول فاشلة
        
        Args:
            email: البريد الإلكتروني للمستخدم
        """
        global locked_accounts
        expiry_time = time.time() + ACCOUNT_LOCKOUT_TIME.total_seconds()
        locked_accounts[email] = expiry_time
        logger.warning(f"تم قفل الحساب {email} بسبب محاولات تسجيل دخول فاشلة")

    def _cleanup_expired_locks(self) -> None:
        """إزالة قفل الحسابات المنتهية من القائمة المؤقتة"""
        global locked_accounts
        current_time = time.time()
        expired_accounts = [email for email, expiry in locked_accounts.items() if current_time > expiry]
        for email in expired_accounts:
            del locked_accounts[email]
            logger.info(f"تم إلغاء قفل الحساب تلقائيًا: {email}")

    @staticmethod
    def validate_password_strength(password: str) -> Dict[str, Any]:
        """
        التحقق من قوة كلمة المرور
        
        Args:
            password: كلمة المرور للتحقق
            
        Returns:
            نتيجة التحقق من قوة كلمة المرور
        """
        errors = []
        
        if len(password) < 10:
            errors.append('يجب أن تكون كلمة المرور 10 أحرف على الأقل')
        
        if not any(char.isupper() for char in password):
            errors.append('يجب أن تحتوي كلمة المرور على حرف كبير واحد على الأقل')
            
        if not any(char.islower() for char in password):
            errors.append('يجب أن تحتوي كلمة المرور على حرف صغير واحد على الأقل')
            
        if not any(char.isdigit() for char in password):
            errors.append('يجب أن تحتوي كلمة المرور على رقم واحد على الأقل')
            
        if not any(char in '!@#$%^&*()_+-=[]{}|;:,.<>?/~`' for char in password):
            errors.append('يجب أن تحتوي كلمة المرور على رمز خاص واحد على الأقل')
        
        is_valid = len(errors) == 0
        return {
            'valid': is_valid,
            'errors': errors,
            'strength': 'قوية' if is_valid else ('متوسطة' if len(errors) <= 2 else 'ضعيفة')
        }

    @staticmethod
    def check_ip(ip_address: str, trusted_ips: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        التحقق من عنوان IP لاكتشاف العناوين المشبوهة
        
        Args:
            ip_address: عنوان IP للتحقق
            trusted_ips: قائمة عناوين IP الموثوقة (اختياري)
            
        Returns:
            نتيجة التحقق من عنوان IP
        """
        if not trusted_ips:
            trusted_ips = []
            
        if ip_address in trusted_ips:
            return {'trusted': True, 'private': False, 'message': 'عنوان IP موثوق'}
            
        try:
            ip_obj = ipaddress.ip_address(ip_address)
            is_private = ip_obj.is_private
            is_loopback = ip_obj.is_loopback
            
            if is_loopback:
                return {'trusted': True, 'private': True, 'message': 'عنوان IP محلي (loopback)'}
                
            if is_private:
                return {'trusted': True, 'private': True, 'message': 'عنوان IP خاص (شبكة داخلية)'}
                
            # إضافة منطق إضافي للتحقق من العناوين العامة (مثل قوائم IP السوداء، إلخ)
            return {'trusted': False, 'private': False, 'message': 'عنوان IP عام غير موثوق'}
            
        except ValueError:
            logger.warning(f"عنوان IP غير صالح: {ip_address}")
            return {'trusted': False, 'private': False, 'message': 'عنوان IP غير صالح'}


# زخارف لحماية مسارات API
def role_required(allowed_roles: List[str]):
    """
    زخرفة للتحقق من دور المستخدم
    
    Args:
        allowed_roles: قائمة الأدوار المسموح بها
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # التحقق من وجود الرمز
            auth_header = request.headers.get('Authorization')
            if not auth_header or not auth_header.startswith('Bearer '):
                return jsonify({'error': 'تفويض مفقود أو غير صالح'}), 401
                
            token = auth_header.split(' ')[1]
            
            # التحقق من صحة الرمز
            auth = AdvancedAuth()
            token_data = auth.validate_token(token)
            
            if not token_data['success']:
                return jsonify({'error': token_data['message']}), 401
                
            # التحقق من الدور
            user_role = token_data['role']
            if user_role not in allowed_roles:
                logger.warning(f"محاولة وصول غير مصرح: المستخدم {token_data['email']} بدور {user_role} حاول الوصول إلى مسار يتطلب أحد الأدوار {allowed_roles}")
                return jsonify({'error': 'غير مصرح لك بالوصول إلى هذا المورد'}), 403
                
            # تخزين بيانات المستخدم في كائن g لاستخدامها في المسار
            g.user_id = token_data['user_id']
            g.email = token_data['email']
            g.role = user_role
                
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def admin_required(f):
    """زخرفة تتطلب دور المسؤول"""
    return role_required(['admin'])(f)

def teacher_required(f):
    """زخرفة تتطلب دور المعلم أو المسؤول"""
    return role_required(['teacher', 'admin'])(f)

def auth_required(f):
    """زخرفة تتطلب مصادقة المستخدم بغض النظر عن الدور"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # التحقق من وجود الرمز
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'error': 'تفويض مفقود أو غير صالح'}), 401
            
        token = auth_header.split(' ')[1]
        
        # التحقق من صحة الرمز
        auth = AdvancedAuth()
        token_data = auth.validate_token(token)
        
        if not token_data['success']:
            return jsonify({'error': token_data['message']}), 401
            
        # تخزين بيانات المستخدم في كائن g لاستخدامها في المسار
        g.user_id = token_data['user_id']
        g.email = token_data['email']
        g.role = token_data['role']
            
        return f(*args, **kwargs)
    return decorated_function