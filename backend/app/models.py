from .database import db
from werkzeug.security import generate_password_hash, check_password_hash
import datetime

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), index=True, unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    evaluations = db.relationship('Evaluation', backref='submitter', lazy='dynamic')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.email}>'

class Evaluation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    task_encrypted = db.Column(db.Text, nullable=False)  # Store encrypted task
    grade = db.Column(db.String(100))  # AI generated grade/feedback
    audit_hash = db.Column(db.String(66))  # Blockchain transaction hash (e.g., keccak256)
    submitted_at = db.Column(db.DateTime, index=True, default=datetime.datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return f'<Evaluation {self.id} by User {self.user_id}>'
