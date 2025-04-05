"""
نموذج التقييم في نظام تقييم BTEC
"""
import uuid
from datetime import datetime

from app import db

class Evaluation(db.Model):
    """نموذج التقييم في نظام تقييم BTEC."""
    __tablename__ = 'evaluation'
    
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(36), default=lambda: str(uuid.uuid4()), unique=True)
    
    # معلومات المهمة
    title = db.Column(db.String(200))
    task_description = db.Column(db.Text, nullable=False)
    submission_text = db.Column(db.Text, nullable=False)
    
    # معلومات التقييم
    grade = db.Column(db.Float)  # الدرجة من 0 إلى 100
    feedback = db.Column(db.Text)
    strengths = db.Column(db.Text)  # نقاط القوة مفصولة بالفاصلة المنقوطة
    weaknesses = db.Column(db.Text)  # نقاط الضعف مفصولة بالفاصلة المنقوطة
    criteria_scores = db.Column(db.Text)  # JSON نصي يحتوي على درجات معايير التقييم
    
    # حالة التقييم
    status = db.Column(db.String(20), default='pending')  # pending, in_progress, completed, verified
    verified = db.Column(db.Boolean, default=False)
    verification_hash = db.Column(db.String(64))  # بصمة التحقق (للبلوكتشين)
    transaction_id = db.Column(db.String(100))  # معرف المعاملة (للبلوكتشين)
    
    # العلاقات
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    rubric_id = db.Column(db.Integer, db.ForeignKey('rubric.id'))
    
    # التوقيت
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    evaluated_at = db.Column(db.DateTime)
    verified_at = db.Column(db.DateTime)
    
    # خيارات إضافية
    is_ai_evaluated = db.Column(db.Boolean, default=False)
    language = db.Column(db.String(10), default='ar')  # ar, en
    
    def __repr__(self):
        return f'<Evaluation {self.id} - {self.title}>'
    
    def get_strengths_list(self):
        """الحصول على قائمة نقاط القوة"""
        if self.strengths:
            return [s.strip() for s in self.strengths.split(';')]
        return []
    
    def get_weaknesses_list(self):
        """الحصول على قائمة نقاط الضعف"""
        if self.weaknesses:
            return [w.strip() for w in self.weaknesses.split(';')]
        return []
    
    def get_criteria_scores_dict(self):
        """الحصول على قاموس درجات معايير التقييم"""
        import json
        try:
            return json.loads(self.criteria_scores or '{}')
        except:
            return {}
    
    def update_status(self):
        """تحديث حالة التقييم بناءً على المعلومات الحالية"""
        if self.verified:
            self.status = 'verified'
        elif self.grade is not None:
            self.status = 'completed'
        elif self.id:  # إذا تم حفظ التقييم، فهو قيد التقدم
            self.status = 'in_progress'
        else:
            self.status = 'pending'
    
    def to_dict(self):
        """تحويل التقييم إلى قاموس للواجهة البرمجية"""
        return {
            'id': self.id,
            'uuid': self.uuid,
            'title': self.title,
            'task_description': self.task_description,
            'submission_text': self.submission_text,
            'grade': self.grade,
            'feedback': self.feedback,
            'strengths': self.get_strengths_list(),
            'weaknesses': self.get_weaknesses_list(),
            'criteria_scores': self.get_criteria_scores_dict(),
            'status': self.status,
            'verified': self.verified,
            'verification_hash': self.verification_hash,
            'transaction_id': self.transaction_id,
            'user_id': self.user_id,
            'rubric_id': self.rubric_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'evaluated_at': self.evaluated_at.isoformat() if self.evaluated_at else None,
            'verified_at': self.verified_at.isoformat() if self.verified_at else None,
            'is_ai_evaluated': self.is_ai_evaluated,
            'language': self.language
        }