"""
نموذج الحصص التفاعلية في نظام تقييم BTEC
"""

import datetime
import logging
from app import db

logger = logging.getLogger(__name__)

class Session(db.Model):
    """نموذج الحصة التفاعلية في نظام تقييم BTEC."""
    __tablename__ = 'sessions'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    classroom_id = db.Column(db.Integer, db.ForeignKey('classrooms.id'), nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
    session_type = db.Column(db.String(50), default='live')  # live, recorded, hybrid
    session_url = db.Column(db.String(255))  # رابط الاجتماع أو البث
    meeting_id = db.Column(db.String(100))  # معرف الاجتماع
    password = db.Column(db.String(100))  # كلمة مرور الاجتماع (إن وجدت)
    materials = db.Column(db.JSON, default={})  # مواد الحصة الدراسية
    status = db.Column(db.String(20), default='scheduled')  # scheduled, active, completed, cancelled
    recording_url = db.Column(db.String(255))  # رابط التسجيل (إن وجد)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    
    def __repr__(self):
        return f'<Session {self.title}>'
    
    def to_dict(self):
        """
        تحويل الحصة التفاعلية إلى قاموس
        
        Returns:
            dict: بيانات الحصة التفاعلية كقاموس
        """
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'classroom_id': self.classroom_id,
            'teacher_id': self.teacher_id,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'session_type': self.session_type,
            'session_url': self.session_url,
            'meeting_id': self.meeting_id,
            'password': None,  # لا نرسل كلمة المرور في الاستجابة API
            'materials': self.materials,
            'status': self.status,
            'recording_url': self.recording_url,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    @classmethod
    def get_by_id(cls, session_id):
        """
        الحصول على حصة تفاعلية بواسطة المعرف
        
        Args:
            session_id (int): معرف الحصة التفاعلية
            
        Returns:
            Session: كائن الحصة التفاعلية أو None إذا لم يتم العثور عليه
        """
        return cls.query.get(session_id)
    
    @classmethod
    def get_by_classroom(cls, classroom_id):
        """
        الحصول على الحصص التفاعلية لفصل دراسي معين
        
        Args:
            classroom_id (int): معرف الفصل الدراسي
            
        Returns:
            list: قائمة بكائنات الحصص التفاعلية للفصل الدراسي
        """
        return cls.query.filter_by(classroom_id=classroom_id).all()
    
    @classmethod
    def get_by_teacher(cls, teacher_id):
        """
        الحصول على الحصص التفاعلية لمدرس معين
        
        Args:
            teacher_id (int): معرف المدرس
            
        Returns:
            list: قائمة بكائنات الحصص التفاعلية للمدرس
        """
        return cls.query.filter_by(teacher_id=teacher_id).all()
    
    @classmethod
    def get_active(cls):
        """
        الحصول على الحصص التفاعلية النشطة حاليًا
        
        Returns:
            list: قائمة بكائنات الحصص التفاعلية النشطة
        """
        now = datetime.datetime.utcnow()
        return cls.query.filter(cls.start_time <= now, cls.end_time >= now, cls.status == 'active').all()
    
    @classmethod
    def get_upcoming(cls, hours=24):
        """
        الحصول على الحصص التفاعلية القادمة
        
        Args:
            hours (int): عدد الساعات القادمة للبحث
            
        Returns:
            list: قائمة بكائنات الحصص التفاعلية القادمة
        """
        now = datetime.datetime.utcnow()
        end_time = now + datetime.timedelta(hours=hours)
        return cls.query.filter(cls.start_time >= now, cls.start_time <= end_time, cls.status == 'scheduled').all()
    
    def save(self):
        """
        حفظ الحصة التفاعلية في قاعدة البيانات
        
        Returns:
            bool: نجاح العملية
        """
        try:
            db.session.add(self)
            db.session.commit()
            logger.info(f"تم حفظ الحصة التفاعلية: {self.title}")
            return True
        except Exception as e:
            db.session.rollback()
            logger.error(f"خطأ في حفظ الحصة التفاعلية: {str(e)}")
            return False
    
    def delete(self):
        """
        حذف الحصة التفاعلية من قاعدة البيانات
        
        Returns:
            bool: نجاح العملية
        """
        try:
            db.session.delete(self)
            db.session.commit()
            logger.info(f"تم حذف الحصة التفاعلية: {self.title}")
            return True
        except Exception as e:
            db.session.rollback()
            logger.error(f"خطأ في حذف الحصة التفاعلية: {str(e)}")
            return False