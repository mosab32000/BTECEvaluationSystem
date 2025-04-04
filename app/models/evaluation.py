"""
نموذج التقييم في نظام تقييم BTEC
"""
from datetime import datetime
import json
from app import db

class Evaluation(db.Model):
    """نموذج التقييم في نظام تقييم BTEC"""
    __tablename__ = 'evaluations'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    content = db.Column(db.Text, nullable=False)
    rubric_id = db.Column(db.Integer, db.ForeignKey('rubrics.id'), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    result = db.Column(db.JSON, nullable=True)
    grade = db.Column(db.String(20), nullable=True)
    feedback = db.Column(db.Text, nullable=True)
    verification_hash = db.Column(db.String(128), nullable=True)
    verification_status = db.Column(db.Boolean, default=False)
    is_verified = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Evaluation {self.id}: {self.title}>'
    
    def to_dict(self):
        """تحويل التقييم إلى قاموس"""
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'content': self.content,
            'rubric_id': self.rubric_id,
            'user_id': self.user_id,
            'result': self.result,
            'grade': self.grade,
            'feedback': self.feedback,
            'verification_hash': self.verification_hash,
            'verification_status': self.verification_status,
            'is_verified': self.is_verified,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
