"""
وحدة أدوات عنوان IP لتعزيز الأمان في نظام تقييم BTEC
"""

from flask import request
import ipaddress
import logging

def get_client_ip():
    """
    الحصول على عنوان IP الخاص بالعميل من الطلب الحالي.
    يحاول استخراج العنوان من رؤوس X-Forwarded-For أو من عنوان العميل المباشر.
    
    Returns:
        str: عنوان IP للعميل
    """
    # محاولة الحصول على عنوان IP من رأس X-Forwarded-For
    x_forwarded_for = request.headers.get('X-Forwarded-For')
    if x_forwarded_for:
        # العنوان الأول هو عنوان العميل الأصلي
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        # استخدام عنوان العميل المباشر
        ip = request.remote_addr
    
    return ip

def is_valid_ip(ip_str):
    """
    التحقق مما إذا كان سلسلة العنوان تمثل عنوان IP صالح
    
    Args:
        ip_str (str): سلسلة تمثل عنوان IP للتحقق منها
        
    Returns:
        bool: True إذا كان العنوان صالحًا، False خلاف ذلك
    """
    try:
        ipaddress.ip_address(ip_str)
        return True
    except ValueError:
        return False

def is_private_ip(ip_str):
    """
    التحقق مما إذا كان عنوان IP مخصصًا للشبكات الخاصة
    
    Args:
        ip_str (str): سلسلة تمثل عنوان IP للتحقق منها
        
    Returns:
        bool: True إذا كان العنوان خاصًا، False خلاف ذلك
    """
    try:
        ip = ipaddress.ip_address(ip_str)
        return ip.is_private
    except ValueError:
        logging.warning(f"عنوان IP غير صالح: {ip_str}")
        return False

def is_loopback_ip(ip_str):
    """
    التحقق مما إذا كان عنوان IP هو عنوان loopback
    
    Args:
        ip_str (str): سلسلة تمثل عنوان IP للتحقق منها
        
    Returns:
        bool: True إذا كان العنوان loopback، False خلاف ذلك
    """
    try:
        ip = ipaddress.ip_address(ip_str)
        return ip.is_loopback
    except ValueError:
        logging.warning(f"عنوان IP غير صالح: {ip_str}")
        return False

def log_request_info():
    """
    تسجيل معلومات الطلب الحالي للأغراض الأمنية
    """
    ip = get_client_ip()
    user_agent = request.headers.get('User-Agent', 'Unknown')
    method = request.method
    path = request.path
    
    logging.info(f"Request: {method} {path} | IP: {ip} | User-Agent: {user_agent}")
    
    if is_private_ip(ip) and not is_loopback_ip(ip):
        logging.warning(f"طلب من عنوان IP خاص: {ip}")
    
    return {
        'ip': ip,
        'user_agent': user_agent,
        'method': method,
        'path': path
    }