"""
نموذج معايير التقييم في نظام تقييم BTEC
"""
import json
from datetime import datetime

from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSONB

from app import db

class RubricTemplate(db.Model):
    """نموذج قالب معايير التقييم في نظام تقييم BTEC."""
    __tablename__ = 'rubric_template'
    
    # الأعمدة الأساسية
    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False)
    description = Column(Text)
    criteria_json = Column(JSONB)  # معايير التقييم (JSON)
    is_active = Column(Boolean, default=True)
    is_public = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # العلاقات
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship('User', back_populates='rubric_templates')
    evaluations = relationship('Evaluation', back_populates='rubric')
    
    def set_criteria(self, criteria):
        """تعيين معايير التقييم.
        
        Args:
            criteria: معايير التقييم (قائمة من القواميس)
        """
        self.criteria_json = criteria
    
    def get_criteria(self):
        """الحصول على معايير التقييم.
        
        Returns:
            list: قائمة من القواميس تمثل معايير التقييم
        """
        return self.criteria_json
    
    def calculate_max_score(self):
        """حساب أقصى درجة ممكنة لمعايير التقييم.
        
        Returns:
            float: أقصى درجة ممكنة
        """
        criteria = self.get_criteria()
        if not criteria:
            return 0
        
        max_score = 0
        for criterion in criteria:
            weight = criterion.get('weight', 0)
            levels = criterion.get('levels', [])
            if levels:
                max_level_score = max(level.get('score', 0) for level in levels)
                max_score += (weight / 100) * max_level_score
        
        return max_score
    
    def normalize_score(self, score):
        """تطبيع الدرجة لتكون بين 0 و 100.
        
        Args:
            score: الدرجة المراد تطبيعها
            
        Returns:
            float: الدرجة المطبّعة
        """
        max_score = self.calculate_max_score()
        if max_score == 0:
            return 0
        
        return (score / max_score) * 100
    
    def to_dict(self):
        """تحويل كائن قالب معايير التقييم إلى قاموس.
        
        Returns:
            dict: قاموس يمثل قالب معايير التقييم
        """
        rubric_dict = {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'criteria': self.get_criteria(),
            'max_score': self.calculate_max_score(),
            'is_active': self.is_active,
            'is_public': self.is_public,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'user_id': self.user_id
        }
        
        # إضافة بيانات المستخدم المنشئ
        if self.user:
            rubric_dict['user'] = {
                'id': self.user.id,
                'name': self.user.name,
                'email': self.user.email
            }
        
        return rubric_dict
    
    def __repr__(self):
        """تمثيل سلسلة نصية لقالب معايير التقييم.
        
        Returns:
            str: تمثيل سلسلة نصية
        """
        return f"<RubricTemplate {self.id} ({self.name})>"