"""
نماذج الفصول الدراسية في نظام تقييم BTEC
"""

from datetime import datetime

from app.extensions import db

# جدول العلاقة بين الفصول والطلاب
class_student = db.Table(
    'class_student',
    db.Column('class_id', db.Integer, db.ForeignKey('classes.id'), primary_key=True),
    db.Column('student_id', db.Integer, db.ForeignKey('users.id'), primary_key=True),
    db.Column('joined_at', db.DateTime, default=datetime.utcnow)
)


class Class(db.Model):
    """نموذج الفصل الدراسي في نظام تقييم BTEC."""
    __tablename__ = 'classes'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    teacher_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    course_code = db.Column(db.String(20))
    semester = db.Column(db.String(20))
    academic_year = db.Column(db.String(10))
    status = db.Column(db.String(20), default='active')  # active, completed, cancelled
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # العلاقات
    teacher = db.relationship('User', foreign_keys=[teacher_id], backref='teaching_classes')
    students = db.relationship('User', secondary=class_student, backref='enrolled_classes')
    attendance_logs = db.relationship('AttendanceLog', backref='class_group', lazy='dynamic')
    
    def __repr__(self):
        return f'<Class {self.id} - {self.name}>'
    
    def add_student(self, student):
        """إضافة طالب إلى الفصل.
        
        Args:
            student (User): الطالب المراد إضافته
            
        Returns:
            bool: True إذا تمت الإضافة بنجاح، False إذا كان الطالب مضافًا بالفعل
        """
        if student in self.students:
            return False
        
        self.students.append(student)
        return True
    
    def remove_student(self, student):
        """إزالة طالب من الفصل.
        
        Args:
            student (User): الطالب المراد إزالته
            
        Returns:
            bool: True إذا تمت الإزالة بنجاح، False إذا لم يكن الطالب موجودًا في الفصل
        """
        if student not in self.students:
            return False
        
        self.students.remove(student)
        return True
    
    def get_student_count(self):
        """الحصول على عدد الطلاب في الفصل.
        
        Returns:
            int: عدد الطلاب
        """
        return len(self.students)
    
    def to_dict(self):
        """تحويل بيانات الفصل إلى قاموس.
        
        Returns:
            dict: بيانات الفصل
        """
        teacher_name = self.teacher.name if self.teacher else None
        
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'teacher_id': self.teacher_id,
            'teacher_name': teacher_name,
            'course_code': self.course_code,
            'semester': self.semester,
            'academic_year': self.academic_year,
            'status': self.status,
            'student_count': self.get_student_count(),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }