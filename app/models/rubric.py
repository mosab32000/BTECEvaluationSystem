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
    evaluations = db.relationship('Evaluation', backref='rubric', lazy='dynamic')
    
    def __repr__(self):
        return f'<Rubric {self.name}>'
    
    def get_criteria_normalized(self):
        """الحصول على معايير التقييم مع تطبيع الأوزان.
        
        Returns:
            dict: معايير التقييم بعد تطبيع الأوزان
        """
        if not self.criteria:
            return {}
        
        total_weight = sum(criterion.get('weight', 0) for criterion in self.criteria.values())
        
        if total_weight == 0:
            return self.criteria
        
        normalized_criteria = {}
        for key, criterion in self.criteria.items():
            normalized_criteria[key] = criterion.copy()
            normalized_criteria[key]['normalized_weight'] = criterion.get('weight', 0) / total_weight
            
        return normalized_criteria
    
    def calculate_score(self, criteria_scores):
        """حساب الدرجة الإجمالية بناءً على درجات المعايير.
        
        Args:
            criteria_scores (dict): درجات المعايير (الاسم: الدرجة)
            
        Returns:
            float: الدرجة الإجمالية
        """
        if not self.criteria or not criteria_scores:
            return 0
        
        normalized_criteria = self.get_criteria_normalized()
        
        total_score = 0
        for key, criterion in normalized_criteria.items():
            if key in criteria_scores:
                # حساب النسبة المئوية من الدرجة القصوى للمعيار
                max_criterion_score = criterion.get('max_score', 100)
                criterion_score = criteria_scores[key]
                
                if max_criterion_score > 0:
                    score_percentage = criterion_score / max_criterion_score
                else:
                    score_percentage = 0
                
                # إضافة الدرجة المرجحة إلى المجموع
                total_score += score_percentage * criterion.get('normalized_weight', 0) * self.max_score
        
        return round(total_score, 2)
    
    def to_dict(self):
        """تحويل بيانات معيار التقييم إلى قاموس.
        
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
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }