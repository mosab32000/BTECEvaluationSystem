"""
حزمة الأمان لنظام تقييم BTEC
توفر أدوات للتشفير، إدارة التوكن، تحديد معدل الطلبات والمصادقة المتقدمة
"""

from .encryption import Vault
from .token_utils import generate_token, verify_token, token_required
from .ip_utils import get_client_ip, is_valid_ip, is_private_ip, log_request_info
from .rate_limiter import rate_limit, general_limiter, auth_limiter, api_limiter
from .auth_utils import (
    validate_password_strength,
    generate_totp_secret,
    generate_totp,
    verify_totp,
    role_required,
    admin_required,
    teacher_required,
    user_required,
    ROLE_USER,
    ROLE_TEACHER,
    ROLE_ADMIN
)

__all__ = [
    'Vault',
    'generate_token',
    'verify_token',
    'token_required',
    'get_client_ip',
    'is_valid_ip',
    'is_private_ip',
    'log_request_info',
    'rate_limit',
    'general_limiter',
    'auth_limiter',
    'api_limiter',
    'validate_password_strength',
    'generate_totp_secret',
    'generate_totp',
    'verify_totp',
    'role_required',
    'admin_required',
    'teacher_required',
    'user_required',
    'ROLE_USER',
    'ROLE_TEACHER',
    'ROLE_ADMIN'
]