"""
نموذج سجل التدقيق في نظام تقييم BTEC
"""
from datetime import datetime
from app import db

class AuditLog(db.Model):
    """نموذج سجل التدقيق في نظام تقييم BTEC"""
    __tablename__ = 'audit_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    event_type = db.Column(db.String(50), nullable=False, index=True)
    user = db.Column(db.String(120), nullable=False)
    details = db.Column(db.Text, nullable=True)
    ip_address = db.Column(db.String(50), nullable=True)
    user_agent = db.Column(db.String(256), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<AuditLog {self.id}: {self.event_type}>'
    
    def to_dict(self):
        """تحويل سجل التدقيق إلى قاموس"""
        return {
            'id': self.id,
            'event_type': self.event_type,
            'user': self.user,
            'details': self.details,
            'ip_address': self.ip_address,
            'user_agent': self.user_agent,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
