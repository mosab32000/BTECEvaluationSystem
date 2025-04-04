"""
نموذج المستخدم في نظام تقييم BTEC
"""
import datetime

from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app import db

class User(db.Model, UserMixin):
    """
    نموذج المستخدم في نظام تقييم BTEC
    """
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    email = Column(String(120), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    name = Column(String(100), nullable=False)
    role = Column(String(20), default='user')
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    institution = Column(String(200), nullable=True)
    position = Column(String(100), nullable=True)
    profile_image = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    last_login = Column(DateTime, nullable=True)
    
    # العلاقات
    evaluations = relationship('Evaluation', back_populates='evaluator', cascade='all, delete-orphan')
    student_evaluations = relationship('Evaluation', foreign_keys='Evaluation.student_id', 
                                      back_populates='student', cascade='all, delete-orphan')
    
    @property
    def password(self):
        """
        منع الوصول المباشر إلى كلمة المرور
        """
        raise AttributeError('كلمة المرور غير قابلة للقراءة')
    
    @password.setter
    def password(self, password):
        """
        تعيين كلمة المرور (مع التشفير)
        
        Args:
            password: كلمة المرور الجديدة
        """
        self.password_hash = generate_password_hash(password)
    
    def verify_password(self, password):
        """
        التحقق من صحة كلمة المرور
        
        Args:
            password: كلمة المرور المراد التحقق منها
            
        Returns:
            bool: ما إذا كانت كلمة المرور صحيحة
        """
        return check_password_hash(self.password_hash, password)
    
    def is_admin(self):
        """
        التحقق مما إذا كان المستخدم مسؤولاً
        
        Returns:
            bool: ما إذا كان المستخدم مسؤولاً
        """
        return self.role == 'admin'
    
    def is_instructor(self):
        """
        التحقق مما إذا كان المستخدم مدرسًا
        
        Returns:
            bool: ما إذا كان المستخدم مدرسًا
        """
        return self.role == 'instructor'
    
    def is_student(self):
        """
        التحقق مما إذا كان المستخدم طالبًا
        
        Returns:
            bool: ما إذا كان المستخدم طالبًا
        """
        return self.role == 'student'
    
    def update_last_login(self):
        """
        تحديث وقت آخر تسجيل دخول
        """
        self.last_login = datetime.datetime.utcnow()
        db.session.commit()
    
    def to_dict(self, include_private=False):
        """
        تحويل المستخدم إلى قاموس
        
        Args:
            include_private: ما إذا كان يجب تضمين الحقول الخاصة
            
        Returns:
            dict: بيانات المستخدم
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
            'profile_image': self.profile_image,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
        
        if include_private:
            user_dict.update({
                'last_login': self.last_login.isoformat() if self.last_login else None,
            })
        
        return user_dict
    
    def __repr__(self):
        """
        تمثيل المستخدم كسلسلة نصية
        
        Returns:
            str: تمثيل المستخدم
        """
        return f'<User {self.email}: {self.name} ({self.role})>'


class BlacklistedToken(db.Model):
    """
    نموذج للرموز المميزة المحظورة (للتحكم في عمليات تسجيل الخروج)
    """
    __tablename__ = 'blacklisted_tokens'
    
    id = Column(Integer, primary_key=True)
    jti = Column(String(36), nullable=False, index=True)
    token_type = Column(String(10), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    blacklisted_on = Column(DateTime, default=datetime.datetime.utcnow)
    expires = Column(DateTime, nullable=False)
    
    def to_dict(self):
        """
        تحويل الرمز المميز المحظور إلى قاموس
        
        Returns:
            dict: بيانات الرمز المميز المحظور
        """
        return {
            'token_id': self.id,
            'jti': self.jti,
            'token_type': self.token_type,
            'user_id': self.user_id,
            'blacklisted_on': self.blacklisted_on.isoformat() if self.blacklisted_on else None,
            'expires': self.expires.isoformat() if self.expires else None
        }
    
    @classmethod
    def is_blacklisted(cls, jti):
        """
        التحقق مما إذا كان الرمز المميز محظورًا
        
        Args:
            jti: معرف الرمز المميز
            
        Returns:
            bool: ما إذا كان الرمز المميز محظورًا
        """
        return cls.query.filter_by(jti=jti).first() is not None