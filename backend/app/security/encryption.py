"""
وحدة التشفير لنظام تقييم BTEC
توفر أدوات للتشفير وفك التشفير باستخدام مفتاح آمن
"""

import os
import base64
import logging
from typing import Any, Optional, Union, Dict
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from flask import current_app

# إعداد السجل
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Vault:
    """صنف للتشفير وفك التشفير باستخدام مفتاح آمن"""

    def __init__(self, encryption_key: Optional[str] = None):
        """
        تهيئة الخزنة مع المفتاح المقدم أو من المتغيرات البيئية
        
        Args:
            encryption_key: مفتاح التشفير (اختياري، سيتم استخدام المتغير البيئي إذا لم يتم توفيره)
        """
        if encryption_key:
            self.key = self._prepare_key(encryption_key)
        else:
            # البحث عن مفتاح التشفير في المتغيرات البيئية أو إعدادات التطبيق
            env_key = os.environ.get('ENCRYPTION_KEY') or current_app.config.get('ENCRYPTION_KEY')
            if env_key:
                self.key = self._prepare_key(env_key)
            else:
                logger.warning("تحذير: لم يتم توفير مفتاح التشفير. سيتم إنشاء مفتاح مؤقت غير آمن.")
                self.key = Fernet.generate_key()
        
        self.cipher_suite = Fernet(self.key)
    
    def _prepare_key(self, key_str: str) -> bytes:
        """
        تحضير المفتاح للاستخدام مع Fernet
        
        Args:
            key_str: المفتاح كسلسلة نصية
            
        Returns:
            المفتاح بتنسيق مناسب
        """
        # التحقق مما إذا كان المفتاح مشفرًا بـ base64 بالفعل وبالطول المناسب
        try:
            decoded = base64.urlsafe_b64decode(key_str)
            if len(decoded) == 32:  # مفتاح Fernet القياسي
                return key_str.encode() if isinstance(key_str, str) else key_str
        except Exception:
            pass
        
        # إنشاء مفتاح فرنيت من كلمة سر
        salt = b'btec_evaluation_system'  # ملح ثابت للتوافق عبر عمليات إعادة التشغيل
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000
        )
        key_material = kdf.derive(key_str.encode())
        key = base64.urlsafe_b64encode(key_material)
        return key
    
    def encrypt(self, data: Union[str, dict, bytes]) -> str:
        """
        تشفير البيانات
        
        Args:
            data: البيانات للتشفير (نص، قاموس، أو بيانات ثنائية)
            
        Returns:
            البيانات المشفرة كسلسلة نصية
        """
        try:
            # تحويل البيانات إلى تنسيق مناسب
            if isinstance(data, dict):
                import json
                data = json.dumps(data)
            
            if isinstance(data, str):
                data = data.encode('utf-8')
            
            # التشفير
            encrypted_data = self.cipher_suite.encrypt(data)
            return encrypted_data.decode('utf-8')
        except Exception as e:
            logger.error(f"خطأ في تشفير البيانات: {e}")
            raise
    
    def decrypt(self, encrypted_data: str) -> bytes:
        """
        فك تشفير البيانات
        
        Args:
            encrypted_data: البيانات المشفرة
            
        Returns:
            البيانات المفكوكة التشفير
        """
        try:
            # تحويل البيانات المشفرة إلى بايت إذا كانت سلسلة نصية
            if isinstance(encrypted_data, str):
                encrypted_data = encrypted_data.encode('utf-8')
            
            # فك التشفير
            return self.cipher_suite.decrypt(encrypted_data)
        except Exception as e:
            logger.error(f"خطأ في فك تشفير البيانات: {e}")
            raise
    
    def decrypt_to_string(self, encrypted_data: str) -> str:
        """
        فك تشفير البيانات وإرجاعها كسلسلة نصية
        
        Args:
            encrypted_data: البيانات المشفرة
            
        Returns:
            البيانات المفكوكة التشفير كسلسلة نصية
        """
        return self.decrypt(encrypted_data).decode('utf-8')
    
    def decrypt_to_json(self, encrypted_data: str) -> Dict[str, Any]:
        """
        فك تشفير البيانات وإرجاعها كقاموس JSON
        
        Args:
            encrypted_data: البيانات المشفرة
            
        Returns:
            البيانات المفكوكة التشفير كقاموس
        """
        import json
        json_str = self.decrypt_to_string(encrypted_data)
        return json.loads(json_str)
    
    @staticmethod
    def generate_key() -> str:
        """
        إنشاء مفتاح تشفير جديد
        
        Returns:
            مفتاح التشفير الجديد كسلسلة نصية
        """
        key = Fernet.generate_key()
        return key.decode('utf-8')


def encrypt_task(task_content: str, vault: Optional[Vault] = None) -> str:
    """
    تشفير محتوى المهمة
    
    Args:
        task_content: محتوى المهمة
        vault: خزنة التشفير (اختياري)
        
    Returns:
        المحتوى المشفر
    """
    if vault is None:
        vault = Vault()
    
    return vault.encrypt(task_content)


def decrypt_task(encrypted_content: str, vault: Optional[Vault] = None) -> str:
    """
    فك تشفير محتوى المهمة
    
    Args:
        encrypted_content: المحتوى المشفر
        vault: خزنة التشفير (اختياري)
        
    Returns:
        محتوى المهمة الأصلي
    """
    if vault is None:
        vault = Vault()
    
    return vault.decrypt_to_string(encrypted_content)