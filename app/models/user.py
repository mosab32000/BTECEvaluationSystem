"""
نموذج المستخدم في نظام تقييم BTEC
"""

from datetime import datetime

from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from app.extensions import db


class User(UserMixin, db.Model):
    """نموذج المستخدم في نظام تقييم BTEC."""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), index=True, unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    name = db.Column(db.String(100))
    role = db.Column(db.String(20), default='student')  # student, teacher, admin
    is_active = db.Column(db.Boolean, default=True)
    last_login = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<User {self.id} - {self.email}>'
    
    def set_password(self, password):
        """تعيين كلمة مرور المستخدم
        
        Args:
            password (str): كلمة المرور الجديدة
        """
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """التحقق من كلمة مرور المستخدم
        
        Args:
            password (str): كلمة المرور المراد التحقق منها
        
        Returns:
            bool: True إذا كانت كلمة المرور صحيحة، False خلاف ذلك
        """
        return check_password_hash(self.password_hash, password)
    
    def is_admin(self):
        """التحقق مما إذا كان المستخدم مسؤولًا
        
        Returns:
            bool: True إذا كان المستخدم مسؤولًا، False خلاف ذلك
        """
        return self.role == 'admin'
    
    def is_teacher(self):
        """التحقق مما إذا كان المستخدم معلمًا
        
        Returns:
            bool: True إذا كان المستخدم معلمًا، False خلاف ذلك
        """
        return self.role == 'teacher'
    
    def is_student(self):
        """التحقق مما إذا كان المستخدم طالبًا
        
        Returns:
            bool: True إذا كان المستخدم طالبًا، False خلاف ذلك
        """
        return self.role == 'student'
    
    def to_dict(self):
        """تحويل بيانات المستخدم إلى قاموس
        
        Returns:
            dict: بيانات المستخدم
        """
        return {
            'id': self.id,
            'email': self.email,
            'name': self.name,
            'role': self.role,
            'is_active': self.is_active,
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }