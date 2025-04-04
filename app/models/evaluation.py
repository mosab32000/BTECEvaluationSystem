"""
نموذج التقييم في نظام تقييم BTEC
"""
import datetime
import json
import uuid

from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import relationship

from app import db

class Evaluation(db.Model):
    """
    نموذج التقييم في نظام تقييم BTEC
    """
    __tablename__ = 'evaluations'
    
    id = Column(Integer, primary_key=True)
    uuid = Column(String(36), unique=True, default=lambda: str(uuid.uuid4()), index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    task_description = Column(Text, nullable=False)
    submission_text = Column(Text, nullable=False)
    grade = Column(Float, nullable=True)
    status = Column(String(20), default='pending')  # pending, completed, verified
    feedback = Column(Text, nullable=True)
    criteria = Column(JSON, nullable=True)
    rubric_id = Column(Integer, ForeignKey('rubric_templates.id', ondelete='SET NULL'), nullable=True)
    evaluator_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=True)
    student_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    course_id = Column(Integer, ForeignKey('courses.id', ondelete='SET NULL'), nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    
    # بيانات التحقق من البلوكتشين
    verified = Column(Boolean, default=False)
    verification_time = Column(DateTime, nullable=True)
    verification_data = Column(JSON, nullable=True)
    blockchain_hash = Column(String(128), nullable=True)
    
    # بيانات وسائط متعددة (روابط إلى ملفات)
    media_files = Column(JSON, nullable=True)
    
    # العلاقات
    evaluator = relationship('User', foreign_keys=[evaluator_id], back_populates='evaluations')
    student = relationship('User', foreign_keys=[student_id], back_populates='student_evaluations')
    rubric = relationship('RubricTemplate')
    
    def to_dict(self):
        """
        تحويل التقييم إلى قاموس
        
        Returns:
            dict: بيانات التقييم
        """
        return {
            'id': self.id,
            'uuid': self.uuid,
            'title': self.title,
            'description': self.description,
            'task_description': self.task_description,
            'grade': self.grade,
            'status': self.status,
            'feedback': self.feedback,
            'criteria': self.criteria,
            'rubric_id': self.rubric_id,
            'evaluator_id': self.evaluator_id,
            'student_id': self.student_id,
            'course_id': self.course_id,
            'verified': self.verified,
            'blockchain_hash': self.blockchain_hash,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
        }
    
    def to_json(self):
        """
        تحويل التقييم إلى سلسلة JSON
        
        Returns:
            str: سلسلة JSON للتقييم
        """
        return json.dumps(self.to_dict())
    
    def get_criteria_grades(self):
        """
        الحصول على درجات معايير التقييم
        
        Returns:
            dict: درجات المعايير
        """
        if not self.criteria:
            return {}
        
        # التحقق من نوع البيانات وتحويلها إذا لزم الأمر
        criteria_data = self.criteria
        if isinstance(criteria_data, str):
            try:
                criteria_data = json.loads(criteria_data)
            except:
                return {}
        
        # استخراج درجات المعايير
        if isinstance(criteria_data, dict) and 'criteria_grades' in criteria_data:
            return criteria_data['criteria_grades']
        elif isinstance(criteria_data, list):
            return {item.get('name', f'Criterion {i+1}'): item.get('grade', 0) 
                   for i, item in enumerate(criteria_data) if 'grade' in item}
        
        return {}
    
    def get_feedback_summary(self, max_length=200):
        """
        الحصول على ملخص الملاحظات
        
        Args:
            max_length: الحد الأقصى لطول الملخص
            
        Returns:
            str: ملخص الملاحظات
        """
        if not self.feedback:
            return "لا توجد ملاحظات متاحة"
        
        feedback = self.feedback
        if len(feedback) > max_length:
            return feedback[:max_length] + "..."
        return feedback
    
    def update_status(self, status):
        """
        تحديث حالة التقييم
        
        Args:
            status: الحالة الجديدة للتقييم (pending, completed, verified)
        """
        self.status = status
        if status == 'completed' and not self.completed_at:
            self.completed_at = datetime.datetime.utcnow()
        
        db.session.commit()
    
    def set_verification_data(self, verification_data):
        """
        تعيين بيانات التحقق
        
        Args:
            verification_data: بيانات التحقق
        """
        self.verified = True
        self.verification_time = datetime.datetime.utcnow()
        
        # تخزين بيانات التحقق
        if isinstance(verification_data, dict):
            self.verification_data = verification_data
            if 'hash' in verification_data:
                self.blockchain_hash = verification_data['hash']
        else:
            self.verification_data = {'data': str(verification_data)}
        
        db.session.commit()
    
    def __repr__(self):
        """
        تمثيل التقييم كسلسلة نصية
        
        Returns:
            str: تمثيل التقييم
        """
        return f'<Evaluation {self.id}: {self.title} ({self.status})>'


class Course(db.Model):
    """
    نموذج المساق في نظام تقييم BTEC
    """
    __tablename__ = 'courses'
    
    id = Column(Integer, primary_key=True)
    code = Column(String(20), unique=True, nullable=False, index=True)
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    institution = Column(String(200), nullable=True)
    level = Column(String(50), nullable=True)
    credits = Column(Integer, nullable=True)
    instructor_id = Column(Integer, ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    # العلاقات
    instructor = relationship('User')
    
    def to_dict(self):
        """
        تحويل المساق إلى قاموس
        
        Returns:
            dict: بيانات المساق
        """
        return {
            'id': self.id,
            'code': self.code,
            'name': self.name,
            'description': self.description,
            'institution': self.institution,
            'level': self.level,
            'credits': self.credits,
            'instructor_id': self.instructor_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
    
    def __repr__(self):
        """
        تمثيل المساق كسلسلة نصية
        
        Returns:
            str: تمثيل المساق
        """
        return f'<Course {self.code}: {self.name}>'


class Submission(db.Model):
    """
    نموذج تقديم المهام في نظام تقييم BTEC
    """
    __tablename__ = 'submissions'
    
    id = Column(Integer, primary_key=True)
    uuid = Column(String(36), unique=True, default=lambda: str(uuid.uuid4()), index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    content = Column(Text, nullable=False)
    student_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    course_id = Column(Integer, ForeignKey('courses.id', ondelete='SET NULL'), nullable=True)
    task_id = Column(Integer, ForeignKey('tasks.id', ondelete='SET NULL'), nullable=True)
    submitted_at = Column(DateTime, default=datetime.datetime.utcnow)
    status = Column(String(20), default='submitted')  # submitted, evaluated
    
    # بيانات وسائط متعددة (روابط إلى ملفات)
    media_files = Column(JSON, nullable=True)
    
    # العلاقات
    student = relationship('User')
    evaluations = relationship('Evaluation', secondary='evaluation_submissions', backref='submissions')
    
    def to_dict(self):
        """
        تحويل التقديم إلى قاموس
        
        Returns:
            dict: بيانات التقديم
        """
        return {
            'id': self.id,
            'uuid': self.uuid,
            'title': self.title,
            'description': self.description,
            'student_id': self.student_id,
            'course_id': self.course_id,
            'task_id': self.task_id,
            'submitted_at': self.submitted_at.isoformat() if self.submitted_at else None,
            'status': self.status,
            'media_files': self.media_files,
        }
    
    def __repr__(self):
        """
        تمثيل التقديم كسلسلة نصية
        
        Returns:
            str: تمثيل التقديم
        """
        return f'<Submission {self.id}: {self.title} ({self.status})>'


class Task(db.Model):
    """
    نموذج المهمة في نظام تقييم BTEC
    """
    __tablename__ = 'tasks'
    
    id = Column(Integer, primary_key=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    course_id = Column(Integer, ForeignKey('courses.id', ondelete='CASCADE'), nullable=False)
    rubric_id = Column(Integer, ForeignKey('rubric_templates.id', ondelete='SET NULL'), nullable=True)
    due_date = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    # العلاقات
    course = relationship('Course')
    rubric = relationship('RubricTemplate')
    
    def to_dict(self):
        """
        تحويل المهمة إلى قاموس
        
        Returns:
            dict: بيانات المهمة
        """
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'course_id': self.course_id,
            'rubric_id': self.rubric_id,
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
    
    def __repr__(self):
        """
        تمثيل المهمة كسلسلة نصية
        
        Returns:
            str: تمثيل المهمة
        """
        return f'<Task {self.id}: {self.title}>'


# جدول الربط بين التقييمات والتقديمات
evaluation_submissions = db.Table('evaluation_submissions',
    Column('evaluation_id', Integer, ForeignKey('evaluations.id', ondelete='CASCADE'), primary_key=True),
    Column('submission_id', Integer, ForeignKey('submissions.id', ondelete='CASCADE'), primary_key=True)
)