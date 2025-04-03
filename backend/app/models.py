from .database import db
from werkzeug.security import generate_password_hash, check_password_hash
import datetime
import json
from sqlalchemy.ext.hybrid import hybrid_property

class User(db.Model):
    """نموذج المستخدم في نظام تقييم BTEC."""
    __tablename__ = 'user'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), index=True, unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    name = db.Column(db.String(100))
    role = db.Column(db.String(20), default='user')  # يمكن أن يكون 'user', 'admin', 'teacher'
    is_active = db.Column(db.Boolean, default=True)
    last_login = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    evaluations = db.relationship('Evaluation', backref='submitter', lazy='dynamic', cascade='all, delete-orphan')
    
    def set_password(self, password):
        """تعيين كلمة المرور المشفرة."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """التحقق من صحة كلمة المرور."""
        return check_password_hash(self.password_hash, password)
    
    @property
    def is_admin(self):
        """التحقق ما إذا كان المستخدم مسؤولاً."""
        return self.role == 'admin'
    
    @property
    def is_teacher(self):
        """التحقق ما إذا كان المستخدم معلماً."""
        return self.role == 'teacher'
    
    def update_last_login(self):
        """تحديث وقت آخر تسجيل دخول."""
        self.last_login = datetime.datetime.utcnow()
        db.session.commit()
    
    def to_dict(self):
        """تحويل بيانات المستخدم إلى قاموس."""
        return {
            'id': self.id,
            'email': self.email,
            'name': self.name,
            'role': self.role,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'evaluation_count': self.evaluations.count()
        }

    def __repr__(self):
        return f'<User {self.email}>'

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
    
    @hybrid_property
    def is_verified(self):
        """التحقق ما إذا كان التقييم مُتحقق منه."""
        return self.verification_status is True
    
    @property
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
        self.rubric_results = json.dumps(data)
    
    def verify(self):
        """وضع علامة على التقييم كمُتحقق منه."""
        self.verification_status = True
        self.verification_timestamp = datetime.datetime.utcnow()
        db.session.commit()
    
    def to_dict(self, include_task=False, vault=None):
        """تحويل بيانات التقييم إلى قاموس."""
        result = {
            'id': self.id,
            'grade': self.grade,
            'grade_numerical': self.grade_numerical,
            'feedback': self.feedback,
            'audit_hash': self.audit_hash,
            'is_verified': self.is_verified,
            'submitted_at': self.submitted_at.isoformat() if self.submitted_at else None,
            'evaluated_at': self.evaluated_at.isoformat() if self.evaluated_at else None,
            'verification_timestamp': self.verification_timestamp.isoformat() if self.verification_timestamp else None,
            'user_id': self.user_id,
            'rubric_results': self.rubric_data
        }
        
        # فك تشفير المهمة إذا طُلب ذلك وتوفر Vault
        if include_task and vault:
            try:
                result['task'] = vault.decrypt(self.task_encrypted)
            except Exception:
                result['task'] = "خطأ في فك تشفير المهمة."
        elif include_task:
            result['task'] = "المهمة مشفرة."
            
        return result

    def __repr__(self):
        return f'<Evaluation {self.id} by User {self.user_id}>'

class RubricTemplate(db.Model):
    """نموذج قالب معايير التقييم."""
    __tablename__ = 'rubric_template'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    content = db.Column(db.Text, nullable=False)  # معايير التقييم بتنسيق JSON
    is_default = db.Column(db.Boolean, default=False)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.datetime.utcnow)
    
    user = db.relationship('User', backref=db.backref('rubric_templates', lazy='dynamic'))
    
    @property
    def rubric_data(self):
        """استرجاع معايير التقييم كقاموس Python."""
        try:
            return json.loads(self.content)
        except json.JSONDecodeError:
            return {}
    
    def set_rubric_data(self, data):
        """تعيين معايير التقييم من قاموس Python."""
        self.content = json.dumps(data)
    
    def to_dict(self):
        """تحويل بيانات قالب المعايير إلى قاموس."""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'content': self.rubric_data,
            'is_default': self.is_default,
            'created_by': self.created_by,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<RubricTemplate {self.name}>'

class SystemMetrics(db.Model):
    """نموذج لتخزين مقاييس النظام."""
    __tablename__ = 'system_metrics'
    
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    api_calls = db.Column(db.Integer, default=0)
    evaluations_completed = db.Column(db.Integer, default=0)
    blockchain_verifications = db.Column(db.Integer, default=0)
    average_response_time = db.Column(db.Float)
    error_count = db.Column(db.Integer, default=0)
    active_users = db.Column(db.Integer, default=0)
    
    def to_dict(self):
        """تحويل بيانات المقاييس إلى قاموس."""
        return {
            'id': self.id,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'api_calls': self.api_calls,
            'evaluations_completed': self.evaluations_completed,
            'blockchain_verifications': self.blockchain_verifications,
            'average_response_time': self.average_response_time,
            'error_count': self.error_count,
            'active_users': self.active_users
        }
    
    def __repr__(self):
        return f'<SystemMetrics {self.timestamp}>'