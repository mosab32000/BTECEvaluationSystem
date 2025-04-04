"""
نموذج قالب معايير التقييم
"""

import json
import datetime
from app import db

class RubricTemplate(db.Model):
    """نموذج قالب معايير التقييم."""
    __tablename__ = 'rubric_template'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    content = db.Column(db.Text, nullable=False)  # معايير التقييم بتنسيق JSON
    is_default = db.Column(db.Boolean, default=False)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.datetime.utcnow)
    
    user = db.relationship('User', backref=db.backref('rubric_templates', lazy='dynamic'))
    
    def rubric_data(self):
        """استرجاع معايير التقييم كقاموس Python."""
        if not self.content:
            return {}
        
        try:
            return json.loads(self.content)
        except json.JSONDecodeError:
            return {}
    
    def set_rubric_data(self, data):
        """تعيين معايير التقييم من قاموس Python."""
        if isinstance(data, dict):
            self.content = json.dumps(data)
        elif isinstance(data, str):
            # التأكد من أن النص يمثل JSON صالح
            try:
                json.loads(data)
                self.content = data
            except json.JSONDecodeError:
                raise ValueError("معايير التقييم ليست بتنسيق JSON صالح")
        else:
            raise ValueError("معايير التقييم يجب أن تكون قاموس أو نص JSON")
    
    def to_dict(self):
        """تحويل بيانات قالب المعايير إلى قاموس."""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'content': self.rubric_data(),
            'is_default': self.is_default,
            'created_by': self.created_by,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<RubricTemplate {self.name}>'
