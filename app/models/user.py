"""
نموذج المستخدم في نظام تقييم BTEC
"""

import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from app import db

class User(db.Model):
    """نموذج المستخدم في نظام تقييم BTEC."""
    __tablename__ = 'user'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), index=True, unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    name = db.Column(db.String(100))
    role = db.Column(db.String(20), default='user')  # يمكن أن يكون 'user', 'admin', 'teacher'
    is_active = db.Column(db.Boolean, default=True)
    last_login = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    
    def set_password(self, password):
        """تعيين كلمة المرور المشفرة."""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """التحقق من صحة كلمة المرور."""
        return check_password_hash(self.password_hash, password)
    
    def is_admin(self):
        """التحقق ما إذا كان المستخدم مسؤولاً."""
        return self.role == 'admin'
    
    def is_teacher(self):
        """التحقق ما إذا كان المستخدم معلماً."""
        return self.role == 'teacher'
    
    def update_last_login(self):
        """تحديث وقت آخر تسجيل دخول."""
        self.last_login = datetime.datetime.utcnow()
        db.session.commit()
    
    def to_dict(self):
        """تحويل بيانات المستخدم إلى قاموس."""
        return {
            'id': self.id,
            'email': self.email,
            'name': self.name,
            'role': self.role,
            'is_active': self.is_active,
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'created_at': self.created_at.isoformat()
        }
    
    def __repr__(self):
        return f'<User {self.email}>'
