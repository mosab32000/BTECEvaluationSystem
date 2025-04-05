"""
نموذج المستخدم في نظام تقييم BTEC
"""
import logging
import json
from datetime import datetime

from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

from app.database import get_db_conn, get_db_cursor

# تهيئة السجل
logger = logging.getLogger(__name__)

class User(UserMixin):
    """نموذج المستخدم في نظام تقييم BTEC"""
    
    def __init__(self, **kwargs):
        """
        تهيئة كائن المستخدم
        
        Args:
            id (int, optional): معرف المستخدم
            email (str, optional): البريد الإلكتروني
            password_hash (str, optional): تجزئة كلمة المرور
            name (str, optional): الاسم
            role (str, optional): الدور (admin, evaluator, student)
            is_active (bool, optional): حالة النشاط
            created_at (datetime, optional): تاريخ إنشاء الحساب
            updated_at (datetime, optional): تاريخ آخر تحديث
        """
        self.id = kwargs.get('id')
        self.email = kwargs.get('email')
        self.password_hash = kwargs.get('password_hash')
        self.name = kwargs.get('name')
        self.role = kwargs.get('role', 'student')  # الدور الافتراضي هو طالب
        self.is_active = kwargs.get('is_active', True)  # المستخدم نشط افتراضيًا
        self.created_at = kwargs.get('created_at')
        self.updated_at = kwargs.get('updated_at')
    
    def check_password(self, password):
        """
        التحقق من كلمة المرور
        
        Args:
            password (str): كلمة المرور للتحقق
            
        Returns:
            bool: ما إذا كانت كلمة المرور صحيحة
        """
        if not self.password_hash:
            return False
        
        return check_password_hash(self.password_hash, password)
    
    def set_password(self, password):
        """
        تعيين كلمة المرور
        
        Args:
            password (str): كلمة المرور
        """
        self.password_hash = generate_password_hash(password)
    
    @staticmethod
    def get_by_id(user_id):
        """
        الحصول على المستخدم بواسطة المعرف
        
        Args:
            user_id (int): معرف المستخدم
            
        Returns:
            User: كائن المستخدم أو None إذا لم يتم العثور عليه
        """
        try:
            query = "SELECT * FROM users WHERE id = %s"
            with get_db_cursor() as cursor:
                cursor.execute(query, (user_id,))
                user_data = cursor.fetchone()
                
                if user_data:
                    user_dict = dict(user_data)
                    return User(**user_dict)
                
            return None
        
        except Exception as e:
            logger.error(f"خطأ في الحصول على المستخدم بواسطة المعرف: {e}")
            return None
    
    @staticmethod
    def get_by_email(email):
        """
        الحصول على المستخدم بواسطة البريد الإلكتروني
        
        Args:
            email (str): البريد الإلكتروني
            
        Returns:
            User: كائن المستخدم أو None إذا لم يتم العثور عليه
        """
        try:
            query = "SELECT * FROM users WHERE email = %s"
            with get_db_cursor() as cursor:
                cursor.execute(query, (email,))
                user_data = cursor.fetchone()
                
                if user_data:
                    user_dict = dict(user_data)
                    return User(**user_dict)
                
            return None
        
        except Exception as e:
            logger.error(f"خطأ في الحصول على المستخدم بواسطة البريد الإلكتروني: {e}")
            return None
    
    @staticmethod
    def get_all(limit=100, offset=0):
        """
        الحصول على قائمة المستخدمين
        
        Args:
            limit (int, optional): الحد الأقصى للنتائج. الافتراضي هو 100.
            offset (int, optional): بداية النتائج. الافتراضي هو 0.
            
        Returns:
            list: قائمة كائنات المستخدمين
        """
        try:
            query = "SELECT * FROM users ORDER BY id LIMIT %s OFFSET %s"
            with get_db_cursor() as cursor:
                cursor.execute(query, (limit, offset))
                users_data = cursor.fetchall()
                
                users = []
                for user_data in users_data:
                    user_dict = dict(user_data)
                    users.append(User(**user_dict))
                
                return users
        
        except Exception as e:
            logger.error(f"خطأ في الحصول على قائمة المستخدمين: {e}")
            return []
    
    @staticmethod
    def get_by_role(role, limit=100, offset=0):
        """
        الحصول على قائمة المستخدمين حسب الدور
        
        Args:
            role (str): الدور (admin, evaluator, student)
            limit (int, optional): الحد الأقصى للنتائج. الافتراضي هو 100.
            offset (int, optional): بداية النتائج. الافتراضي هو 0.
            
        Returns:
            list: قائمة كائنات المستخدمين
        """
        try:
            query = "SELECT * FROM users WHERE role = %s ORDER BY id LIMIT %s OFFSET %s"
            with get_db_cursor() as cursor:
                cursor.execute(query, (role, limit, offset))
                users_data = cursor.fetchall()
                
                users = []
                for user_data in users_data:
                    user_dict = dict(user_data)
                    users.append(User(**user_dict))
                
                return users
        
        except Exception as e:
            logger.error(f"خطأ في الحصول على قائمة المستخدمين حسب الدور: {e}")
            return []
    
    def save(self):
        """
        حفظ المستخدم في قاعدة البيانات (إنشاء أو تحديث)
        
        Returns:
            bool: ما إذا تم الحفظ بنجاح
        """
        try:
            conn = get_db_conn()
            cursor = conn.cursor()
            
            # الحصول على التاريخ الحالي للتحديث
            current_time = datetime.now()
            
            # تحديث مستخدم موجود
            if self.id:
                query = """
                    UPDATE users SET 
                        email = %s,
                        password_hash = %s,
                        name = %s,
                        role = %s,
                        is_active = %s,
                        updated_at = %s
                    WHERE id = %s
                """
                cursor.execute(query, (
                    self.email,
                    self.password_hash,
                    self.name,
                    self.role,
                    self.is_active,
                    current_time,
                    self.id
                ))
            
            # إنشاء مستخدم جديد
            else:
                query = """
                    INSERT INTO users (
                        email, password_hash, name, role, is_active, created_at, updated_at
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    RETURNING id
                """
                cursor.execute(query, (
                    self.email,
                    self.password_hash,
                    self.name,
                    self.role,
                    self.is_active,
                    current_time,
                    current_time
                ))
                
                # الحصول على معرف المستخدم الجديد
                self.id = cursor.fetchone()[0]
                self.created_at = current_time
            
            self.updated_at = current_time
            conn.commit()
            return True
        
        except Exception as e:
            if conn:
                conn.rollback()
            logger.error(f"خطأ في حفظ المستخدم: {e}")
            return False
        
        finally:
            if cursor:
                cursor.close()
    
    def delete(self):
        """
        حذف المستخدم من قاعدة البيانات
        
        Returns:
            bool: ما إذا تم الحذف بنجاح
        """
        if not self.id:
            return False
        
        try:
            conn = get_db_conn()
            cursor = conn.cursor()
            
            query = "DELETE FROM users WHERE id = %s"
            cursor.execute(query, (self.id,))
            
            conn.commit()
            return True
        
        except Exception as e:
            if conn:
                conn.rollback()
            logger.error(f"خطأ في حذف المستخدم: {e}")
            return False
        
        finally:
            if cursor:
                cursor.close()
    
    def to_dict(self):
        """
        تحويل المستخدم إلى قاموس
        
        Returns:
            dict: بيانات المستخدم كقاموس
        """
        return {
            'id': self.id,
            'email': self.email,
            'name': self.name,
            'role': self.role,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def is_authenticated(self):
        """
        التحقق مما إذا كان المستخدم مصادقًا
        
        Returns:
            bool: ما إذا كان المستخدم مصادقًا
        """
        return True
    
    def is_active(self):
        """
        التحقق مما إذا كان المستخدم نشطًا
        
        Returns:
            bool: ما إذا كان المستخدم نشطًا
        """
        return self.is_active
    
    def is_anonymous(self):
        """
        التحقق مما إذا كان المستخدم مجهولاً
        
        Returns:
            bool: ما إذا كان المستخدم مجهولاً
        """
        return False
    
    def get_id(self):
        """
        الحصول على معرف المستخدم (مطلوب لـ flask-login)
        
        Returns:
            str: معرف المستخدم كسلسلة نصية
        """
        return str(self.id)
    
    def __repr__(self):
        """
        تمثيل المستخدم كسلسلة نصية
        
        Returns:
            str: تمثيل المستخدم
        """
        return f'<User {self.id}: {self.email}>'