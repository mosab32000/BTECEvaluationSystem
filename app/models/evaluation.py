"""
نموذج التقييم في نظام تقييم BTEC
"""

from datetime import datetime

from app.extensions import db


class Evaluation(db.Model):
    """نموذج التقييم في نظام تقييم BTEC."""
    __tablename__ = 'evaluations'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    assignment_id = db.Column(db.String(50))
    rubric_id = db.Column(db.Integer, db.ForeignKey('rubrics.id'))
    submission_text = db.Column(db.Text)
    evaluation_result = db.Column(db.JSON, default={})
    score = db.Column(db.Float)
    ai_score = db.Column(db.Float)
    evaluator_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    evaluator_comments = db.Column(db.Text)
    status = db.Column(db.String(20), default='pending')  # pending, in_progress, completed, rejected
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # العلاقات
    student = db.relationship('User', foreign_keys=[student_id], backref='student_evaluations')
    evaluator = db.relationship('User', foreign_keys=[evaluator_id], backref='evaluator_evaluations')
    rubric = db.relationship('Rubric', backref='evaluations')
    blockchain_verifications = db.relationship('BlockchainVerification', backref='evaluation', lazy='dynamic')
    
    def __repr__(self):
        return f'<Evaluation {self.id} - Student {self.student_id} - Assignment {self.assignment_id}>'
    
    def evaluate_criterion(self, criterion_name, level, score, comment=None):
        """
        تقييم معيار محدد
        
        Args:
            criterion_name (str): اسم المعيار
            level (str): مستوى التقييم
            score (float): الدرجة
            comment (str, optional): تعليق على التقييم
        
        Returns:
            bool: True إذا تم التقييم بنجاح، False خلاف ذلك
        """
        if not self.evaluation_result:
            self.evaluation_result = {}
        
        if criterion_name not in self.evaluation_result:
            self.evaluation_result[criterion_name] = {}
        
        self.evaluation_result[criterion_name]['level'] = level
        self.evaluation_result[criterion_name]['score'] = score
        
        if comment:
            self.evaluation_result[criterion_name]['comment'] = comment
        
        return True
    
    def calculate_total_score(self):
        """
        حساب الدرجة الإجمالية بناءً على تقييم المعايير والأوزان في معيار التقييم
        
        Returns:
            float: الدرجة الإجمالية
        """
        if not self.rubric or not self.evaluation_result:
            return 0
        
        total_score = 0
        total_weight = 0
        
        for criterion_name, criterion_data in self.rubric.criteria.items():
            weight = criterion_data.get('weight', 0)
            
            if criterion_name in self.evaluation_result:
                score = self.evaluation_result[criterion_name].get('score', 0)
                total_score += score * weight
                total_weight += weight
        
        if total_weight == 0:
            return 0
        
        # تطبيع الدرجة النهائية على مقياس max_score
        normalized_score = (total_score / total_weight) * self.rubric.max_score
        
        # تحديث قيمة score
        self.score = normalized_score
        
        return normalized_score
    
    def mark_as_completed(self):
        """
        تعيين حالة التقييم كمكتمل
        
        Returns:
            bool: True إذا تم تحديث الحالة بنجاح، False خلاف ذلك
        """
        self.status = 'completed'
        return True
    
    def mark_as_rejected(self):
        """
        تعيين حالة التقييم كمرفوض
        
        Returns:
            bool: True إذا تم تحديث الحالة بنجاح، False خلاف ذلك
        """
        self.status = 'rejected'
        return True
    
    def mark_as_in_progress(self):
        """
        تعيين حالة التقييم كقيد التنفيذ
        
        Returns:
            bool: True إذا تم تحديث الحالة بنجاح، False خلاف ذلك
        """
        self.status = 'in_progress'
        return True
    
    def to_dict(self):
        """
        تحويل بيانات التقييم إلى قاموس
        
        Returns:
            dict: بيانات التقييم
        """
        return {
            'id': self.id,
            'student_id': self.student_id,
            'student_name': self.student.name if self.student else None,
            'assignment_id': self.assignment_id,
            'rubric_id': self.rubric_id,
            'rubric_name': self.rubric.name if self.rubric else None,
            'submission_text': self.submission_text,
            'evaluation_result': self.evaluation_result,
            'score': self.score,
            'ai_score': self.ai_score,
            'evaluator_id': self.evaluator_id,
            'evaluator_name': self.evaluator.name if self.evaluator else None,
            'evaluator_comments': self.evaluator_comments,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'blockchain_verified': any(v.verified for v in self.blockchain_verifications)
        }