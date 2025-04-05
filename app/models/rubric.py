"""
نموذج معيار التقييم في نظام تقييم BTEC
"""

from datetime import datetime

from app.extensions import db


class Rubric(db.Model):
    """نموذج معيار التقييم في نظام تقييم BTEC."""
    __tablename__ = 'rubrics'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    criteria = db.Column(db.JSON, default={})
    max_score = db.Column(db.Float, default=100)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # العلاقات
    creator = db.relationship('User', backref='created_rubrics')
    
    def __repr__(self):
        return f'<Rubric {self.id} - {self.name}>'
    
    def add_criterion(self, name, description, weight, levels):
        """
        إضافة معيار جديد إلى معيار التقييم
        
        Args:
            name (str): اسم المعيار
            description (str): وصف المعيار
            weight (float): وزن المعيار من إجمالي التقييم (0-100)
            levels (dict): مستويات التقييم للمعيار (مثال: {"مستوى 1": "وصف"، "مستوى 2": "وصف"})
        
        Returns:
            bool: True إذا تمت الإضافة بنجاح، False خلاف ذلك
        """
        if not self.criteria:
            self.criteria = {}
        
        # التحقق من عدم وجود معيار بنفس الاسم
        if name in self.criteria:
            return False
        
        self.criteria[name] = {
            'description': description,
            'weight': weight,
            'levels': levels
        }
        
        return True
    
    def update_criterion(self, name, **kwargs):
        """
        تحديث معيار موجود
        
        Args:
            name (str): اسم المعيار
            **kwargs: القيم المراد تحديثها (description, weight, levels)
        
        Returns:
            bool: True إذا تم التحديث بنجاح، False خلاف ذلك
        """
        if not self.criteria or name not in self.criteria:
            return False
        
        for key, value in kwargs.items():
            if key in ['description', 'weight', 'levels']:
                self.criteria[name][key] = value
        
        return True
    
    def remove_criterion(self, name):
        """
        إزالة معيار من معيار التقييم
        
        Args:
            name (str): اسم المعيار
        
        Returns:
            bool: True إذا تمت الإزالة بنجاح، False خلاف ذلك
        """
        if not self.criteria or name not in self.criteria:
            return False
        
        del self.criteria[name]
        return True
    
    def get_criteria_list(self):
        """
        الحصول على قائمة بجميع المعايير
        
        Returns:
            list: قائمة بجميع المعايير
        """
        if not self.criteria:
            return []
        
        return [{
            'name': name,
            'description': data['description'],
            'weight': data['weight'],
            'levels': data['levels']
        } for name, data in self.criteria.items()]
    
    def to_dict(self):
        """
        تحويل بيانات معيار التقييم إلى قاموس
        
        Returns:
            dict: بيانات معيار التقييم
        """
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'criteria': self.criteria,
            'max_score': self.max_score,
            'created_by': self.created_by,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }