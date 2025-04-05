"""
نموذج المستخدم في نظام تقييم BTEC
"""

from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from app.extensions import db


class User(db.Model, UserMixin):
    """نموذج المستخدم في نظام تقييم BTEC."""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), index=True, unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    name = db.Column(db.String(100))
    role = db.Column(db.String(20), default='student')  # student, teacher, admin
    is_active = db.Column(db.Boolean, default=True)
    avatar = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # العلاقات
    evaluations_submitted = db.relationship('Evaluation', foreign_keys='Evaluation.student_id', backref='student', lazy='dynamic')
    evaluations_reviewed = db.relationship('Evaluation', foreign_keys='Evaluation.evaluator_id', backref='evaluator', lazy='dynamic')
    created_rubrics = db.relationship('Rubric', backref='creator', lazy='dynamic')
    
    def __repr__(self):
        return f'<User {self.email}>'
    
    def set_password(self, password):
        """تعيين كلمة المرور المشفرة للمستخدم.
        
        Args:
            password (str): كلمة المرور الجديدة
        """
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """التحقق من صحة كلمة المرور.
        
        Args:
            password (str): كلمة المرور المراد التحقق منها
            
        Returns:
            bool: True إذا كانت كلمة المرور صحيحة، False خلاف ذلك
        """
        return check_password_hash(self.password_hash, password)
    
    def has_role(self, role):
        """التحقق مما إذا كان المستخدم يملك دورًا معينًا.
        
        Args:
            role (str): الدور المطلوب التحقق منه
            
        Returns:
            bool: True إذا كان المستخدم يملك الدور، False خلاف ذلك
        """
        if role == 'admin':
            return self.role == 'admin'
        elif role == 'teacher':
            return self.role in ['admin', 'teacher']
        elif role == 'student':
            return self.role == 'student'
        return False
    
    @property
    def is_admin(self):
        """التحقق مما إذا كان المستخدم مديرًا.
        
        Returns:
            bool: True إذا كان المستخدم مديرًا، False خلاف ذلك
        """
        return self.role == 'admin'
    
    @property
    def is_teacher(self):
        """التحقق مما إذا كان المستخدم معلمًا.
        
        Returns:
            bool: True إذا كان المستخدم معلمًا، False خلاف ذلك
        """
        return self.role == 'teacher'
    
    @property
    def is_student(self):
        """التحقق مما إذا كان المستخدم طالبًا.
        
        Returns:
            bool: True إذا كان المستخدم طالبًا، False خلاف ذلك
        """
        return self.role == 'student'
    
    def to_dict(self):
        """تحويل بيانات المستخدم إلى قاموس.
        
        Returns:
            dict: بيانات المستخدم
        """
        return {
            'id': self.id,
            'email': self.email,
            'name': self.name,
            'role': self.role,
            'is_active': self.is_active,
            'avatar': self.avatar,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }