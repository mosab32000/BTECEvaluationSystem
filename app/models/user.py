"""
نموذج المستخدم في نظام تقييم BTEC
"""

import json
import logging
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

from app.database import get_db_conn, get_db_cursor

logger = logging.getLogger(__name__)

class User:
    """نموذج المستخدم في نظام تقييم BTEC"""
    
    def __init__(self, **kwargs):
        """
        تهيئة كائن المستخدم
        
        Args:
            id (int, optional): معرف المستخدم
            email (str, optional): البريد الإلكتروني
            password_hash (str, optional): تجزئة كلمة المرور (password hash)
            name (str, optional): الاسم
            role (str, optional): الدور (student, teacher, admin)
            is_active (bool, optional): ما إذا كان المستخدم نشطًا
            created_at (datetime, optional): تاريخ إنشاء الحساب
            updated_at (datetime, optional): تاريخ آخر تحديث
        """
        self.id = kwargs.get('id')
        self.email = kwargs.get('email')
        self.password_hash = kwargs.get('password_hash')
        self.name = kwargs.get('name')
        self.role = kwargs.get('role', 'student')
        self.is_active = kwargs.get('is_active', True)
        self.created_at = kwargs.get('created_at')
        self.updated_at = kwargs.get('updated_at')
    
    def set_password(self, password):
        """
        تعيين كلمة المرور (تخزين تجزئة كلمة المرور فقط)
        
        Args:
            password (str): كلمة المرور كنص عادي
            
        Returns:
            bool: True إذا تم تعيين كلمة المرور بنجاح
        """
        try:
            self.password_hash = generate_password_hash(password)
            return True
        except Exception as e:
            logger.error(f"خطأ عند تعيين كلمة المرور: {str(e)}")
            return False
    
    def check_password(self, password):
        """
        التحقق من صحة كلمة المرور
        
        Args:
            password (str): كلمة المرور كنص عادي للتحقق
            
        Returns:
            bool: True إذا كانت كلمة المرور صحيحة
        """
        try:
            if not self.password_hash:
                return False
            return check_password_hash(self.password_hash, password)
        except Exception as e:
            logger.error(f"خطأ عند التحقق من كلمة المرور: {str(e)}")
            return False
    
    @staticmethod
    def get_by_id(user_id):
        """
        الحصول على المستخدم بواسطة المعرف
        
        Args:
            user_id (int): معرف المستخدم
            
        Returns:
            User: كائن المستخدم أو None إذا لم يتم العثور عليه
        """
        conn, cursor = get_db_cursor()
        if not cursor:
            return None
        
        try:
            cursor.execute(
                "SELECT id, email, password_hash, name, role, is_active, created_at, updated_at FROM users WHERE id = %s",
                (user_id,)
            )
            row = cursor.fetchone()
            if row:
                return User(
                    id=row[0],
                    email=row[1],
                    password_hash=row[2],
                    name=row[3],
                    role=row[4],
                    is_active=row[5],
                    created_at=row[6],
                    updated_at=row[7]
                )
            return None
        except Exception as e:
            logger.error(f"خطأ عند الحصول على المستخدم بالمعرف {user_id}: {str(e)}")
            return None
        finally:
            if cursor:
                cursor.close()
            if conn:
                from app.database import db_pool
                if db_pool:
                    db_pool.putconn(conn)
    
    @staticmethod
    def get_by_email(email):
        """
        الحصول على المستخدم بواسطة البريد الإلكتروني
        
        Args:
            email (str): البريد الإلكتروني
            
        Returns:
            User: كائن المستخدم أو None إذا لم يتم العثور عليه
        """
        conn, cursor = get_db_cursor()
        if not cursor:
            return None
        
        try:
            cursor.execute(
                "SELECT id, email, password_hash, name, role, is_active, created_at, updated_at FROM users WHERE email = %s",
                (email,)
            )
            row = cursor.fetchone()
            if row:
                return User(
                    id=row[0],
                    email=row[1],
                    password_hash=row[2],
                    name=row[3],
                    role=row[4],
                    is_active=row[5],
                    created_at=row[6],
                    updated_at=row[7]
                )
            return None
        except Exception as e:
            logger.error(f"خطأ عند الحصول على المستخدم بالبريد الإلكتروني {email}: {str(e)}")
            return None
        finally:
            if cursor:
                cursor.close()
            if conn:
                from app.database import db_pool
                if db_pool:
                    db_pool.putconn(conn)
    
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
        conn, cursor = get_db_cursor()
        if not cursor:
            return []
        
        try:
            cursor.execute(
                "SELECT id, email, password_hash, name, role, is_active, created_at, updated_at FROM users LIMIT %s OFFSET %s",
                (limit, offset)
            )
            rows = cursor.fetchall()
            return [
                User(
                    id=row[0],
                    email=row[1],
                    password_hash=row[2],
                    name=row[3],
                    role=row[4],
                    is_active=row[5],
                    created_at=row[6],
                    updated_at=row[7]
                )
                for row in rows
            ]
        except Exception as e:
            logger.error(f"خطأ عند الحصول على قائمة المستخدمين: {str(e)}")
            return []
        finally:
            if cursor:
                cursor.close()
            if conn:
                from app.database import db_pool
                if db_pool:
                    db_pool.putconn(conn)
    
    def save(self):
        """
        حفظ المستخدم في قاعدة البيانات (إنشاء أو تحديث)
        
        Returns:
            bool: ما إذا تم الحفظ بنجاح
        """
        conn, cursor = get_db_cursor()
        if not cursor:
            return False
        
        try:
            if self.id:
                # تحديث مستخدم موجود
                cursor.execute(
                    """
                    UPDATE users
                    SET email = %s, password_hash = %s, name = %s, role = %s, is_active = %s, updated_at = NOW()
                    WHERE id = %s
                    RETURNING updated_at
                    """,
                    (self.email, self.password_hash, self.name, self.role, self.is_active, self.id)
                )
                self.updated_at = cursor.fetchone()[0]
            else:
                # إنشاء مستخدم جديد
                cursor.execute(
                    """
                    INSERT INTO users (email, password_hash, name, role, is_active)
                    VALUES (%s, %s, %s, %s, %s)
                    RETURNING id, created_at, updated_at
                    """,
                    (self.email, self.password_hash, self.name, self.role, self.is_active)
                )
                self.id, self.created_at, self.updated_at = cursor.fetchone()
            
            conn.commit()
            return True
        except Exception as e:
            conn.rollback()
            logger.error(f"خطأ عند حفظ المستخدم: {str(e)}")
            return False
        finally:
            if cursor:
                cursor.close()
            if conn:
                from app.database import db_pool
                if db_pool:
                    db_pool.putconn(conn)
    
    def delete(self):
        """
        حذف المستخدم من قاعدة البيانات
        
        Returns:
            bool: ما إذا تم الحذف بنجاح
        """
        if not self.id:
            return False
        
        conn, cursor = get_db_cursor()
        if not cursor:
            return False
        
        try:
            cursor.execute("DELETE FROM users WHERE id = %s", (self.id,))
            conn.commit()
            self.id = None
            return True
        except Exception as e:
            conn.rollback()
            logger.error(f"خطأ عند حذف المستخدم: {str(e)}")
            return False
        finally:
            if cursor:
                cursor.close()
            if conn:
                from app.database import db_pool
                if db_pool:
                    db_pool.putconn(conn)
    
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
    
    def __repr__(self):
        """
        تمثيل المستخدم كسلسلة نصية
        
        Returns:
            str: تمثيل المستخدم
        """
        return f"<User id={self.id} email={self.email} role={self.role}>"