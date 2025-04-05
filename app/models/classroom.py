"""
نموذج الفصل الدراسي في نظام تقييم BTEC
"""

import datetime
from typing import Dict, Any, Optional, List

from app.extensions import db

class Classroom(db.Model):
    """نموذج الفصل الدراسي في نظام تقييم BTEC"""
    __tablename__ = 'classrooms'
    
    # حقول قاعدة البيانات
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    code = db.Column(db.String(20), unique=True, nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    # العلاقات
    # teacher = db.relationship('User', backref='classrooms')
    # sessions = db.relationship('Session', backref='classroom', lazy='dynamic')
    # participants = db.relationship('ClassroomParticipant', backref='classroom', lazy='dynamic')
    
    def __repr__(self):
        return f'<Classroom {self.name}>'
    
    def to_dict(self) -> Dict[str, Any]:
        """
        تحويل الفصل الدراسي إلى قاموس
        
        Returns:
            Dict[str, Any]: بيانات الفصل الدراسي
        """
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'code': self.code,
            'teacher_id': self.teacher_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'is_active': self.is_active
        }
    
    @classmethod
    def get_by_id(cls, classroom_id: int) -> Optional['Classroom']:
        """
        الحصول على فصل دراسي حسب المعرف
        
        Args:
            classroom_id (int): معرف الفصل الدراسي
        
        Returns:
            Optional[Classroom]: الفصل الدراسي أو None إذا لم يتم العثور عليه
        """
        return cls.query.filter_by(id=classroom_id, is_active=True).first()
    
    @classmethod
    def get_by_code(cls, code: str) -> Optional['Classroom']:
        """
        الحصول على فصل دراسي حسب الرمز
        
        Args:
            code (str): رمز الفصل الدراسي
        
        Returns:
            Optional[Classroom]: الفصل الدراسي أو None إذا لم يتم العثور عليه
        """
        return cls.query.filter_by(code=code, is_active=True).first()
    
    @classmethod
    def get_by_teacher(cls, teacher_id: int) -> List['Classroom']:
        """
        الحصول على الفصول الدراسية حسب المعلم
        
        Args:
            teacher_id (int): معرف المعلم
        
        Returns:
            List[Classroom]: قائمة الفصول الدراسية
        """
        return cls.query.filter_by(teacher_id=teacher_id, is_active=True).all()
    
    def add_participant(self, user_id: int, role: str = 'student') -> 'ClassroomParticipant':
        """
        إضافة مشارك إلى الفصل الدراسي
        
        Args:
            user_id (int): معرف المستخدم
            role (str): دور المشارك (افتراضي: 'student')
        
        Returns:
            ClassroomParticipant: المشارك الجديد
        """
        from app.models.participant import ClassroomParticipant
        
        # التحقق مما إذا كان المستخدم مشاركًا بالفعل
        existing_participant = ClassroomParticipant.query.filter_by(
            classroom_id=self.id, user_id=user_id).first()
        
        if existing_participant:
            return existing_participant
        
        # إنشاء مشارك جديد
        participant = ClassroomParticipant(
            classroom_id=self.id,
            user_id=user_id,
            role=role
        )
        
        db.session.add(participant)
        return participant
    
    def remove_participant(self, user_id: int) -> bool:
        """
        إزالة مشارك من الفصل الدراسي
        
        Args:
            user_id (int): معرف المستخدم
        
        Returns:
            bool: ما إذا تمت إزالة المشارك بنجاح
        """
        from app.models.participant import ClassroomParticipant
        
        participant = ClassroomParticipant.query.filter_by(
            classroom_id=self.id, user_id=user_id).first()
        
        if participant:
            db.session.delete(participant)
            return True
        
        return False
    
    def get_participants(self) -> List['ClassroomParticipant']:
        """
        الحصول على المشاركين في الفصل الدراسي
        
        Returns:
            List[ClassroomParticipant]: قائمة المشاركين
        """
        from app.models.participant import ClassroomParticipant
        
        return ClassroomParticipant.query.filter_by(classroom_id=self.id).all()
    
    def get_students(self) -> List['ClassroomParticipant']:
        """
        الحصول على الطلاب في الفصل الدراسي
        
        Returns:
            List[ClassroomParticipant]: قائمة الطلاب
        """
        from app.models.participant import ClassroomParticipant
        
        return ClassroomParticipant.query.filter_by(
            classroom_id=self.id, role='student').all()
    
    def create_session(self, title: str, description: str = None) -> 'Session':
        """
        إنشاء جلسة جديدة في الفصل الدراسي
        
        Args:
            title (str): عنوان الجلسة
            description (str, optional): وصف الجلسة
        
        Returns:
            Session: الجلسة الجديدة
        """
        from app.models.session import Session
        
        session = Session(
            classroom_id=self.id,
            title=title,
            description=description
        )
        
        db.session.add(session)
        return session