"""
نموذج المستخدم في نظام تقييم BTEC
"""
import json
from datetime import datetime, timedelta

from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship

from app import db

class User(UserMixin, db.Model):
    """نموذج المستخدم في نظام تقييم BTEC."""
    __tablename__ = 'user'
    
    # الأعمدة الأساسية
    id = Column(Integer, primary_key=True)
    email = Column(String(120), index=True, unique=True, nullable=False)
    password_hash = Column(String(256), nullable=False)
    name = Column(String(100))
    role = Column(String(20), default='student')  # admin, instructor, student
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    institution = Column(String(100))
    position = Column(String(100))
    profile_picture = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = Column(DateTime)
    settings = Column(Text)  # إعدادات المستخدم (JSON)
    
    # العلاقات
    evaluations_given = relationship('Evaluation', foreign_keys='Evaluation.evaluator_id', back_populates='evaluator', cascade='all, delete-orphan')
    evaluations_received = relationship('Evaluation', foreign_keys='Evaluation.student_id', back_populates='student', cascade='all, delete-orphan')
    courses = relationship('Course', back_populates='instructor')
    rubric_templates = relationship('RubricTemplate', back_populates='user')
    
    @property
    def password(self):
        """جعل كلمة المرور غير قابلة للقراءة."""
        raise AttributeError('لا يمكن قراءة كلمة المرور')
    
    @password.setter
    def password(self, password):
        """تعيين كلمة المرور مع تجزئتها."""
        self.password_hash = generate_password_hash(password)
    
    def verify_password(self, password):
        """التحقق من صحة كلمة المرور.
        
        Args:
            password: كلمة المرور المراد التحقق منها
            
        Returns:
            bool: ما إذا كانت كلمة المرور صحيحة
        """
        return check_password_hash(self.password_hash, password)
    
    def is_admin(self):
        """التحقق من أن المستخدم مسؤول.
        
        Returns:
            bool: ما إذا كان المستخدم مسؤولاً
        """
        return self.role == 'admin'
    
    def is_instructor(self):
        """التحقق من أن المستخدم مدرس.
        
        Returns:
            bool: ما إذا كان المستخدم مدرساً
        """
        return self.role == 'instructor'
    
    def is_student(self):
        """التحقق من أن المستخدم طالب.
        
        Returns:
            bool: ما إذا كان المستخدم طالباً
        """
        return self.role == 'student'
    
    def update_last_login(self):
        """تحديث وقت آخر تسجيل دخول."""
        self.last_login = datetime.utcnow()
        db.session.commit()
    
    def get_settings(self):
        """الحصول على إعدادات المستخدم.
        
        Returns:
            dict: إعدادات المستخدم
        """
        if not self.settings:
            return {}
        
        try:
            return json.loads(self.settings)
        except Exception:
            return {}
    
    def set_settings(self, settings):
        """تعيين إعدادات المستخدم.
        
        Args:
            settings: إعدادات المستخدم
        """
        self.settings = json.dumps(settings)
    
    def to_dict(self, include_private=False):
        """تحويل كائن المستخدم إلى قاموس.
        
        Args:
            include_private: ما إذا كان يجب تضمين المعلومات الخاصة
            
        Returns:
            dict: قاموس يمثل المستخدم
        """
        user_dict = {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'role': self.role,
            'is_active': self.is_active,
            'is_verified': self.is_verified,
            'institution': self.institution,
            'position': self.position,
            'profile_picture': self.profile_picture,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
        
        if include_private:
            user_dict.update({
                'updated_at': self.updated_at.isoformat() if self.updated_at else None,
                'last_login': self.last_login.isoformat() if self.last_login else None,
                'settings': self.get_settings()
            })
        
        return user_dict
    
    def __repr__(self):
        """تمثيل سلسلة نصية للمستخدم.
        
        Returns:
            str: تمثيل سلسلة نصية
        """
        return f"<User {self.id} {self.email} ({self.role})>"

class BlacklistedToken(db.Model):
    """نموذج الرموز المميزة المحظورة في نظام تقييم BTEC."""
    __tablename__ = 'blacklisted_token'
    
    id = Column(Integer, primary_key=True)
    jti = Column(String(36), unique=True, nullable=False)
    token_type = Column(String(10), nullable=False)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    expires = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    @classmethod
    def is_blacklisted(cls, jti):
        """التحقق مما إذا كان الرمز المميز محظوراً.
        
        Args:
            jti: معرف الرمز المميز
            
        Returns:
            bool: ما إذا كان الرمز المميز محظوراً
        """
        token = cls.query.filter_by(jti=jti).first()
        return bool(token and token.expires > datetime.utcnow())
    
    @classmethod
    def clean_expired_tokens(cls):
        """تنظيف الرموز المميزة المنتهية الصلاحية."""
        cls.query.filter(cls.expires < datetime.utcnow()).delete()
        db.session.commit()
    
    def __repr__(self):
        """تمثيل سلسلة نصية للرمز المميز المحظور.
        
        Returns:
            str: تمثيل سلسلة نصية
        """
        return f"<BlacklistedToken {self.jti} ({self.token_type})>"