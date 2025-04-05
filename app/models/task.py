
"""
نموذج المهام والتقييم في نظام BTEC
"""
import os
import datetime
from backend.app.database import db

def task_upload_path(instance, filename):
    """إنشاء مسار التحميل للملفات"""
    return f'tasks/{filename}'

class Task(db.Model):
    """نموذج المهمة المقدمة للتحليل والتقييم"""
    __tablename__ = 'tasks'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)
    uploaded_file = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    analysis_result = db.Column(db.JSON, nullable=True)
    evaluation_result = db.Column(db.JSON, nullable=True)
    
    def __repr__(self):
        return f"<Task {self.id}: {self.title}>"
    
    @property
    def filename(self):
        """الحصول على اسم الملف المرفوع"""
        if self.uploaded_file:
            return os.path.basename(self.uploaded_file)
        return None
