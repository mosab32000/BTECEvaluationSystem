"""
نموذج التقييم في نظام تقييم BTEC
"""
import json
from datetime import datetime
import hashlib

from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey, Table
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSONB

from app import db

# جدول العلاقة بين المساقات والطلاب
course_student = Table(
    'course_student',
    db.Model.metadata,
    Column('course_id', Integer, ForeignKey('course.id'), primary_key=True),
    Column('student_id', Integer, ForeignKey('user.id'), primary_key=True)
)

class Evaluation(db.Model):
    """نموذج التقييم في نظام تقييم BTEC."""
    __tablename__ = 'evaluation'
    
    # الأعمدة الأساسية
    id = Column(Integer, primary_key=True)
    title = Column(String(200), nullable=False)
    description = Column(Text)
    task_description = Column(Text, nullable=False)
    submission_text = Column(Text, nullable=False)
    grade = Column(Float)
    feedback = Column(Text)
    status = Column(String(20), default='pending')  # pending, in_progress, completed, archived
    criteria = Column(JSONB)  # معايير التقييم والدرجات (JSON)
    media_files = Column(Text)  # قائمة الملفات المرفقة (JSON)
    verification_data = Column(JSONB)  # بيانات التحقق من البلوكتشين (JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at = Column(DateTime)
    
    # العلاقات
    evaluator_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    student_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    course_id = Column(Integer, ForeignKey('course.id'))
    rubric_id = Column(Integer, ForeignKey('rubric_template.id'))
    
    # العلاقات (relationships)
    evaluator = relationship('User', foreign_keys=[evaluator_id], back_populates='evaluations_given')
    student = relationship('User', foreign_keys=[student_id], back_populates='evaluations_received')
    course = relationship('Course', back_populates='evaluations')
    rubric = relationship('RubricTemplate', back_populates='evaluations')
    
    def get_media_files(self):
        """الحصول على قائمة الملفات المرفقة.
        
        Returns:
            list: قائمة الملفات المرفقة
        """
        if not self.media_files:
            return []
        
        try:
            return json.loads(self.media_files)
        except Exception:
            return []
    
    def set_media_files(self, files):
        """تعيين قائمة الملفات المرفقة.
        
        Args:
            files: قائمة الملفات المرفقة
        """
        self.media_files = json.dumps(files)
    
    def set_verification_data(self, data):
        """تعيين بيانات التحقق من البلوكتشين.
        
        Args:
            data: بيانات التحقق
        """
        self.verification_data = data
        db.session.commit()
    
    def generate_hash(self):
        """توليد هاش للتقييم.
        
        Returns:
            str: هاش التقييم
        """
        # إنشاء سلسلة نصية تمثل البيانات الأساسية للتقييم
        data_str = f"{self.id}|{self.task_description}|{self.submission_text}|{self.grade}|{self.evaluator_id}|{self.student_id}"
        
        # توليد هاش SHA-256
        hash_obj = hashlib.sha256(data_str.encode())
        return hash_obj.hexdigest()
    
    def is_verified(self):
        """التحقق مما إذا كان التقييم مُتحقق منه بواسطة البلوكتشين.
        
        Returns:
            bool: ما إذا كان التقييم مُتحقق منه
        """
        return bool(self.verification_data and self.verification_data.get('verified', False))
    
    def to_dict(self):
        """تحويل كائن التقييم إلى قاموس.
        
        Returns:
            dict: قاموس يمثل التقييم
        """
        eval_dict = {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'task_description': self.task_description,
            'submission_text': self.submission_text,
            'grade': self.grade,
            'feedback': self.feedback,
            'status': self.status,
            'criteria': self.criteria,
            'media_files': self.get_media_files(),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'evaluator_id': self.evaluator_id,
            'student_id': self.student_id,
            'course_id': self.course_id,
            'rubric_id': self.rubric_id,
            'is_verified': self.is_verified()
        }
        
        # إضافة بيانات المقيّم والطالب
        if self.evaluator:
            eval_dict['evaluator'] = {
                'id': self.evaluator.id,
                'name': self.evaluator.name,
                'email': self.evaluator.email
            }
        
        if self.student:
            eval_dict['student'] = {
                'id': self.student.id,
                'name': self.student.name,
                'email': self.student.email
            }
        
        # إضافة بيانات المساق
        if self.course:
            eval_dict['course'] = {
                'id': self.course.id,
                'code': self.course.code,
                'name': self.course.name
            }
        
        # إضافة بيانات معايير التقييم
        if self.rubric:
            eval_dict['rubric'] = {
                'id': self.rubric.id,
                'name': self.rubric.name
            }
        
        return eval_dict
    
    def __repr__(self):
        """تمثيل سلسلة نصية للتقييم.
        
        Returns:
            str: تمثيل سلسلة نصية
        """
        return f"<Evaluation {self.id} ({self.title})>"

class Course(db.Model):
    """نموذج المساق في نظام تقييم BTEC."""
    __tablename__ = 'course'
    
    # الأعمدة الأساسية
    id = Column(Integer, primary_key=True)
    code = Column(String(50), unique=True, nullable=False)
    name = Column(String(200), nullable=False)
    description = Column(Text)
    institution = Column(String(100))
    level = Column(String(50))
    credits = Column(Integer)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # العلاقات
    instructor_id = Column(Integer, ForeignKey('user.id'))
    instructor = relationship('User', back_populates='courses')
    evaluations = relationship('Evaluation', back_populates='course')
    students = relationship('User', secondary=course_student, backref='enrolled_courses')
    tasks = relationship('Task', back_populates='course', cascade='all, delete-orphan')
    
    def to_dict(self):
        """تحويل كائن المساق إلى قاموس.
        
        Returns:
            dict: قاموس يمثل المساق
        """
        course_dict = {
            'id': self.id,
            'code': self.code,
            'name': self.name,
            'description': self.description,
            'institution': self.institution,
            'level': self.level,
            'credits': self.credits,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'instructor_id': self.instructor_id
        }
        
        # إضافة بيانات المدرس
        if self.instructor:
            course_dict['instructor'] = {
                'id': self.instructor.id,
                'name': self.instructor.name,
                'email': self.instructor.email
            }
        
        return course_dict
    
    def __repr__(self):
        """تمثيل سلسلة نصية للمساق.
        
        Returns:
            str: تمثيل سلسلة نصية
        """
        return f"<Course {self.id} {self.code} ({self.name})>"

class Task(db.Model):
    """نموذج المهمة في نظام تقييم BTEC."""
    __tablename__ = 'task'
    
    # الأعمدة الأساسية
    id = Column(Integer, primary_key=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    instructions = Column(Text)
    deadline = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # العلاقات
    course_id = Column(Integer, ForeignKey('course.id'), nullable=False)
    rubric_id = Column(Integer, ForeignKey('rubric_template.id'))
    
    # العلاقات (relationships)
    course = relationship('Course', back_populates='tasks')
    rubric = relationship('RubricTemplate')
    
    def to_dict(self):
        """تحويل كائن المهمة إلى قاموس.
        
        Returns:
            dict: قاموس يمثل المهمة
        """
        task_dict = {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'instructions': self.instructions,
            'deadline': self.deadline.isoformat() if self.deadline else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'course_id': self.course_id,
            'rubric_id': self.rubric_id
        }
        
        # إضافة بيانات المساق
        if self.course:
            task_dict['course'] = {
                'id': self.course.id,
                'code': self.course.code,
                'name': self.course.name
            }
        
        # إضافة بيانات معايير التقييم
        if self.rubric:
            task_dict['rubric'] = {
                'id': self.rubric.id,
                'name': self.rubric.name
            }
        
        return task_dict
    
    def __repr__(self):
        """تمثيل سلسلة نصية للمهمة.
        
        Returns:
            str: تمثيل سلسلة نصية
        """
        return f"<Task {self.id} ({self.title})>"