"""
نموذج معايير التقييم في نظام تقييم BTEC
"""
from datetime import datetime
from app import db

class Rubric(db.Model):
    """نموذج معايير التقييم في نظام تقييم BTEC"""
    __tablename__ = 'rubrics'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    criteria = db.Column(db.JSON, nullable=False)
    is_default = db.Column(db.Boolean, default=False)
    creator_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # العلاقات
    evaluations = db.relationship('Evaluation', backref='rubric', lazy='dynamic')
    
    def __repr__(self):
        return f'<Rubric {self.id}: {self.name}>'
    
    def to_dict(self):
        """تحويل معيار التقييم إلى قاموس"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'criteria': self.criteria,
            'is_default': self.is_default,
            'creator_id': self.creator_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
