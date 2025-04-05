"""
نموذج التقييم في نظام تقييم BTEC
"""

import datetime
from typing import Dict, Any, Optional, List

from app.extensions import db

class Evaluation(db.Model):
    """نموذج التقييم في نظام تقييم BTEC"""
    __tablename__ = 'evaluations'
    
    # حقول قاعدة البيانات
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
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    
    # العلاقات
    # student = db.relationship('User', foreign_keys=[student_id], backref='evaluations_submitted')
    # evaluator = db.relationship('User', foreign_keys=[evaluator_id], backref='evaluations_evaluated')
    # rubric = db.relationship('Rubric', backref='evaluations')
    # blockchain_verification = db.relationship('BlockchainVerification', backref='evaluation', uselist=False)
    
    def __repr__(self):
        return f'<Evaluation {self.id} - {self.status}>'
    
    def to_dict(self) -> Dict[str, Any]:
        """
        تحويل التقييم إلى قاموس
        
        Returns:
            Dict[str, Any]: بيانات التقييم
        """
        return {
            'id': self.id,
            'student_id': self.student_id,
            'assignment_id': self.assignment_id,
            'rubric_id': self.rubric_id,
            'submission_text': self.submission_text,
            'evaluation_result': self.evaluation_result,
            'score': self.score,
            'ai_score': self.ai_score,
            'evaluator_id': self.evaluator_id,
            'evaluator_comments': self.evaluator_comments,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    @classmethod
    def get_by_id(cls, evaluation_id: int) -> Optional['Evaluation']:
        """
        الحصول على تقييم حسب المعرف
        
        Args:
            evaluation_id (int): معرف التقييم
        
        Returns:
            Optional[Evaluation]: التقييم أو None إذا لم يتم العثور عليه
        """
        return cls.query.filter_by(id=evaluation_id).first()
    
    @classmethod
    def get_by_student(cls, student_id: int) -> List['Evaluation']:
        """
        الحصول على التقييمات حسب الطالب
        
        Args:
            student_id (int): معرف الطالب
        
        Returns:
            List[Evaluation]: قائمة التقييمات
        """
        return cls.query.filter_by(student_id=student_id).all()
    
    @classmethod
    def get_by_evaluator(cls, evaluator_id: int) -> List['Evaluation']:
        """
        الحصول على التقييمات حسب المقيم
        
        Args:
            evaluator_id (int): معرف المقيم
        
        Returns:
            List[Evaluation]: قائمة التقييمات
        """
        return cls.query.filter_by(evaluator_id=evaluator_id).all()
    
    @classmethod
    def get_by_status(cls, status: str) -> List['Evaluation']:
        """
        الحصول على التقييمات حسب الحالة
        
        Args:
            status (str): حالة التقييم
        
        Returns:
            List[Evaluation]: قائمة التقييمات
        """
        return cls.query.filter_by(status=status).all()
    
    def calculate_score(self) -> float:
        """
        حساب درجة التقييم
        
        Returns:
            float: درجة التقييم
        """
        score = 0.0
        total_possible = 0.0
        
        if not self.evaluation_result:
            return 0.0
        
        for criterion_name, criterion_data in self.evaluation_result.items():
            if 'score' in criterion_data and 'max_score' in criterion_data:
                score += criterion_data['score']
                total_possible += criterion_data['max_score']
        
        if total_possible == 0:
            return 0.0
        
        return (score / total_possible) * 100
    
    def update_score(self) -> None:
        """
        تحديث درجة التقييم
        """
        self.score = self.calculate_score()
    
    def add_criterion_evaluation(self, criterion_name: str, score: float, max_score: float, feedback: str) -> None:
        """
        إضافة تقييم لمعيار
        
        Args:
            criterion_name (str): اسم المعيار
            score (float): الدرجة
            max_score (float): الدرجة القصوى
            feedback (str): التعليق
        """
        if self.evaluation_result is None:
            self.evaluation_result = {}
        
        self.evaluation_result[criterion_name] = {
            'score': score,
            'max_score': max_score,
            'feedback': feedback
        }
        
        # تحديث الدرجة الكلية
        self.update_score()
    
    def mark_as_complete(self) -> None:
        """
        تحديد التقييم كمكتمل
        """
        self.status = 'completed'
        self.updated_at = datetime.datetime.utcnow()
    
    def mark_as_in_progress(self) -> None:
        """
        تحديد التقييم كقيد التنفيذ
        """
        self.status = 'in_progress'
        self.updated_at = datetime.datetime.utcnow()
    
    def mark_as_rejected(self) -> None:
        """
        تحديد التقييم كمرفوض
        """
        self.status = 'rejected'
        self.updated_at = datetime.datetime.utcnow()

class BlockchainVerification(db.Model):
    """نموذج التحقق من سلسلة الكتل في نظام تقييم BTEC"""
    __tablename__ = 'blockchain_verifications'
    
    # حقول قاعدة البيانات
    id = db.Column(db.Integer, primary_key=True)
    evaluation_id = db.Column(db.Integer, db.ForeignKey('evaluations.id'))
    hash_value = db.Column(db.String(256), nullable=False)
    transaction_id = db.Column(db.String(256), nullable=False)
    verified = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    verification_date = db.Column(db.DateTime)
    
    # العلاقات
    # evaluation = db.relationship('Evaluation', backref='blockchain_verification', uselist=False)
    
    def __repr__(self):
        return f'<BlockchainVerification {self.id} - {self.verified}>'
    
    def to_dict(self) -> Dict[str, Any]:
        """
        تحويل التحقق من سلسلة الكتل إلى قاموس
        
        Returns:
            Dict[str, Any]: بيانات التحقق من سلسلة الكتل
        """
        return {
            'id': self.id,
            'evaluation_id': self.evaluation_id,
            'hash_value': self.hash_value,
            'transaction_id': self.transaction_id,
            'verified': self.verified,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'verification_date': self.verification_date.isoformat() if self.verification_date else None
        }
    
    @classmethod
    def get_by_evaluation_id(cls, evaluation_id: int) -> Optional['BlockchainVerification']:
        """
        الحصول على التحقق من سلسلة الكتل حسب معرف التقييم
        
        Args:
            evaluation_id (int): معرف التقييم
        
        Returns:
            Optional[BlockchainVerification]: التحقق من سلسلة الكتل أو None إذا لم يتم العثور عليه
        """
        return cls.query.filter_by(evaluation_id=evaluation_id).first()
    
    def mark_as_verified(self) -> None:
        """
        تحديد التحقق من سلسلة الكتل كمتحقق منه
        """
        self.verified = True
        self.verification_date = datetime.datetime.utcnow()