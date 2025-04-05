"""
نموذج المشارك في الفصل الدراسي في نظام تقييم BTEC
"""

import datetime
from typing import Dict, Any

from app.extensions import db

class ClassroomParticipant(db.Model):
    """نموذج المشارك في الفصل الدراسي في نظام تقييم BTEC"""
    __tablename__ = 'classroom_participants'
    
    # حقول قاعدة البيانات
    id = db.Column(db.Integer, primary_key=True)
    classroom_id = db.Column(db.Integer, db.ForeignKey('classrooms.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    role = db.Column(db.String(20), default='student')  # student, assistant
    joined_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    # العلاقات
    # classroom = db.relationship('Classroom', backref='participants')
    # user = db.relationship('User', backref='classroom_participations')
    # attendances = db.relationship('Attendance', backref='participant', lazy='dynamic')
    
    # إضافة قيد فريد لضمان أن المستخدم لا يمكن أن يكون مشاركًا في نفس الفصل الدراسي أكثر من مرة
    __table_args__ = (
        db.UniqueConstraint('classroom_id', 'user_id', name='uq_classroom_participant'),
    )
    
    def __repr__(self):
        return f'<ClassroomParticipant classroom_id={self.classroom_id} user_id={self.user_id} role={self.role}>'
    
    def to_dict(self) -> Dict[str, Any]:
        """
        تحويل المشارك في الفصل الدراسي إلى قاموس
        
        Returns:
            Dict[str, Any]: بيانات المشارك في الفصل الدراسي
        """
        return {
            'id': self.id,
            'classroom_id': self.classroom_id,
            'user_id': self.user_id,
            'role': self.role,
            'joined_at': self.joined_at.isoformat() if self.joined_at else None,
            'is_active': self.is_active
        }
    
    def deactivate(self) -> None:
        """
        إلغاء تنشيط المشارك في الفصل الدراسي
        """
        self.is_active = False
    
    def activate(self) -> None:
        """
        تنشيط المشارك في الفصل الدراسي
        """
        self.is_active = True
    
    def change_role(self, new_role: str) -> None:
        """
        تغيير دور المشارك في الفصل الدراسي
        
        Args:
            new_role (str): الدور الجديد (student, assistant)
        """
        if new_role not in ['student', 'assistant']:
            raise ValueError(f"الدور '{new_role}' غير صالح. الأدوار الصالحة هي 'student' و 'assistant'.")
        
        self.role = new_role

class Attendance(db.Model):
    """نموذج الحضور في نظام تقييم BTEC"""
    __tablename__ = 'attendances'
    
    # حقول قاعدة البيانات
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey('sessions.id'), nullable=False)
    participant_id = db.Column(db.Integer, db.ForeignKey('classroom_participants.id'), nullable=False)
    status = db.Column(db.String(20), default='present')  # present, absent, late, excused
    check_in_time = db.Column(db.DateTime)
    check_out_time = db.Column(db.DateTime)
    notes = db.Column(db.Text)
    
    # العلاقات
    # session = db.relationship('Session', backref='attendances')
    # participant = db.relationship('ClassroomParticipant', backref='attendances')
    
    # إضافة قيد فريد لضمان أن المشارك لا يمكن أن يكون له أكثر من حضور واحد لكل جلسة
    __table_args__ = (
        db.UniqueConstraint('session_id', 'participant_id', name='uq_session_participant'),
    )
    
    def __repr__(self):
        return f'<Attendance session_id={self.session_id} participant_id={self.participant_id} status={self.status}>'
    
    def to_dict(self) -> Dict[str, Any]:
        """
        تحويل الحضور إلى قاموس
        
        Returns:
            Dict[str, Any]: بيانات الحضور
        """
        return {
            'id': self.id,
            'session_id': self.session_id,
            'participant_id': self.participant_id,
            'status': self.status,
            'check_in_time': self.check_in_time.isoformat() if self.check_in_time else None,
            'check_out_time': self.check_out_time.isoformat() if self.check_out_time else None,
            'notes': self.notes
        }
    
    def check_in(self) -> None:
        """
        تسجيل وقت تسجيل الدخول
        """
        if not self.check_in_time:
            self.check_in_time = datetime.datetime.utcnow()
            if self.status == 'absent':
                self.status = 'present'
    
    def check_out(self) -> None:
        """
        تسجيل وقت تسجيل الخروج
        """
        if self.check_in_time and not self.check_out_time:
            self.check_out_time = datetime.datetime.utcnow()
    
    def mark_as_present(self) -> None:
        """
        تحديد الحضور كحاضر
        """
        self.status = 'present'
        if not self.check_in_time:
            self.check_in_time = datetime.datetime.utcnow()
    
    def mark_as_absent(self) -> None:
        """
        تحديد الحضور كغائب
        """
        self.status = 'absent'
        self.check_in_time = None
        self.check_out_time = None
    
    def mark_as_late(self) -> None:
        """
        تحديد الحضور كمتأخر
        """
        self.status = 'late'
        if not self.check_in_time:
            self.check_in_time = datetime.datetime.utcnow()
    
    def mark_as_excused(self) -> None:
        """
        تحديد الحضور كمعذور
        """
        self.status = 'excused'