"""
نموذج مقاييس النظام في نظام تقييم BTEC
"""
from datetime import datetime
from app import db

class SystemMetrics(db.Model):
    """نموذج مقاييس النظام في نظام تقييم BTEC"""
    __tablename__ = 'system_metrics'
    
    id = db.Column(db.Integer, primary_key=True)
    user_count = db.Column(db.Integer, default=0)
    evaluation_count = db.Column(db.Integer, default=0)
    verification_count = db.Column(db.Integer, default=0)
    api_calls_count = db.Column(db.Integer, default=0)
    active_users_count = db.Column(db.Integer, default=0)
    average_response_time = db.Column(db.Float, default=0.0)
    error_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<SystemMetrics {self.id} at {self.created_at}>'
    
    def to_dict(self):
        """تحويل مقاييس النظام إلى قاموس"""
        return {
            'id': self.id,
            'user_count': self.user_count,
            'evaluation_count': self.evaluation_count,
            'verification_count': self.verification_count,
            'api_calls_count': self.api_calls_count,
            'active_users_count': self.active_users_count,
            'average_response_time': self.average_response_time,
            'error_count': self.error_count,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
