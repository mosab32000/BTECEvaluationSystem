"""
نموذج التقييم في نظام تقييم BTEC
"""

import datetime
import json
from typing import Dict, Any, Optional, List, Union

from app.extensions import db

class Evaluation(db.Model):
    """نموذج التقييم في نظام تقييم BTEC"""
    __tablename__ = 'evaluations'
    
    # حقول قاعدة البيانات
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    evaluator_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    rubric_id = db.Column(db.Integer, db.ForeignKey('rubrics.id'), nullable=False)
    assignment_id = db.Column(db.String(100))  # معرف خارجي اختياري للمهمة
    classroom_id = db.Column(db.Integer, db.ForeignKey('classrooms.id'))
    submission_text = db.Column(db.Text, nullable=False)
    submission_files = db.Column(db.JSON, default=[])
    evaluation_result = db.Column(db.JSON, default={})
    score = db.Column(db.Float)
    ai_score = db.Column(db.Float)
    status = db.Column(db.String(20), default='pending')  # pending, completed, reviewed
    evaluator_comments = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    submitted_at = db.Column(db.DateTime)
    evaluated_at = db.Column(db.DateTime)
    
    # العلاقات
    # student = db.relationship('User', foreign_keys=[student_id], backref='submitted_evaluations')
    # evaluator = db.relationship('User', foreign_keys=[evaluator_id], backref='evaluated_evaluations')
    # rubric = db.relationship('Rubric', backref='evaluations')
    # classroom = db.relationship('Classroom', backref='evaluations')
    
    def __repr__(self):
        return f'<Evaluation {self.id} - Student ID: {self.student_id}>'
    
    def to_dict(self) -> Dict[str, Any]:
        """
        تحويل التقييم إلى قاموس
        
        Returns:
            Dict[str, Any]: بيانات التقييم
        """
        return {
            'id': self.id,
            'student_id': self.student_id,
            'evaluator_id': self.evaluator_id,
            'rubric_id': self.rubric_id,
            'assignment_id': self.assignment_id,
            'classroom_id': self.classroom_id,
            'submission_text': self.submission_text,
            'submission_files': self.submission_files,
            'evaluation_result': self.evaluation_result,
            'score': self.score,
            'ai_score': self.ai_score,
            'status': self.status,
            'evaluator_comments': self.evaluator_comments,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'submitted_at': self.submitted_at.isoformat() if self.submitted_at else None,
            'evaluated_at': self.evaluated_at.isoformat() if self.evaluated_at else None
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
        return cls.query.get(evaluation_id)
    
    @classmethod
    def get_by_student(cls, student_id: int) -> List['Evaluation']:
        """
        الحصول على تقييمات الطالب
        
        Args:
            student_id (int): معرف الطالب
        
        Returns:
            List[Evaluation]: قائمة التقييمات
        """
        return cls.query.filter_by(student_id=student_id).all()
    
    @classmethod
    def get_by_evaluator(cls, evaluator_id: int) -> List['Evaluation']:
        """
        الحصول على تقييمات المقيم
        
        Args:
            evaluator_id (int): معرف المقيم
        
        Returns:
            List[Evaluation]: قائمة التقييمات
        """
        return cls.query.filter_by(evaluator_id=evaluator_id).all()
    
    @classmethod
    def get_by_classroom(cls, classroom_id: int) -> List['Evaluation']:
        """
        الحصول على تقييمات الفصل الدراسي
        
        Args:
            classroom_id (int): معرف الفصل الدراسي
        
        Returns:
            List[Evaluation]: قائمة التقييمات
        """
        return cls.query.filter_by(classroom_id=classroom_id).all()
    
    @classmethod
    def get_by_status(cls, status: str) -> List['Evaluation']:
        """
        الحصول على تقييمات حسب الحالة
        
        Args:
            status (str): حالة التقييم (pending, completed, reviewed)
        
        Returns:
            List[Evaluation]: قائمة التقييمات
        """
        return cls.query.filter_by(status=status).all()
    
    def submit(self) -> None:
        """
        تقديم التقييم
        """
        self.submitted_at = datetime.datetime.utcnow()
        self.status = 'pending'
    
    def evaluate(self, evaluation_result: Dict[str, Any], evaluator_id: int, comments: str = None) -> None:
        """
        تقييم المهمة
        
        Args:
            evaluation_result (Dict[str, Any]): نتائج التقييم
            evaluator_id (int): معرف المقيم
            comments (str, optional): تعليقات المقيم
        """
        self.evaluation_result = evaluation_result
        self.evaluator_id = evaluator_id
        self.evaluator_comments = comments
        self.score = self.calculate_score()
        self.status = 'completed'
        self.evaluated_at = datetime.datetime.utcnow()
    
    def calculate_score(self) -> float:
        """
        حساب الدرجة بناءً على نتائج التقييم
        
        Returns:
            float: الدرجة المحسوبة
        """
        if not self.evaluation_result:
            return 0.0
        
        total_score = 0.0
        max_score = 0.0
        
        for criterion_name, criterion_data in self.evaluation_result.items():
            if isinstance(criterion_data, dict) and 'score' in criterion_data and 'max_score' in criterion_data:
                total_score += criterion_data.get('score', 0)
                max_score += criterion_data.get('max_score', 0)
        
        return (total_score / max_score) * 100 if max_score > 0 else 0.0
    
    def add_ai_score(self, ai_score: float) -> None:
        """
        إضافة درجة الذكاء الاصطناعي
        
        Args:
            ai_score (float): درجة الذكاء الاصطناعي
        """
        self.ai_score = ai_score
    
    def add_file(self, file_path: str, file_type: str, file_name: str) -> None:
        """
        إضافة ملف للتقييم
        
        Args:
            file_path (str): مسار الملف
            file_type (str): نوع الملف
            file_name (str): اسم الملف
        """
        if not self.submission_files:
            self.submission_files = []
        
        file_info = {
            'path': file_path,
            'type': file_type,
            'name': file_name,
            'uploaded_at': datetime.datetime.utcnow().isoformat()
        }
        
        self.submission_files.append(file_info)
    
    def remove_file(self, file_path: str) -> bool:
        """
        إزالة ملف من التقييم
        
        Args:
            file_path (str): مسار الملف
        
        Returns:
            bool: True إذا تمت الإزالة بنجاح، False إذا لم يتم العثور على الملف
        """
        if not self.submission_files:
            return False
        
        initial_length = len(self.submission_files)
        self.submission_files = [f for f in self.submission_files if f.get('path') != file_path]
        
        return len(self.submission_files) < initial_length
    
    def get_files(self) -> List[Dict[str, Any]]:
        """
        الحصول على قائمة الملفات
        
        Returns:
            List[Dict[str, Any]]: قائمة الملفات
        """
        return self.submission_files or []