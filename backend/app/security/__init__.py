"""
حزمة الأمان لنظام تقييم BTEC
توفر أدوات للتشفير، إدارة التوكن، تحديد معدل الطلبات والمصادقة المتقدمة
"""

from .auth_utils import (
    generate_token,
    validate_token,
    hash_password,
    verify_password,
    token_required,
    admin_required,
    teacher_required,
    get_user_id_from_request
)
from .encryption import Vault, encrypt_task, decrypt_task
from .advanced_auth import (
    AdvancedAuth,
    role_required,
    admin_required as advanced_admin_required,
    teacher_required as advanced_teacher_required,
    auth_required
)

__all__ = [
    'generate_token',
    'validate_token',
    'hash_password',
    'verify_password',
    'token_required',
    'admin_required',
    'teacher_required',
    'get_user_id_from_request',
    'Vault',
    'encrypt_task',
    'decrypt_task',
    'AdvancedAuth',
    'role_required',
    'advanced_admin_required',
    'advanced_teacher_required',
    'auth_required'
]