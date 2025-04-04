"""
نموذج لتخزين مقاييس النظام
"""

import datetime
from app import db

class SystemMetrics(db.Model):
    """نموذج لتخزين مقاييس النظام."""
    __tablename__ = 'system_metrics'
    
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    api_calls = db.Column(db.Integer, default=0)
    evaluations_completed = db.Column(db.Integer, default=0)
    blockchain_verifications = db.Column(db.Integer, default=0)
    average_response_time = db.Column(db.Float)
    error_count = db.Column(db.Integer, default=0)
    active_users = db.Column(db.Integer, default=0)
    
    def to_dict(self):
        """تحويل بيانات المقاييس إلى قاموس."""
        return {
            'id': self.id,
            'timestamp': self.timestamp.isoformat(),
            'api_calls': self.api_calls,
            'evaluations_completed': self.evaluations_completed,
            'blockchain_verifications': self.blockchain_verifications,
            'average_response_time': self.average_response_time,
            'error_count': self.error_count,
            'active_users': self.active_users
        }
    
    def __repr__(self):
        return f'<SystemMetrics {self.timestamp}>'
