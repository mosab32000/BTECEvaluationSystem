"""
نموذج المشاركين في الحصص التفاعلية في نظام تقييم BTEC
"""

import datetime
import logging
from app import db

logger = logging.getLogger(__name__)

class Participant(db.Model):
    """نموذج المشارك في الحصة التفاعلية في نظام تقييم BTEC."""
    __tablename__ = 'participants'
    
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey('sessions.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    join_time = db.Column(db.DateTime)
    leave_time = db.Column(db.DateTime)
    attendance_status = db.Column(db.String(20), default='pending')  # pending, present, absent, late
    participation_score = db.Column(db.Float)  # درجة المشاركة (0-10)
    participation_notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    
    # قيد فريد للتأكد من أن المستخدم لا يتم تسجيله مرتين في نفس الحصة
    __table_args__ = (db.UniqueConstraint('session_id', 'user_id', name='uq_participant_session'),)
    
    def __repr__(self):
        return f'<Participant {self.user_id} in Session {self.session_id}>'
    
    def to_dict(self):
        """
        تحويل المشارك إلى قاموس
        
        Returns:
            dict: بيانات المشارك كقاموس
        """
        return {
            'id': self.id,
            'session_id': self.session_id,
            'user_id': self.user_id,
            'join_time': self.join_time.isoformat() if self.join_time else None,
            'leave_time': self.leave_time.isoformat() if self.leave_time else None,
            'attendance_status': self.attendance_status,
            'participation_score': self.participation_score,
            'participation_notes': self.participation_notes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    @classmethod
    def get_by_id(cls, participant_id):
        """
        الحصول على مشارك بواسطة المعرف
        
        Args:
            participant_id (int): معرف المشارك
            
        Returns:
            Participant: كائن المشارك أو None إذا لم يتم العثور عليه
        """
        return cls.query.get(participant_id)
    
    @classmethod
    def get_by_session_and_user(cls, session_id, user_id):
        """
        الحصول على مشارك بواسطة معرف الحصة ومعرف المستخدم
        
        Args:
            session_id (int): معرف الحصة
            user_id (int): معرف المستخدم
            
        Returns:
            Participant: كائن المشارك أو None إذا لم يتم العثور عليه
        """
        return cls.query.filter_by(session_id=session_id, user_id=user_id).first()
    
    @classmethod
    def get_by_session(cls, session_id):
        """
        الحصول على جميع المشاركين في حصة معينة
        
        Args:
            session_id (int): معرف الحصة
            
        Returns:
            list: قائمة بكائنات المشاركين في الحصة
        """
        return cls.query.filter_by(session_id=session_id).all()
    
    @classmethod
    def get_by_user(cls, user_id):
        """
        الحصول على جميع مشاركات مستخدم معين
        
        Args:
            user_id (int): معرف المستخدم
            
        Returns:
            list: قائمة بكائنات مشاركات المستخدم
        """
        return cls.query.filter_by(user_id=user_id).all()
    
    def save(self):
        """
        حفظ المشارك في قاعدة البيانات
        
        Returns:
            bool: نجاح العملية
        """
        try:
            db.session.add(self)
            db.session.commit()
            logger.info(f"تم حفظ المشارك: المستخدم {self.user_id} في الحصة {self.session_id}")
            return True
        except Exception as e:
            db.session.rollback()
            logger.error(f"خطأ في حفظ المشارك: {str(e)}")
            return False
    
    def delete(self):
        """
        حذف المشارك من قاعدة البيانات
        
        Returns:
            bool: نجاح العملية
        """
        try:
            db.session.delete(self)
            db.session.commit()
            logger.info(f"تم حذف المشارك: المستخدم {self.user_id} من الحصة {self.session_id}")
            return True
        except Exception as e:
            db.session.rollback()
            logger.error(f"خطأ في حذف المشارك: {str(e)}")
            return False