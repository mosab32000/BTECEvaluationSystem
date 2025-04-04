"""
نموذج معايير التقييم في نظام تقييم BTEC
"""
import datetime
import json
import uuid

from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import relationship

from app import db

class RubricTemplate(db.Model):
    """
    نموذج قالب معايير التقييم في نظام تقييم BTEC
    """
    __tablename__ = 'rubric_templates'
    
    id = Column(Integer, primary_key=True)
    uuid = Column(String(36), unique=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    criteria = Column(JSON, nullable=False)
    is_default = Column(Boolean, default=False)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    
    # العلاقات
    user = relationship('User')
    
    def set_criteria(self, criteria_list):
        """
        تعيين معايير التقييم
        
        Args:
            criteria_list: قائمة معايير التقييم
        """
        if isinstance(criteria_list, list):
            self.criteria = criteria_list
        elif isinstance(criteria_list, str):
            try:
                self.criteria = json.loads(criteria_list)
            except json.JSONDecodeError:
                self.criteria = [{'name': criteria_list, 'description': '', 'weight': 100}]
        else:
            self.criteria = []
    
    def get_criteria(self):
        """
        الحصول على معايير التقييم
        
        Returns:
            list: قائمة معايير التقييم
        """
        if not self.criteria:
            return []
        
        if isinstance(self.criteria, str):
            try:
                return json.loads(self.criteria)
            except json.JSONDecodeError:
                return []
        
        return self.criteria
    
    def get_weights(self):
        """
        الحصول على أوزان معايير التقييم
        
        Returns:
            dict: أوزان معايير التقييم
        """
        criteria = self.get_criteria()
        weights = {}
        
        for criterion in criteria:
            name = criterion.get('name', '')
            weight = criterion.get('weight', 0)
            if name:
                weights[name] = weight
        
        return weights
    
    def to_dict(self):
        """
        تحويل قالب معايير التقييم إلى قاموس
        
        Returns:
            dict: بيانات قالب معايير التقييم
        """
        return {
            'id': self.id,
            'uuid': self.uuid,
            'name': self.name,
            'description': self.description,
            'criteria': self.get_criteria(),
            'is_default': self.is_default,
            'user_id': self.user_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
    
    def to_json(self):
        """
        تحويل قالب معايير التقييم إلى سلسلة JSON
        
        Returns:
            str: سلسلة JSON لقالب معايير التقييم
        """
        return json.dumps(self.to_dict())
    
    def __repr__(self):
        """
        تمثيل قالب معايير التقييم كسلسلة نصية
        
        Returns:
            str: تمثيل قالب معايير التقييم
        """
        return f'<RubricTemplate {self.id}: {self.name}>'


class RubricCategory(db.Model):
    """
    نموذج فئة معايير التقييم في نظام تقييم BTEC
    """
    __tablename__ = 'rubric_categories'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    parent_id = Column(Integer, ForeignKey('rubric_categories.id', ondelete='SET NULL'), nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    # العلاقات
    parent = relationship('RubricCategory', remote_side=[id], backref='subcategories')
    criteria = relationship('RubricCriterion', back_populates='category')
    
    def to_dict(self, include_criteria=False):
        """
        تحويل فئة معايير التقييم إلى قاموس
        
        Args:
            include_criteria: ما إذا كان يجب تضمين معايير التقييم
            
        Returns:
            dict: بيانات فئة معايير التقييم
        """
        result = {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'parent_id': self.parent_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
        
        if include_criteria:
            result['criteria'] = [criterion.to_dict() for criterion in self.criteria]
            result['subcategories'] = [subcategory.to_dict(include_criteria=True) 
                                      for subcategory in self.subcategories]
        
        return result
    
    def __repr__(self):
        """
        تمثيل فئة معايير التقييم كسلسلة نصية
        
        Returns:
            str: تمثيل فئة معايير التقييم
        """
        return f'<RubricCategory {self.id}: {self.name}>'


class RubricCriterion(db.Model):
    """
    نموذج معيار التقييم في نظام تقييم BTEC
    """
    __tablename__ = 'rubric_criteria'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    weight = Column(Float, default=0)
    category_id = Column(Integer, ForeignKey('rubric_categories.id', ondelete='SET NULL'), nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    # مستويات التقييم
    levels = Column(JSON, nullable=True)  # [{"level": "ممتاز", "description": "...", "score": 10}, ...]
    
    # العلاقات
    category = relationship('RubricCategory', back_populates='criteria')
    
    def set_levels(self, levels_list):
        """
        تعيين مستويات التقييم
        
        Args:
            levels_list: قائمة مستويات التقييم
        """
        if isinstance(levels_list, list):
            self.levels = levels_list
        elif isinstance(levels_list, str):
            try:
                self.levels = json.loads(levels_list)
            except json.JSONDecodeError:
                self.levels = []
        else:
            self.levels = []
    
    def get_levels(self):
        """
        الحصول على مستويات التقييم
        
        Returns:
            list: قائمة مستويات التقييم
        """
        if not self.levels:
            return []
        
        if isinstance(self.levels, str):
            try:
                return json.loads(self.levels)
            except json.JSONDecodeError:
                return []
        
        return self.levels
    
    def to_dict(self):
        """
        تحويل معيار التقييم إلى قاموس
        
        Returns:
            dict: بيانات معيار التقييم
        """
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'weight': self.weight,
            'category_id': self.category_id,
            'levels': self.get_levels(),
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
    
    def __repr__(self):
        """
        تمثيل معيار التقييم كسلسلة نصية
        
        Returns:
            str: تمثيل معيار التقييم
        """
        return f'<RubricCriterion {self.id}: {self.name}>'


# جدول الربط بين قوالب معايير التقييم ومعايير التقييم
rubric_template_criteria = db.Table('rubric_template_criteria',
    Column('template_id', Integer, ForeignKey('rubric_templates.id', ondelete='CASCADE'), primary_key=True),
    Column('criterion_id', Integer, ForeignKey('rubric_criteria.id', ondelete='CASCADE'), primary_key=True),
    Column('weight', Float, default=0)
)