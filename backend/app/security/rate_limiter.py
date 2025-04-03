"""
وحدة للتحكم في معدل الطلبات ومنع الهجمات في نظام تقييم BTEC
"""

import time
import logging
from collections import defaultdict
from flask import request, jsonify
from functools import wraps
from .ip_utils import get_client_ip
import threading

class RateLimiter:
    """
    فئة للتحكم في معدل الطلبات لمنع هجمات الخدمة المُوزَّعة (DDOS)
    وهجمات القوة الغاشمة (Brute Force)
    """
    
    def __init__(self, max_requests=100, period=60, block_time=300):
        """
        تهيئة محدد معدل الطلبات
        
        Args:
            max_requests (int): الحد الأقصى لعدد الطلبات المسموح بها خلال الفترة
            period (int): طول الفترة بالثواني
            block_time (int): مدة حظر العنوان بعد تجاوز الحد بالثواني
        """
        self.max_requests = max_requests
        self.period = period
        self.block_time = block_time
        self.request_counts = defaultdict(list)
        self.blocked_ips = {}
        
        # قفل لضمان تزامن الوصول للبيانات في بيئة متعددة المؤشرات
        self.lock = threading.RLock()
        
        # بدء مؤقت لتنظيف البيانات القديمة
        self.start_cleanup_timer()
    
    def is_rate_limited(self, ip=None):
        """
        التحقق مما إذا كان الطلب تجاوز الحد المسموح به
        
        Args:
            ip (str, optional): عنوان IP للتحقق منه. إذا لم يتم تحديده، سيتم استخدام عنوان طلب العميل الحالي
        
        Returns:
            bool: True إذا تم تجاوز الحد، False خلاف ذلك
        """
        if ip is None:
            ip = get_client_ip()
        
        with self.lock:
            # التحقق إذا كان العنوان محظورًا
            if ip in self.blocked_ips:
                block_time = self.blocked_ips[ip]
                if time.time() < block_time:
                    logging.warning(f"Blocked request from rate-limited IP: {ip}")
                    return True
                else:
                    # إزالة الحظر بعد انتهاء المدة
                    del self.blocked_ips[ip]
            
            # تنظيف الطلبات القديمة للعنوان
            current_time = time.time()
            self.request_counts[ip] = [req_time for req_time in self.request_counts[ip]
                                      if current_time - req_time < self.period]
            
            # إضافة الوقت الحالي إلى قائمة الطلبات
            self.request_counts[ip].append(current_time)
            
            # التحقق من تجاوز الحد
            if len(self.request_counts[ip]) > self.max_requests:
                self.blocked_ips[ip] = current_time + self.block_time
                logging.warning(f"Rate limit exceeded. Blocking IP: {ip} for {self.block_time} seconds")
                return True
            
            return False
    
    def start_cleanup_timer(self):
        """
        بدء مؤقت لتنظيف البيانات القديمة دوريًا
        """
        def cleanup():
            while True:
                time.sleep(300)  # تنظيف كل 5 دقائق
                self.cleanup_old_data()
        
        cleanup_thread = threading.Thread(target=cleanup, daemon=True)
        cleanup_thread.start()
    
    def cleanup_old_data(self):
        """
        تنظيف بيانات الطلبات القديمة والعناوين المحظورة المنتهية
        """
        with self.lock:
            current_time = time.time()
            
            # تنظيف الطلبات القديمة
            for ip in list(self.request_counts.keys()):
                self.request_counts[ip] = [req_time for req_time in self.request_counts[ip]
                                          if current_time - req_time < self.period]
                
                # إزالة المدخلات الفارغة
                if not self.request_counts[ip]:
                    del self.request_counts[ip]
            
            # تنظيف العناوين المحظورة المنتهية
            for ip in list(self.blocked_ips.keys()):
                if current_time > self.blocked_ips[ip]:
                    del self.blocked_ips[ip]
            
            logging.debug(f"تم تنظيف البيانات. {len(self.request_counts)} عناوين نشطة، {len(self.blocked_ips)} عناوين محظورة")

# إنشاء محددات معدل الطلبات المختلفة
general_limiter = RateLimiter(max_requests=200, period=60, block_time=300)  # 200 طلب/دقيقة
auth_limiter = RateLimiter(max_requests=10, period=60, block_time=600)  # 10 طلبات/دقيقة لعمليات المصادقة
api_limiter = RateLimiter(max_requests=50, period=60, block_time=300)  # 50 طلب/دقيقة لطلبات API

def rate_limit(limiter=general_limiter):
    """
    زخرفة لتطبيق تحديد معدل الطلبات على مسار
    
    Args:
        limiter (RateLimiter): محدد معدل الطلبات المراد استخدامه
    
    Returns:
        function: الزخرفة
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if limiter.is_rate_limited():
                response = {
                    'status': 'error',
                    'message': 'تم تجاوز الحد المسموح به من الطلبات',
                    'details': 'يرجى المحاولة مرة أخرى بعد فترة'
                }
                return jsonify(response), 429  # Too Many Requests
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator