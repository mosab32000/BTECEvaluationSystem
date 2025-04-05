"""
نموذج سجلات الحضور والغياب في نظام تقييم BTEC
"""

import datetime
import logging
from app import db

logger = logging.getLogger(__name__)

class Attendance(db.Model):
    """نموذج سجل الحضور والغياب في نظام تقييم BTEC."""
    __tablename__ = 'attendance'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    classroom_id = db.Column(db.Integer, db.ForeignKey('classrooms.id'), nullable=False)
    date = db.Column(db.Date, default=datetime.date.today, nullable=False)
    status = db.Column(db.String(20), default='present')  # present, absent, late, excused
    note = db.Column(db.Text)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    
    def __repr__(self):
        return f'<Attendance {self.student_id} - {self.date}>'
    
    def to_dict(self):
        """
        تحويل سجل الحضور إلى قاموس
        
        Returns:
            dict: بيانات سجل الحضور كقاموس
        """
        return {
            'id': self.id,
            'student_id': self.student_id,
            'classroom_id': self.classroom_id,
            'date': self.date.isoformat() if self.date else None,
            'status': self.status,
            'note': self.note,
            'created_by': self.created_by,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    @classmethod
    def get_by_id(cls, attendance_id):
        """
        الحصول على سجل حضور بواسطة المعرف
        
        Args:
            attendance_id (int): معرف سجل الحضور
            
        Returns:
            Attendance: كائن سجل الحضور أو None إذا لم يتم العثور عليه
        """
        return cls.query.get(attendance_id)
    
    @classmethod
    def get_by_student_and_date(cls, student_id, date):
        """
        الحصول على سجل حضور طالب في تاريخ معين
        
        Args:
            student_id (int): معرف الطالب
            date (date): التاريخ
            
        Returns:
            list: قائمة بكائنات سجلات الحضور للطالب في التاريخ المحدد
        """
        return cls.query.filter_by(student_id=student_id, date=date).all()
    
    @classmethod
    def get_by_classroom_and_date(cls, classroom_id, date):
        """
        الحصول على سجلات الحضور لفصل دراسي في تاريخ معين
        
        Args:
            classroom_id (int): معرف الفصل الدراسي
            date (date): التاريخ
            
        Returns:
            list: قائمة بكائنات سجلات الحضور للفصل الدراسي في التاريخ المحدد
        """
        return cls.query.filter_by(classroom_id=classroom_id, date=date).all()
    
    @classmethod
    def get_by_student_and_classroom(cls, student_id, classroom_id):
        """
        الحصول على سجلات حضور طالب في فصل دراسي معين
        
        Args:
            student_id (int): معرف الطالب
            classroom_id (int): معرف الفصل الدراسي
            
        Returns:
            list: قائمة بكائنات سجلات الحضور للطالب في الفصل الدراسي المحدد
        """
        return cls.query.filter_by(student_id=student_id, classroom_id=classroom_id).all()
    
    @classmethod
    def get_student_attendance_rate(cls, student_id, classroom_id):
        """
        الحصول على نسبة حضور طالب في فصل دراسي معين
        
        Args:
            student_id (int): معرف الطالب
            classroom_id (int): معرف الفصل الدراسي
            
        Returns:
            float: نسبة الحضور (0-100)
        """
        records = cls.query.filter_by(student_id=student_id, classroom_id=classroom_id).all()
        if not records:
            return 0
        
        total = len(records)
        present = len([r for r in records if r.status == 'present'])
        return (present / total) * 100
    
    def save(self):
        """
        حفظ سجل الحضور في قاعدة البيانات
        
        Returns:
            bool: نجاح العملية
        """
        try:
            db.session.add(self)
            db.session.commit()
            logger.info(f"تم حفظ سجل الحضور للطالب {self.student_id} في {self.date}")
            return True
        except Exception as e:
            db.session.rollback()
            logger.error(f"خطأ في حفظ سجل الحضور: {str(e)}")
            return False
    
    def delete(self):
        """
        حذف سجل الحضور من قاعدة البيانات
        
        Returns:
            bool: نجاح العملية
        """
        try:
            db.session.delete(self)
            db.session.commit()
            logger.info(f"تم حذف سجل الحضور للطالب {self.student_id} في {self.date}")
            return True
        except Exception as e:
            db.session.rollback()
            logger.error(f"خطأ في حذف سجل الحضور: {str(e)}")
            return False