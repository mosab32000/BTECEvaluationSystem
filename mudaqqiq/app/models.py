from datetime import datetime
import jwt
from time import time
import os
import uuid
from werkzeug.security import generate_password_hash, check_password_hash
from flask import current_app
from flask_login import UserMixin
from app import db, login_manager

# جدول العلاقة بين المستخدمين والأدوار
roles_users = db.Table('roles_users',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id')),
    db.Column('role_id', db.Integer, db.ForeignKey('roles.id'))
)

class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))
    
    def __repr__(self):
        return f'<Role {self.name}>'

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    email = db.Column(db.String(120), unique=True, index=True)
    password_hash = db.Column(db.String(128))
    full_name = db.Column(db.String(150))
    about_me = db.Column(db.Text)
    profile_image = db.Column(db.String(150), default='default_profile.png')
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # العلاقات
    roles = db.relationship('Role', secondary=roles_users, 
                           backref=db.backref('users', lazy='dynamic'))
    projects = db.relationship('Project', backref='owner', lazy='dynamic')
    audit_results = db.relationship('AuditResult', backref='auditor', lazy='dynamic')
    
    @property
    def password(self):
        raise AttributeError('لا يمكن الوصول إلى كلمة المرور!')
        
    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def has_role(self, role_name):
        return any(role.name == role_name for role in self.roles)
    
    def is_admin(self):
        return self.has_role('admin')
        
    def get_reset_password_token(self, expires_in=3600):
        return jwt.encode(
            {'reset_password': self.id, 'exp': time() + expires_in},
            current_app.config['SECRET_KEY'], algorithm='HS256'
        )
        
    @staticmethod
    def verify_reset_password_token(token):
        try:
            id = jwt.decode(token, current_app.config['SECRET_KEY'],
                           algorithms=['HS256'])['reset_password']
        except:
            return None
        return User.query.get(id)
        
    def __repr__(self):
        return f'<User {self.username}>'

@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))

class Project(db.Model):
    __tablename__ = 'projects'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text)
    project_type = db.Column(db.String(50))
    file_path = db.Column(db.String(255))
    status = db.Column(db.String(20), default='قيد الانتظار')  # قيد الانتظار، قيد التدقيق، مكتمل، مرفوض
    submission_date = db.Column(db.DateTime, default=datetime.utcnow)
    completion_date = db.Column(db.DateTime)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    # العلاقات
    audit_results = db.relationship('AuditResult', backref='project', lazy='dynamic')
    
    def generate_unique_filename(self, original_filename):
        """إنشاء اسم فريد للملف المرفوع"""
        _, extension = os.path.splitext(original_filename)
        return f'{uuid.uuid4().hex}{extension}'
    
    def __repr__(self):
        return f'<Project {self.title}>'

class AuditCriteria(db.Model):
    __tablename__ = 'audit_criteria'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    category = db.Column(db.String(50))
    weight = db.Column(db.Float, default=1.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<AuditCriteria {self.name}>'

class AuditResult(db.Model):
    __tablename__ = 'audit_results'
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'))
    auditor_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    audit_date = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='قيد التقدم')  # قيد التقدم، مكتمل
    score = db.Column(db.Float)
    feedback = db.Column(db.Text)
    result_details = db.Column(db.JSON)
    
    def __repr__(self):
        return f'<AuditResult {self.id} for Project {self.project_id}>'

class Notification(db.Model):
    __tablename__ = 'notifications'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    message = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(20), default='info')
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    read = db.Column(db.Boolean, default=False)
    
    user = db.relationship('User', backref=db.backref('notifications', lazy='dynamic'))
    
    def __repr__(self):
        return f'<Notification {self.id} for User {self.user_id}>'

class ActivityLog(db.Model):
    __tablename__ = 'activity_logs'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    action = db.Column(db.String(255), nullable=False)
    details = db.Column(db.Text)
    ip_address = db.Column(db.String(45))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', backref=db.backref('activities', lazy='dynamic'))
    
    def __repr__(self):
        return f'<ActivityLog {self.id} - {self.action}>'
