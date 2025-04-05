"""
نموذج معيار التقييم في نظام تقييم BTEC
"""

import datetime
from typing import Dict, Any, Optional, List

from app.extensions import db

class Rubric(db.Model):
    """نموذج معيار التقييم في نظام تقييم BTEC"""
    __tablename__ = 'rubrics'
    
    # حقول قاعدة البيانات
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    criteria = db.Column(db.JSON, default={})
    max_score = db.Column(db.Float, default=100)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    # العلاقات
    # creator = db.relationship('User', backref='created_rubrics')
    # evaluations = db.relationship('Evaluation', backref='rubric', lazy='dynamic')
    
    def __repr__(self):
        return f'<Rubric {self.name}>'
    
    def to_dict(self) -> Dict[str, Any]:
        """
        تحويل معيار التقييم إلى قاموس
        
        Returns:
            Dict[str, Any]: بيانات معيار التقييم
        """
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'criteria': self.criteria,
            'max_score': self.max_score,
            'created_by': self.created_by,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'is_active': self.is_active
        }
    
    @classmethod
    def get_by_id(cls, rubric_id: int) -> Optional['Rubric']:
        """
        الحصول على معيار تقييم حسب المعرف
        
        Args:
            rubric_id (int): معرف معيار التقييم
        
        Returns:
            Optional[Rubric]: معيار التقييم أو None إذا لم يتم العثور عليه
        """
        return cls.query.filter_by(id=rubric_id, is_active=True).first()
    
    @classmethod
    def get_by_creator(cls, creator_id: int) -> List['Rubric']:
        """
        الحصول على معايير التقييم حسب المنشئ
        
        Args:
            creator_id (int): معرف المنشئ
        
        Returns:
            List[Rubric]: قائمة معايير التقييم
        """
        return cls.query.filter_by(created_by=creator_id, is_active=True).all()
    
    @classmethod
    def get_active_rubrics(cls) -> List['Rubric']:
        """
        الحصول على معايير التقييم النشطة
        
        Returns:
            List[Rubric]: قائمة معايير التقييم النشطة
        """
        return cls.query.filter_by(is_active=True).all()
    
    def add_criterion(self, criterion_name: str, description: str, max_score: float, indicators: Dict[str, Any] = None) -> None:
        """
        إضافة معيار فرعي إلى معيار التقييم
        
        Args:
            criterion_name (str): اسم المعيار الفرعي
            description (str): وصف المعيار الفرعي
            max_score (float): الدرجة القصوى للمعيار الفرعي
            indicators (Dict[str, Any], optional): مؤشرات المعيار الفرعي
        """
        if self.criteria is None:
            self.criteria = {}
        
        self.criteria[criterion_name] = {
            'description': description,
            'max_score': max_score,
            'indicators': indicators or {}
        }
    
    def remove_criterion(self, criterion_name: str) -> bool:
        """
        إزالة معيار فرعي من معيار التقييم
        
        Args:
            criterion_name (str): اسم المعيار الفرعي
        
        Returns:
            bool: True إذا تمت الإزالة بنجاح، False إذا لم يتم العثور على المعيار الفرعي
        """
        if self.criteria and criterion_name in self.criteria:
            del self.criteria[criterion_name]
            return True
        return False
    
    def update_criterion(self, criterion_name: str, description: str = None, max_score: float = None, indicators: Dict[str, Any] = None) -> bool:
        """
        تحديث معيار فرعي في معيار التقييم
        
        Args:
            criterion_name (str): اسم المعيار الفرعي
            description (str, optional): وصف المعيار الفرعي الجديد
            max_score (float, optional): الدرجة القصوى الجديدة للمعيار الفرعي
            indicators (Dict[str, Any], optional): مؤشرات المعيار الفرعي الجديدة
        
        Returns:
            bool: True إذا تم التحديث بنجاح، False إذا لم يتم العثور على المعيار الفرعي
        """
        if not self.criteria or criterion_name not in self.criteria:
            return False
        
        if description is not None:
            self.criteria[criterion_name]['description'] = description
        
        if max_score is not None:
            self.criteria[criterion_name]['max_score'] = max_score
        
        if indicators is not None:
            self.criteria[criterion_name]['indicators'] = indicators
        
        return True
    
    def get_total_max_score(self) -> float:
        """
        حساب الدرجة القصوى الإجمالية للمعيار
        
        Returns:
            float: الدرجة القصوى الإجمالية
        """
        total = 0.0
        if self.criteria:
            for criterion in self.criteria.values():
                total += criterion.get('max_score', 0)
        return total
    
    def deactivate(self) -> None:
        """
        تعطيل معيار التقييم
        """
        self.is_active = False
    
    def activate(self) -> None:
        """
        تنشيط معيار التقييم
        """
        self.is_active = True
    
    def duplicate(self, new_name: str = None) -> 'Rubric':
        """
        إنشاء نسخة من معيار التقييم
        
        Args:
            new_name (str, optional): اسم النسخة الجديدة
        
        Returns:
            Rubric: النسخة الجديدة من معيار التقييم
        """
        name = new_name or f"{self.name} (نسخة)"
        
        # إنشاء نسخة جديدة
        new_rubric = Rubric(
            name=name,
            description=self.description,
            criteria=self.criteria.copy() if self.criteria else {},
            max_score=self.max_score,
            created_by=self.created_by
        )
        
        return new_rubric