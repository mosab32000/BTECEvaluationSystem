"""
وحدة التشفير في نظام تقييم BTEC
توفر وظائف التشفير وفك التشفير للبيانات الحساسة
"""

import os
import base64
import logging
import json
from typing import Dict, Any, Optional, Union

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

logger = logging.getLogger(__name__)

# المتغيرات العامة
_encryption_key: Optional[str] = None
_fernet: Optional[Fernet] = None

def _derive_key(password: Union[str, bytes], salt: bytes = None) -> bytes:
    """
    اشتقاق مفتاح من كلمة مرور وملح
    
    Args:
        password (Union[str, bytes]): كلمة المرور
        salt (bytes, optional): الملح المستخدم. إذا كان None، سيتم إنشاء ملح عشوائي
    
    Returns:
        bytes: المفتاح المشتق
    """
    if isinstance(password, str):
        password = password.encode()
    
    if salt is None:
        salt = os.urandom(16)
    
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
    )
    
    return base64.urlsafe_b64encode(kdf.derive(password))

def init_encryption(encryption_key: Optional[str] = None) -> None:
    """
    تهيئة نظام التشفير
    
    Args:
        encryption_key (Optional[str], optional): مفتاح التشفير. إذا كان None، سيتم استخدام مفتاح البيئة
    """
    global _encryption_key, _fernet
    
    # استخدام المفتاح المعطى أو البحث عنه في متغيرات البيئة
    key = encryption_key or os.environ.get('ENCRYPTION_KEY')
    
    if not key:
        logger.warning("لم يتم العثور على مفتاح التشفير. تم تعطيل التشفير.")
        _encryption_key = None
        _fernet = None
        return
    
    try:
        # التحقق من صحة المفتاح
        if len(key) < 32:
            # إذا كان المفتاح قصيرًا جدًا، اشتق مفتاحًا جديدًا منه
            key = _derive_key(key)
            key = base64.urlsafe_b64decode(key)
            key = base64.urlsafe_b64encode(key)
        
        # تحويل المفتاح إلى بايت إذا كان سلسلة نصية
        if isinstance(key, str):
            key = key.encode()
        
        # التحقق من صحة تنسيق المفتاح
        Fernet(key)
        
        _encryption_key = key
        _fernet = Fernet(key)
        logger.info("تم تهيئة نظام التشفير بنجاح.")
    except Exception as e:
        logger.error(f"خطأ في تهيئة نظام التشفير: {str(e)}")
        _encryption_key = None
        _fernet = None

def encrypt(data: str) -> Optional[str]:
    """
    تشفير البيانات
    
    Args:
        data (str): البيانات المراد تشفيرها
    
    Returns:
        Optional[str]: البيانات المشفرة كسلسلة نصية base64، أو None إذا فشل التشفير
    """
    if not _fernet:
        logger.warning("محاولة تشفير البيانات لكن نظام التشفير غير مهيأ.")
        return None
    
    try:
        encrypted_data = _fernet.encrypt(data.encode())
        return encrypted_data.decode()
    except Exception as e:
        logger.error(f"خطأ في تشفير البيانات: {str(e)}")
        return None

def decrypt(encrypted_data: str) -> Optional[str]:
    """
    فك تشفير البيانات
    
    Args:
        encrypted_data (str): البيانات المشفرة كسلسلة نصية base64
    
    Returns:
        Optional[str]: البيانات المفكوكة كسلسلة نصية، أو None إذا فشل فك التشفير
    """
    if not _fernet:
        logger.warning("محاولة فك تشفير البيانات لكن نظام التشفير غير مهيأ.")
        return None
    
    try:
        decrypted_data = _fernet.decrypt(encrypted_data.encode())
        return decrypted_data.decode()
    except Exception as e:
        logger.error(f"خطأ في فك تشفير البيانات: {str(e)}")
        return None

class Vault:
    """
    خزانة للبيانات المشفرة
    توفر واجهة لتخزين واسترجاع البيانات المشفرة
    """
    
    def __init__(self, initial_data: Dict[str, Any] = None):
        """
        إنشاء خزانة جديدة
        
        Args:
            initial_data (Dict[str, Any], optional): البيانات الأولية للخزانة
        """
        self._data = initial_data or {}
    
    @classmethod
    def from_encrypted(cls, encrypted_data: str) -> Optional['Vault']:
        """
        إنشاء خزانة من بيانات مشفرة
        
        Args:
            encrypted_data (str): البيانات المشفرة
        
        Returns:
            Optional[Vault]: الخزانة، أو None إذا فشل فك التشفير
        """
        if not encrypted_data:
            return Vault()
        
        decrypted_data = decrypt(encrypted_data)
        if not decrypted_data:
            logger.error("فشل فك تشفير البيانات لإنشاء الخزانة.")
            return None
        
        try:
            data = json.loads(decrypted_data)
            return cls(data)
        except json.JSONDecodeError:
            logger.error("فشل تحليل البيانات المفكوكة كـ JSON.")
            return None
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        الحصول على قيمة من الخزانة
        
        Args:
            key (str): المفتاح
            default (Any, optional): القيمة الافتراضية إذا لم يتم العثور على المفتاح
        
        Returns:
            Any: القيمة المخزنة، أو القيمة الافتراضية إذا لم يتم العثور على المفتاح
        """
        return self._data.get(key, default)
    
    def set(self, key: str, value: Any) -> None:
        """
        تعيين قيمة في الخزانة
        
        Args:
            key (str): المفتاح
            value (Any): القيمة
        """
        self._data[key] = value
    
    def delete(self, key: str) -> None:
        """
        حذف قيمة من الخزانة
        
        Args:
            key (str): المفتاح
        """
        if key in self._data:
            del self._data[key]
    
    def to_encrypted(self) -> Optional[str]:
        """
        تحويل الخزانة إلى بيانات مشفرة
        
        Returns:
            Optional[str]: البيانات المشفرة، أو None إذا فشل التشفير
        """
        try:
            serialized_data = json.dumps(self._data)
            return encrypt(serialized_data)
        except Exception as e:
            logger.error(f"خطأ في تشفير بيانات الخزانة: {str(e)}")
            return None
    
    def keys(self) -> list:
        """
        الحصول على قائمة بالمفاتيح في الخزانة
        
        Returns:
            list: قائمة المفاتيح
        """
        return list(self._data.keys())
    
    def __contains__(self, key: str) -> bool:
        """
        التحقق مما إذا كان المفتاح موجودًا في الخزانة
        
        Args:
            key (str): المفتاح
        
        Returns:
            bool: ما إذا كان المفتاح موجودًا
        """
        return key in self._data
    
    def __len__(self) -> int:
        """
        الحصول على عدد العناصر في الخزانة
        
        Returns:
            int: عدد العناصر
        """
        return len(self._data)
    
    def clear(self) -> None:
        """
        مسح جميع البيانات من الخزانة
        """
        self._data.clear()
    
    def update(self, other: Dict[str, Any]) -> None:
        """
        تحديث البيانات بقاموس آخر
        
        Args:
            other (Dict[str, Any]): القاموس الآخر
        """
        self._data.update(other)