"""
نموذج سجل الحضور في نظام تقييم BTEC
"""

from datetime import datetime

from app.extensions import db


class AttendanceLog(db.Model):
    """نموذج سجل الحضور في نظام تقييم BTEC."""
    __tablename__ = 'attendance_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    class_id = db.Column(db.Integer, db.ForeignKey('classes.id'))
    date = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(20), default='present')  # present, absent, late, excused
    recorded_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    note = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # العلاقات
    student = db.relationship('User', foreign_keys=[student_id], backref='attendance_logs')
    recorder = db.relationship('User', foreign_keys=[recorded_by], backref='recorded_attendance_logs')
    
    def __repr__(self):
        return f'<AttendanceLog {self.id} - Student {self.student_id} - Class {self.class_id}>'
    
    @property
    def is_present(self):
        """التحقق مما إذا كان الطالب حاضرًا.
        
        Returns:
            bool: True إذا كان الطالب حاضرًا، False خلاف ذلك
        """
        return self.status == 'present'
    
    @property
    def is_absent(self):
        """التحقق مما إذا كان الطالب غائبًا.
        
        Returns:
            bool: True إذا كان الطالب غائبًا، False خلاف ذلك
        """
        return self.status == 'absent'
    
    @property
    def is_late(self):
        """التحقق مما إذا كان الطالب متأخرًا.
        
        Returns:
            bool: True إذا كان الطالب متأخرًا، False خلاف ذلك
        """
        return self.status == 'late'
    
    @property
    def is_excused(self):
        """التحقق مما إذا كان غياب الطالب بعذر.
        
        Returns:
            bool: True إذا كان غياب الطالب بعذر، False خلاف ذلك
        """
        return self.status == 'excused'
    
    def mark_present(self, recorder_id=None):
        """تسجيل الطالب كحاضر.
        
        Args:
            recorder_id (int): معرف المستخدم الذي سجل الحضور
        """
        self.status = 'present'
        if recorder_id:
            self.recorded_by = recorder_id
        self.updated_at = datetime.utcnow()
    
    def mark_absent(self, recorder_id=None):
        """تسجيل الطالب كغائب.
        
        Args:
            recorder_id (int): معرف المستخدم الذي سجل الغياب
        """
        self.status = 'absent'
        if recorder_id:
            self.recorded_by = recorder_id
        self.updated_at = datetime.utcnow()
    
    def mark_late(self, recorder_id=None):
        """تسجيل الطالب كمتأخر.
        
        Args:
            recorder_id (int): معرف المستخدم الذي سجل التأخير
        """
        self.status = 'late'
        if recorder_id:
            self.recorded_by = recorder_id
        self.updated_at = datetime.utcnow()
    
    def mark_excused(self, recorder_id=None, note=None):
        """تسجيل غياب الطالب بعذر.
        
        Args:
            recorder_id (int): معرف المستخدم الذي سجل الغياب بعذر
            note (str): ملاحظة حول سبب الغياب بعذر
        """
        self.status = 'excused'
        if recorder_id:
            self.recorded_by = recorder_id
        if note:
            self.note = note
        self.updated_at = datetime.utcnow()
    
    def to_dict(self):
        """تحويل بيانات سجل الحضور إلى قاموس.
        
        Returns:
            dict: بيانات سجل الحضور
        """
        student_name = self.student.name if self.student else None
        recorder_name = self.recorder.name if self.recorder else None
        class_name = self.class_group.name if hasattr(self, 'class_group') and self.class_group else None
        
        return {
            'id': self.id,
            'student_id': self.student_id,
            'student_name': student_name,
            'class_id': self.class_id,
            'class_name': class_name,
            'date': self.date.isoformat() if self.date else None,
            'status': self.status,
            'recorded_by': self.recorded_by,
            'recorder_name': recorder_name,
            'note': self.note,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }