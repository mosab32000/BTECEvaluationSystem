"""
نموذج المستخدم في نظام تقييم BTEC
"""
import uuid
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

from app import db, login_manager

class User(UserMixin, db.Model):
    """نموذج المستخدم في نظام تقييم BTEC."""
    __tablename__ = 'user'
    
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(36), default=lambda: str(uuid.uuid4()), unique=True)
    email = db.Column(db.String(120), index=True, unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    name = db.Column(db.String(100))
    role = db.Column(db.String(20), default='user')  # admin, teacher, student, user
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    
    # العلاقات
    evaluations = db.relationship('Evaluation', backref='user', lazy='dynamic')
    
    def __repr__(self):
        return f'<User {self.email}>'
    
    def set_password(self, password):
        """تعيين كلمة المرور المشفرة"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """التحقق من كلمة المرور"""
        return check_password_hash(self.password_hash, password)
    
    def get_id(self):
        """الحصول على معرف المستخدم للمصادقة"""
        return str(self.uuid)
    
    @property
    def is_admin(self):
        """التحقق مما إذا كان المستخدم مسؤولاً"""
        return self.role == 'admin'
    
    @property
    def is_teacher(self):
        """التحقق مما إذا كان المستخدم مدرساً"""
        return self.role == 'teacher'
    
    @property
    def is_student(self):
        """التحقق مما إذا كان المستخدم طالباً"""
        return self.role == 'student'
    
    def to_dict(self):
        """تحويل المستخدم إلى قاموس للواجهة البرمجية"""
        return {
            'id': self.id,
            'uuid': self.uuid,
            'email': self.email,
            'name': self.name,
            'role': self.role,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None
        }

@login_manager.user_loader
def load_user(user_id):
    """تحميل المستخدم للمصادقة"""
    return User.query.filter_by(uuid=user_id).first()