"""
وحدة أدوات المصادقة المتقدمة لنظام تقييم BTEC
"""

import hashlib
import os
import base64
import time
import hmac
import logging
import re
from datetime import datetime, timedelta
from flask import request, jsonify
from functools import wraps
from .token_utils import verify_token
from .ip_utils import get_client_ip, log_request_info

# ثوابت دليلية للصلاحيات
ROLE_USER = 'user'
ROLE_TEACHER = 'teacher'
ROLE_ADMIN = 'admin'

# قائمة بأنماط كلمات المرور الضعيفة للتحقق
WEAK_PASSWORD_PATTERNS = [
    r'^123456',
    r'^password',
    r'^qwerty',
    r'^\d{6}$',  # 6 أرقام فقط
    r'^admin',
    r'^btec',
    r'^letmein',
]

def validate_password_strength(password):
    """
    التحقق من قوة كلمة المرور
    
    Args:
        password (str): كلمة المرور للتحقق
        
    Returns:
        tuple: (قوة كلمة المرور (bool)، قائمة بالأخطاء)
    """
    errors = []
    
    # التحقق من الطول
    if len(password) < 8:
        errors.append("كلمة المرور يجب أن تكون 8 أحرف على الأقل")
    
    # التحقق من وجود أحرف مختلفة
    if not re.search(r'[A-Z]', password):
        errors.append("كلمة المرور يجب أن تحتوي على حرف كبير واحد على الأقل")
    
    if not re.search(r'[a-z]', password):
        errors.append("كلمة المرور يجب أن تحتوي على حرف صغير واحد على الأقل")
    
    if not re.search(r'\d', password):
        errors.append("كلمة المرور يجب أن تحتوي على رقم واحد على الأقل")
    
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        errors.append("كلمة المرور يجب أن تحتوي على رمز خاص واحد على الأقل")
    
    # التحقق من أنماط كلمات المرور الضعيفة
    for pattern in WEAK_PASSWORD_PATTERNS:
        if re.search(pattern, password, re.IGNORECASE):
            errors.append("كلمة المرور ضعيفة جدًا أو شائعة")
            break
    
    # التحقق من التكرار
    if any(password.count(char) > 3 for char in password):
        errors.append("كلمة المرور تحتوي على أحرف متكررة كثيرة")
    
    return len(errors) == 0, errors

def generate_totp_secret():
    """
    إنشاء مفتاح سري للتوثيق الثنائي TOTP
    
    Returns:
        str: المفتاح السري بتشفير Base32
    """
    # إنشاء 20 بايت عشوائية (160 بت) للمفتاح السري
    random_bytes = os.urandom(20)
    return base64.b32encode(random_bytes).decode('utf-8')

def generate_totp(secret, time_step=30, digits=6):
    """
    إنشاء رمز TOTP للمفتاح السري المحدد
    
    Args:
        secret (str): المفتاح السري بتشفير Base32
        time_step (int): خطوة الوقت بالثواني
        digits (int): عدد أرقام الرمز
        
    Returns:
        str: رمز TOTP
    """
    # تحويل المفتاح السري من Base32 إلى بايت
    key = base64.b32decode(secret)
    
    # حساب قيمة العداد الحالية (عدد خطوات الوقت منذ UNIX epoch)
    counter = int(time.time() / time_step)
    
    # تحويل العداد إلى بايت بالترتيب Big-endian
    counter_bytes = counter.to_bytes(8, byteorder='big')
    
    # حساب HMAC-SHA1
    hmac_result = hmac.new(key, counter_bytes, hashlib.sha1).digest()
    
    # استخراج قيمة الإزاحة
    offset = hmac_result[-1] & 0x0F
    
    # استخراج 4 بايت من النتيجة بدءًا من الإزاحة وإزالة البت الأكثر أهمية
    binary = ((hmac_result[offset] & 0x7F) << 24 |
              (hmac_result[offset + 1] & 0xFF) << 16 |
              (hmac_result[offset + 2] & 0xFF) << 8 |
              (hmac_result[offset + 3] & 0xFF))
    
    # حساب القيمة النهائية بأخذ مُعامل باقي القسمة
    totp = binary % (10 ** digits)
    
    # تحويل إلى سلسلة نصية وإضافة أصفار في البداية إذا لزم الأمر
    return str(totp).zfill(digits)

def verify_totp(secret, token, time_step=30, digits=6, window=1):
    """
    التحقق من صحة رمز TOTP
    
    Args:
        secret (str): المفتاح السري بتشفير Base32
        token (str): الرمز المراد التحقق منه
        time_step (int): خطوة الوقت بالثواني
        digits (int): عدد أرقام الرمز
        window (int): نافذة التحقق (عدد الخطوات قبل وبعد الوقت الحالي)
        
    Returns:
        bool: True إذا كان الرمز صحيحًا، False خلاف ذلك
    """
    # التحقق من شكل الرمز
    if not re.match(r'^\d{%d}$' % digits, token):
        return False
    
    # التحقق من الرمز في نافذة الوقت المحددة
    for i in range(-window, window + 1):
        # حساب قيمة العداد للنافذة
        counter = int(time.time() / time_step) + i
        
        # تحويل العداد إلى بايت بالترتيب Big-endian
        counter_bytes = counter.to_bytes(8, byteorder='big')
        
        # تحويل المفتاح السري من Base32 إلى بايت
        key = base64.b32decode(secret)
        
        # حساب HMAC-SHA1
        hmac_result = hmac.new(key, counter_bytes, hashlib.sha1).digest()
        
        # استخراج قيمة الإزاحة
        offset = hmac_result[-1] & 0x0F
        
        # استخراج 4 بايت من النتيجة بدءًا من الإزاحة وإزالة البت الأكثر أهمية
        binary = ((hmac_result[offset] & 0x7F) << 24 |
                  (hmac_result[offset + 1] & 0xFF) << 16 |
                  (hmac_result[offset + 2] & 0xFF) << 8 |
                  (hmac_result[offset + 3] & 0xFF))
        
        # حساب القيمة النهائية بأخذ مُعامل باقي القسمة
        generated_token = str(binary % (10 ** digits)).zfill(digits)
        
        # مقارنة الرمز المُدخل مع الرمز المُولد
        if token == generated_token:
            return True
    
    return False

def role_required(allowed_roles):
    """
    زخرفة للتحقق من صلاحيات المستخدم
    
    Args:
        allowed_roles (list): قائمة بالصلاحيات المسموح بها
        
    Returns:
        function: الزخرفة
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            from backend.app.models import User
            
            token = None
            auth_header = request.headers.get('Authorization')
            
            # استخراج التوكن من رأس التفويض
            if auth_header:
                if auth_header.startswith('Bearer '):
                    token = auth_header.split(' ')[1]
                else:
                    return jsonify({
                        'status': 'error',
                        'message': 'صيغة رأس التفويض غير صحيحة'
                    }), 401
            
            # التحقق من وجود التوكن
            if not token:
                return jsonify({
                    'status': 'error',
                    'message': 'لم يتم توفير رمز المصادقة'
                }), 401
            
            # التحقق من صحة التوكن واستخراج معرّف المستخدم
            user_id = verify_token(token)
            if not user_id:
                return jsonify({
                    'status': 'error',
                    'message': 'رمز مصادقة غير صالح أو منتهي الصلاحية'
                }), 401
            
            # استعلام عن المستخدم في قاعدة البيانات
            from flask import current_app
            with current_app.app_context():
                user = User.query.get(user_id)
                
                # التحقق من وجود المستخدم وحالته النشطة
                if not user or not user.is_active:
                    return jsonify({
                        'status': 'error',
                        'message': 'حساب المستخدم غير موجود أو غير نشط'
                    }), 401
                
                # التحقق من صلاحيات المستخدم
                if user.role not in allowed_roles:
                    log_request_info()
                    logging.warning(f"محاولة وصول غير مصرح بها: المستخدم {user.id} (صلاحية: {user.role}) محدولة الوصول إلى مسار مقيد")
                    return jsonify({
                        'status': 'error',
                        'message': 'لا تملك الصلاحيات اللازمة للوصول إلى هذا المورد'
                    }), 403
                
                # تحديث وقت آخر تسجيل دخول
                user.update_last_login()
                
                # استدعاء الدالة الأصلية مع تمرير المستخدم
                return f(user, *args, **kwargs)
        
        return decorated_function
    return decorator

# زخرفات للصلاحيات المشتركة
def admin_required(f):
    """زخرفة تتطلب صلاحيات المسؤول"""
    return role_required([ROLE_ADMIN])(f)

def teacher_required(f):
    """زخرفة تتطلب صلاحيات المعلم أو المسؤول"""
    return role_required([ROLE_TEACHER, ROLE_ADMIN])(f)

def user_required(f):
    """زخرفة تتطلب أي صلاحيات نشطة"""
    return role_required([ROLE_USER, ROLE_TEACHER, ROLE_ADMIN])(f)