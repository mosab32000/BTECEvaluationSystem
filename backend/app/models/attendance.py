"""
نموذج سجل الحضور والغياب في نظام تقييم BTEC
"""

import datetime
from backend.app.database import db

class Student(db.Model):
    """نموذج الطالب في نظام تقييم BTEC"""
    __tablename__ = 'student'
    
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    student_id_number = db.Column(db.String(20), unique=True)
    gender = db.Column(db.String(10))
    date_of_birth = db.Column(db.Date)
    grade_level = db.Column(db.String(20))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.datetime.utcnow)
    
    # العلاقات
    attendance_records = db.relationship('Attendance', backref='student', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f"<Student {self.id} {self.first_name} {self.last_name}>"

class Session(db.Model):
    """نموذج جلسة الدرس في نظام تقييم BTEC"""
    __tablename__ = 'session'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    session_date = db.Column(db.Date, nullable=False)
    session_time = db.Column(db.Time, nullable=False)
    description = db.Column(db.Text)
    status = db.Column(db.String(20), default='scheduled')  # scheduled, in-progress, completed, cancelled
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.datetime.utcnow)
    
    def __repr__(self):
        return f"<Session {self.id} {self.title}>"

class Attendance(db.Model):
    """نموذج سجل الحضور والغياب في نظام تقييم BTEC"""
    __tablename__ = 'attendance'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    session_id = db.Column(db.Integer, db.ForeignKey('session.id'))
    attendance_date = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(20), nullable=False)  # present, absent, late, excused
    notes = db.Column(db.Text)
    recorded_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.datetime.utcnow)
    
    def __repr__(self):
        return f"<Attendance {self.id} Student: {self.student_id} Date: {self.attendance_date}>"