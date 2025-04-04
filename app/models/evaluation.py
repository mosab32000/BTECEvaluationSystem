"""
نموذج التقييم في نظام تقييم BTEC
"""

import json
import datetime
from app import db
from app.core.security import SecureVault

class Evaluation(db.Model):
    """نموذج التقييم في نظام تقييم BTEC."""
    __tablename__ = 'evaluation'
    
    id = db.Column(db.Integer, primary_key=True)
    task_encrypted = db.Column(db.Text, nullable=False)  # المهمة المشفرة
    grade = db.Column(db.String(100))  # الدرجة/التقييم الناتج من الذكاء الاصطناعي
    feedback = db.Column(db.Text)  # ملاحظات مفصلة
    grade_numerical = db.Column(db.Float)  # قيمة رقمية للدرجة (مثلاً 0-100)
    rubric_results = db.Column(db.Text)  # نتائج التقييم حسب المعايير بتنسيق JSON
    audit_hash = db.Column(db.String(66))  # رمز التحقق في البلوكتشين
    verification_status = db.Column(db.Boolean, default=False)  # حالة التحقق
    verification_timestamp = db.Column(db.DateTime)  # وقت التحقق الأخير
    submitted_at = db.Column(db.DateTime, index=True, default=datetime.datetime.utcnow)
    evaluated_at = db.Column(db.DateTime)  # وقت التقييم
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    
    submitter = db.relationship('User', backref=db.backref('evaluations', lazy='dynamic', cascade='all, delete-orphan'))
    
    def is_verified(self):
        """التحقق ما إذا كان التقييم مُتحقق منه."""
        return self.verification_status
    
    def rubric_data(self):
        """استرجاع نتائج التقييم كقاموس Python."""
        if not self.rubric_results:
            return {}
        
        try:
            return json.loads(self.rubric_results)
        except json.JSONDecodeError:
            return {}
    
    def set_rubric_data(self, data):
        """تعيين نتائج التقييم من قاموس Python."""
        if isinstance(data, dict):
            self.rubric_results = json.dumps(data)
        elif isinstance(data, str):
            # التأكد من أن النص يمثل JSON صالح
            try:
                json.loads(data)
                self.rubric_results = data
            except json.JSONDecodeError:
                raise ValueError("نتائج التقييم ليست بتنسيق JSON صالح")
        else:
            raise ValueError("نتائج التقييم يجب أن تكون قاموس أو نص JSON")
    
    def verify(self):
        """وضع علامة على التقييم كمُتحقق منه."""
        self.verification_status = True
        self.verification_timestamp = datetime.datetime.utcnow()
    
    def to_dict(self, include_task=False, vault=None):
        """تحويل بيانات التقييم إلى قاموس."""
        data = {
            'id': self.id,
            'grade': self.grade,
            'feedback': self.feedback,
            'grade_numerical': self.grade_numerical,
            'rubric_results': self.rubric_data(),
            'audit_hash': self.audit_hash,
            'verification_status': self.verification_status,
            'verification_timestamp': self.verification_timestamp.isoformat() if self.verification_timestamp else None,
            'submitted_at': self.submitted_at.isoformat(),
            'evaluated_at': self.evaluated_at.isoformat() if self.evaluated_at else None,
            'user_id': self.user_id
        }
        
        # فك تشفير المهمة إذا طُلب ذلك
        if include_task and vault:
            try:
                data['task'] = vault.decrypt(self.task_encrypted)
            except Exception:
                data['task'] = None
        
        return data
    
    def __repr__(self):
        return f'<Evaluation {self.id}>'
