"""
نموذج الجلسة في نظام تقييم BTEC
"""

import datetime
from typing import Dict, Any, Optional, List

from app.extensions import db

class Session(db.Model):
    """نموذج الجلسة في نظام تقييم BTEC"""
    __tablename__ = 'sessions'
    
    # حقول قاعدة البيانات
    id = db.Column(db.Integer, primary_key=True)
    classroom_id = db.Column(db.Integer, db.ForeignKey('classrooms.id'), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    start_time = db.Column(db.DateTime)
    end_time = db.Column(db.DateTime)
    status = db.Column(db.String(20), default='scheduled')  # scheduled, active, completed, cancelled
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    
    # العلاقات
    # classroom = db.relationship('Classroom', backref='sessions')
    # attendances = db.relationship('Attendance', backref='session', lazy='dynamic')
    
    def __repr__(self):
        return f'<Session {self.title} - {self.status}>'
    
    def to_dict(self) -> Dict[str, Any]:
        """
        تحويل الجلسة إلى قاموس
        
        Returns:
            Dict[str, Any]: بيانات الجلسة
        """
        return {
            'id': self.id,
            'classroom_id': self.classroom_id,
            'title': self.title,
            'description': self.description,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    @classmethod
    def get_by_id(cls, session_id: int) -> Optional['Session']:
        """
        الحصول على جلسة حسب المعرف
        
        Args:
            session_id (int): معرف الجلسة
        
        Returns:
            Optional[Session]: الجلسة أو None إذا لم يتم العثور عليها
        """
        return cls.query.filter_by(id=session_id).first()
    
    @classmethod
    def get_by_classroom(cls, classroom_id: int) -> List['Session']:
        """
        الحصول على الجلسات حسب الفصل الدراسي
        
        Args:
            classroom_id (int): معرف الفصل الدراسي
        
        Returns:
            List[Session]: قائمة الجلسات
        """
        return cls.query.filter_by(classroom_id=classroom_id).all()
    
    @classmethod
    def get_active_sessions(cls) -> List['Session']:
        """
        الحصول على الجلسات النشطة
        
        Returns:
            List[Session]: قائمة الجلسات النشطة
        """
        return cls.query.filter_by(status='active').all()
    
    def start(self) -> None:
        """
        بدء الجلسة
        """
        self.status = 'active'
        self.start_time = datetime.datetime.utcnow()
        self.updated_at = datetime.datetime.utcnow()
    
    def end(self) -> None:
        """
        إنهاء الجلسة
        """
        self.status = 'completed'
        self.end_time = datetime.datetime.utcnow()
        self.updated_at = datetime.datetime.utcnow()
    
    def cancel(self) -> None:
        """
        إلغاء الجلسة
        """
        self.status = 'cancelled'
        self.updated_at = datetime.datetime.utcnow()
    
    def reschedule(self, new_start_time: datetime.datetime, new_end_time: Optional[datetime.datetime] = None) -> None:
        """
        إعادة جدولة الجلسة
        
        Args:
            new_start_time (datetime.datetime): وقت البدء الجديد
            new_end_time (Optional[datetime.datetime]): وقت الانتهاء الجديد
        """
        self.start_time = new_start_time
        if new_end_time:
            self.end_time = new_end_time
        self.status = 'scheduled'
        self.updated_at = datetime.datetime.utcnow()
    
    def add_attendance(self, participant_id: int, status: str = 'present') -> 'Attendance':
        """
        إضافة حضور للجلسة
        
        Args:
            participant_id (int): معرف المشارك
            status (str): حالة الحضور (افتراضي: 'present')
        
        Returns:
            Attendance: الحضور الجديد
        """
        from app.models.participant import Attendance
        
        # التحقق مما إذا كان المشارك لديه حضور بالفعل
        existing_attendance = Attendance.query.filter_by(
            session_id=self.id, participant_id=participant_id).first()
        
        if existing_attendance:
            existing_attendance.status = status
            if status == 'present' and not existing_attendance.check_in_time:
                existing_attendance.check_in_time = datetime.datetime.utcnow()
            return existing_attendance
        
        # إنشاء حضور جديد
        attendance = Attendance(
            session_id=self.id,
            participant_id=participant_id,
            status=status
        )
        
        if status == 'present':
            attendance.check_in_time = datetime.datetime.utcnow()
        
        db.session.add(attendance)
        return attendance
    
    def get_attendances(self) -> List['Attendance']:
        """
        الحصول على الحضور للجلسة
        
        Returns:
            List[Attendance]: قائمة الحضور
        """
        from app.models.participant import Attendance
        
        return Attendance.query.filter_by(session_id=self.id).all()
    
    def get_attendance_by_participant(self, participant_id: int) -> Optional['Attendance']:
        """
        الحصول على الحضور للمشارك في الجلسة
        
        Args:
            participant_id (int): معرف المشارك
        
        Returns:
            Optional[Attendance]: الحضور أو None إذا لم يتم العثور عليه
        """
        from app.models.participant import Attendance
        
        return Attendance.query.filter_by(
            session_id=self.id, participant_id=participant_id).first()
    
    def mark_all_absent(self) -> None:
        """
        تحديد جميع المشاركين كغائبين عن الجلسة
        """
        from app.models.participant import Attendance, ClassroomParticipant
        
        # الحصول على جميع المشاركين في الفصل الدراسي
        participants = ClassroomParticipant.query.filter_by(
            classroom_id=self.classroom_id, is_active=True).all()
        
        for participant in participants:
            attendance = self.get_attendance_by_participant(participant.id)
            
            if not attendance:
                # إنشاء حضور جديد
                attendance = Attendance(
                    session_id=self.id,
                    participant_id=participant.id,
                    status='absent'
                )
                db.session.add(attendance)
            elif attendance.status != 'absent' and not attendance.check_in_time:
                # تحديث الحضور الحالي
                attendance.status = 'absent'
                attendance.check_in_time = None
                attendance.check_out_time = None