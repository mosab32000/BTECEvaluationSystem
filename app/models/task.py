"""
نموذج المهمة في نظام تقييم BTEC
"""

import datetime
import json
from typing import Dict, Any, Optional, List, Union

from flask import current_app
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.ext.mutable import MutableDict

from app.extensions import db
from app.security.encryption import encrypt, decrypt

class Task(db.Model):
    """نموذج المهمة في نظام تقييم BTEC"""
    __tablename__ = 'tasks'
    
    # حقول قاعدة البيانات
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    due_date = db.Column(db.DateTime)
    status = db.Column(db.String(20), default='pending')  # pending, in_progress, completed, cancelled
    priority = db.Column(db.String(20), default='medium')  # low, medium, high, urgent
    assigned_to = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    attachments = db.Column(db.JSON, default=[])
    category = db.Column(db.String(50))
    tags = db.Column(db.JSON, default=[])
    _secure_data = db.Column(db.Text, name='secure_data')  # بيانات مؤمنة
    
    # العلاقات
    # assigned_user = db.relationship('User', foreign_keys=[assigned_to], backref='assigned_tasks')
    # creator = db.relationship('User', foreign_keys=[created_by], backref='created_tasks')
    
    def __repr__(self):
        return f'<Task {self.title} - {self.status}>'
    
    @property
    def secure_data(self) -> Dict[str, Any]:
        """
        الحصول على البيانات المؤمنة بعد فك تشفيرها
        
        Returns:
            Dict[str, Any]: البيانات المؤمنة بعد فك تشفيرها
        """
        if not self._secure_data:
            return {}
        
        try:
            decrypted_data = decrypt(self._secure_data)
            if decrypted_data:
                return json.loads(decrypted_data)
        except Exception as e:
            current_app.logger.error(f"خطأ في فك تشفير البيانات المؤمنة: {str(e)}")
        
        return {}
    
    @secure_data.setter
    def secure_data(self, data: Dict[str, Any]) -> None:
        """
        تعيين البيانات المؤمنة مع تشفيرها
        
        Args:
            data (Dict[str, Any]): البيانات المراد تشفيرها وتخزينها
        """
        if not data:
            self._secure_data = None
            return
        
        try:
            json_data = json.dumps(data)
            self._secure_data = encrypt(json_data)
        except Exception as e:
            current_app.logger.error(f"خطأ في تشفير البيانات المؤمنة: {str(e)}")
            self._secure_data = None
    
    def to_dict(self) -> Dict[str, Any]:
        """
        تحويل المهمة إلى قاموس
        
        Returns:
            Dict[str, Any]: بيانات المهمة
        """
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'status': self.status,
            'priority': self.priority,
            'assigned_to': self.assigned_to,
            'created_by': self.created_by,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'attachments': self.attachments,
            'category': self.category,
            'tags': self.tags
        }
    
    @classmethod
    def get_by_id(cls, task_id: int) -> Optional['Task']:
        """
        الحصول على مهمة حسب المعرف
        
        Args:
            task_id (int): معرف المهمة
        
        Returns:
            Optional[Task]: المهمة أو None إذا لم يتم العثور عليها
        """
        return cls.query.filter_by(id=task_id).first()
    
    @classmethod
    def get_by_status(cls, status: str) -> List['Task']:
        """
        الحصول على المهام حسب الحالة
        
        Args:
            status (str): حالة المهام
        
        Returns:
            List[Task]: قائمة المهام
        """
        return cls.query.filter_by(status=status).all()
    
    @classmethod
    def get_by_assignee(cls, user_id: int) -> List['Task']:
        """
        الحصول على المهام المسندة إلى مستخدم معين
        
        Args:
            user_id (int): معرف المستخدم
        
        Returns:
            List[Task]: قائمة المهام
        """
        return cls.query.filter_by(assigned_to=user_id).all()
    
    @classmethod
    def get_by_creator(cls, user_id: int) -> List['Task']:
        """
        الحصول على المهام التي أنشأها مستخدم معين
        
        Args:
            user_id (int): معرف المستخدم
        
        Returns:
            List[Task]: قائمة المهام
        """
        return cls.query.filter_by(created_by=user_id).all()
    
    @classmethod
    def get_by_due_date_range(cls, start_date: datetime.datetime, end_date: datetime.datetime) -> List['Task']:
        """
        الحصول على المهام حسب نطاق تاريخ الاستحقاق
        
        Args:
            start_date (datetime.datetime): تاريخ البداية
            end_date (datetime.datetime): تاريخ النهاية
        
        Returns:
            List[Task]: قائمة المهام
        """
        return cls.query.filter(cls.due_date.between(start_date, end_date)).all()
    
    def update_status(self, new_status: str) -> None:
        """
        تحديث حالة المهمة
        
        Args:
            new_status (str): الحالة الجديدة
        """
        valid_statuses = ['pending', 'in_progress', 'completed', 'cancelled']
        if new_status not in valid_statuses:
            raise ValueError(f"الحالة '{new_status}' غير صالحة. الحالات الصالحة هي {', '.join(valid_statuses)}")
        
        self.status = new_status
        self.updated_at = datetime.datetime.utcnow()
    
    def update_priority(self, new_priority: str) -> None:
        """
        تحديث أولوية المهمة
        
        Args:
            new_priority (str): الأولوية الجديدة
        """
        valid_priorities = ['low', 'medium', 'high', 'urgent']
        if new_priority not in valid_priorities:
            raise ValueError(f"الأولوية '{new_priority}' غير صالحة. الأولويات الصالحة هي {', '.join(valid_priorities)}")
        
        self.priority = new_priority
        self.updated_at = datetime.datetime.utcnow()
    
    def assign_to(self, user_id: int) -> None:
        """
        إسناد المهمة إلى مستخدم
        
        Args:
            user_id (int): معرف المستخدم
        """
        self.assigned_to = user_id
        self.updated_at = datetime.datetime.utcnow()
    
    def mark_as_completed(self) -> None:
        """
        تحديد المهمة كمكتملة
        """
        self.status = 'completed'
        self.updated_at = datetime.datetime.utcnow()
    
    def add_attachment(self, attachment: Dict[str, str]) -> None:
        """
        إضافة مرفق إلى المهمة
        
        Args:
            attachment (Dict[str, str]): بيانات المرفق (file_name, file_path, file_type)
        """
        if not self.attachments:
            self.attachments = []
        
        self.attachments.append(attachment)
        self.updated_at = datetime.datetime.utcnow()
    
    def add_tag(self, tag: str) -> None:
        """
        إضافة وسم إلى المهمة
        
        Args:
            tag (str): الوسم
        """
        if not self.tags:
            self.tags = []
        
        if tag not in self.tags:
            self.tags.append(tag)
            self.updated_at = datetime.datetime.utcnow()
    
    def remove_tag(self, tag: str) -> None:
        """
        إزالة وسم من المهمة
        
        Args:
            tag (str): الوسم
        """
        if self.tags and tag in self.tags:
            self.tags.remove(tag)
            self.updated_at = datetime.datetime.utcnow()