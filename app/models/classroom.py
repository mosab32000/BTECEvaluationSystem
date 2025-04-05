"""
نموذج الفصول الدراسية في نظام تقييم BTEC
"""

import datetime
import logging
from app import db

logger = logging.getLogger(__name__)

class Classroom(db.Model):
    """نموذج الفصل الدراسي في نظام تقييم BTEC."""
    __tablename__ = 'classrooms'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    schedule = db.Column(db.String(100))  # مثال: "الأحد، الثلاثاء، الخميس 10:00-11:30"
    teacher_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    course_code = db.Column(db.String(20))
    max_students = db.Column(db.Integer, default=30)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    
    def __repr__(self):
        return f'<Classroom {self.name}>'
    
    def to_dict(self):
        """
        تحويل الفصل الدراسي إلى قاموس
        
        Returns:
            dict: بيانات الفصل الدراسي كقاموس
        """
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'schedule': self.schedule,
            'teacher_id': self.teacher_id,
            'course_code': self.course_code,
            'max_students': self.max_students,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    @classmethod
    def get_by_id(cls, classroom_id):
        """
        الحصول على فصل دراسي بواسطة المعرف
        
        Args:
            classroom_id (int): معرف الفصل الدراسي
            
        Returns:
            Classroom: كائن الفصل الدراسي أو None إذا لم يتم العثور عليه
        """
        return cls.query.get(classroom_id)
    
    @classmethod
    def get_by_teacher(cls, teacher_id):
        """
        الحصول على الفصول الدراسية لمدرس معين
        
        Args:
            teacher_id (int): معرف المدرس
            
        Returns:
            list: قائمة بكائنات الفصول الدراسية للمدرس
        """
        return cls.query.filter_by(teacher_id=teacher_id).all()
    
    @classmethod
    def get_active(cls):
        """
        الحصول على الفصول الدراسية النشطة
        
        Returns:
            list: قائمة بكائنات الفصول الدراسية النشطة
        """
        return cls.query.filter_by(is_active=True).all()
    
    @classmethod
    def get_all(cls):
        """
        الحصول على جميع الفصول الدراسية
        
        Returns:
            list: قائمة بجميع كائنات الفصول الدراسية
        """
        return cls.query.all()
    
    def save(self):
        """
        حفظ الفصل الدراسي في قاعدة البيانات
        
        Returns:
            bool: نجاح العملية
        """
        try:
            db.session.add(self)
            db.session.commit()
            logger.info(f"تم حفظ الفصل الدراسي: {self.name}")
            return True
        except Exception as e:
            db.session.rollback()
            logger.error(f"خطأ في حفظ الفصل الدراسي: {str(e)}")
            return False
    
    def delete(self):
        """
        حذف الفصل الدراسي من قاعدة البيانات
        
        Returns:
            bool: نجاح العملية
        """
        try:
            db.session.delete(self)
            db.session.commit()
            logger.info(f"تم حذف الفصل الدراسي: {self.name}")
            return True
        except Exception as e:
            db.session.rollback()
            logger.error(f"خطأ في حذف الفصل الدراسي: {str(e)}")
            return False