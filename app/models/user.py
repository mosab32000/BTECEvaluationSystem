"""
نموذج المستخدم في نظام تقييم BTEC
"""

import datetime
from typing import Dict, Any, List, Optional

from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from app.extensions import db

class User(db.Model, UserMixin):
    """نموذج المستخدم في نظام تقييم BTEC"""
    __tablename__ = 'users'
    
    # حقول قاعدة البيانات
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), index=True, unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    name = db.Column(db.String(100))
    role = db.Column(db.String(20), default='student')  # student, teacher, admin
    is_active = db.Column(db.Boolean, default=True)
    last_login = db.Column(db.DateTime)
    profile_picture = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    
    # العلاقات
    # evaluations_submitted = db.relationship('Evaluation', foreign_keys='Evaluation.student_id', backref='student', lazy='dynamic')
    # evaluations_evaluated = db.relationship('Evaluation', foreign_keys='Evaluation.evaluator_id', backref='evaluator', lazy='dynamic')
    # classrooms = db.relationship('Classroom', backref='teacher', lazy='dynamic')
    # class_participations = db.relationship('ClassroomParticipant', backref='user', lazy='dynamic')
    # created_rubrics = db.relationship('Rubric', backref='creator', lazy='dynamic')
    # assigned_tasks = db.relationship('Task', foreign_keys='Task.assigned_to', backref='assigned_user', lazy='dynamic')
    # created_tasks = db.relationship('Task', foreign_keys='Task.created_by', backref='creator', lazy='dynamic')
    
    def __repr__(self):
        return f'<User {self.email} - {self.role}>'
    
    def set_password(self, password: str) -> None:
        """
        تعيين كلمة المرور المشفرة
        
        Args:
            password (str): كلمة المرور الأصلية
        """
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password: str) -> bool:
        """
        التحقق من صحة كلمة المرور
        
        Args:
            password (str): كلمة المرور المراد التحقق منها
        
        Returns:
            bool: ما إذا كانت كلمة المرور صحيحة
        """
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self) -> Dict[str, Any]:
        """
        تحويل المستخدم إلى قاموس
        
        Returns:
            Dict[str, Any]: بيانات المستخدم
        """
        return {
            'id': self.id,
            'email': self.email,
            'name': self.name,
            'role': self.role,
            'is_active': self.is_active,
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'profile_picture': self.profile_picture,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    @classmethod
    def get_by_email(cls, email: str) -> Optional['User']:
        """
        الحصول على مستخدم حسب البريد الإلكتروني
        
        Args:
            email (str): البريد الإلكتروني للمستخدم
        
        Returns:
            Optional[User]: المستخدم أو None إذا لم يتم العثور عليه
        """
        return cls.query.filter_by(email=email).first()
    
    @classmethod
    def get_by_id(cls, user_id: int) -> Optional['User']:
        """
        الحصول على مستخدم حسب المعرف
        
        Args:
            user_id (int): معرف المستخدم
        
        Returns:
            Optional[User]: المستخدم أو None إذا لم يتم العثور عليه
        """
        return cls.query.get(user_id)
    
    @classmethod
    def get_all_active(cls) -> List['User']:
        """
        الحصول على جميع المستخدمين النشطين
        
        Returns:
            List[User]: قائمة المستخدمين النشطين
        """
        return cls.query.filter_by(is_active=True).all()
    
    @classmethod
    def get_by_role(cls, role: str) -> List['User']:
        """
        الحصول على المستخدمين حسب الدور
        
        Args:
            role (str): دور المستخدمين (student, teacher, admin)
        
        Returns:
            List[User]: قائمة المستخدمين
        """
        return cls.query.filter_by(role=role, is_active=True).all()
    
    def update_last_login(self) -> None:
        """
        تحديث وقت آخر تسجيل دخول
        """
        self.last_login = datetime.datetime.utcnow()
    
    def deactivate(self) -> None:
        """
        تعطيل المستخدم
        """
        self.is_active = False
    
    def activate(self) -> None:
        """
        تنشيط المستخدم
        """
        self.is_active = True
    
    def change_role(self, new_role: str) -> None:
        """
        تغيير دور المستخدم
        
        Args:
            new_role (str): الدور الجديد (student, teacher, admin)
        """
        valid_roles = ['student', 'teacher', 'admin']
        if new_role not in valid_roles:
            raise ValueError(f"الدور '{new_role}' غير صالح. الأدوار الصالحة هي {', '.join(valid_roles)}")
        
        self.role = new_role
    
    @property
    def is_admin(self) -> bool:
        """
        التحقق مما إذا كان المستخدم مسؤولاً
        
        Returns:
            bool: ما إذا كان المستخدم مسؤولاً
        """
        return self.role == 'admin'
    
    @property
    def is_teacher(self) -> bool:
        """
        التحقق مما إذا كان المستخدم معلماً
        
        Returns:
            bool: ما إذا كان المستخدم معلماً
        """
        return self.role == 'teacher'
    
    @property
    def is_student(self) -> bool:
        """
        التحقق مما إذا كان المستخدم طالباً
        
        Returns:
            bool: ما إذا كان المستخدم طالباً
        """
        return self.role == 'student'
    
    def get_submitted_evaluations(self) -> List['Evaluation']:
        """
        الحصول على التقييمات المقدمة من المستخدم
        
        Returns:
            List[Evaluation]: قائمة التقييمات
        """
        from app.models.evaluation import Evaluation
        return Evaluation.query.filter_by(student_id=self.id).all()
    
    def get_evaluated_evaluations(self) -> List['Evaluation']:
        """
        الحصول على التقييمات المقيمة من قبل المستخدم
        
        Returns:
            List[Evaluation]: قائمة التقييمات
        """
        from app.models.evaluation import Evaluation
        return Evaluation.query.filter_by(evaluator_id=self.id).all()
    
    def get_classrooms(self) -> List['Classroom']:
        """
        الحصول على الفصول الدراسية التي أنشأها المستخدم
        
        Returns:
            List[Classroom]: قائمة الفصول الدراسية
        """
        from app.models.classroom import Classroom
        return Classroom.query.filter_by(teacher_id=self.id, is_active=True).all()
    
    def get_participating_classrooms(self) -> List['Classroom']:
        """
        الحصول على الفصول الدراسية التي يشارك فيها المستخدم
        
        Returns:
            List[Classroom]: قائمة الفصول الدراسية
        """
        from app.models.participant import ClassroomParticipant
        from app.models.classroom import Classroom
        
        participations = ClassroomParticipant.query.filter_by(user_id=self.id, is_active=True).all()
        classroom_ids = [p.classroom_id for p in participations]
        
        return Classroom.query.filter(Classroom.id.in_(classroom_ids), Classroom.is_active == True).all()