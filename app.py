"""
نقطة الدخول الرئيسية لتطبيق نظام تقييم BTEC
يقوم بتشغيل التطبيق على المنفذ 5000
"""

import os
import logging
from datetime import datetime
from flask import Flask, render_template, jsonify, send_from_directory
from flask_sqlalchemy import SQLAlchemy

# إعداد السجلات
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('server.log')
    ]
)

logger = logging.getLogger(__name__)
logger.info("بدء تشغيل نظام تقييم BTEC")

# إنشاء تطبيق Flask
app = Flask(__name__, 
           template_folder='app/templates', 
           static_folder='app/static')
app.secret_key = os.environ.get("SESSION_SECRET", "btec_secure_key_placeholder")

# إعداد قاعدة البيانات
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}

db = SQLAlchemy(app)

# إنشاء نماذج قاعدة البيانات
class User(db.Model):
    """نموذج المستخدم في نظام تقييم BTEC."""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), index=True, unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    name = db.Column(db.String(100))
    role = db.Column(db.String(20), default='student')
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<User {self.email}>'

class Rubric(db.Model):
    """نموذج معيار التقييم في نظام تقييم BTEC."""
    __tablename__ = 'rubrics'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    criteria = db.Column(db.JSON, default={})
    max_score = db.Column(db.Float, default=100)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Rubric {self.name}>'

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
    status = db.Column(db.String(20), default='pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Evaluation {self.id}>'

class BlockchainVerification(db.Model):
    """نموذج التحقق من سلسلة الكتل في نظام تقييم BTEC."""
    __tablename__ = 'blockchain_verifications'
    
    id = db.Column(db.Integer, primary_key=True)
    evaluation_id = db.Column(db.Integer, db.ForeignKey('evaluations.id'))
    hash_value = db.Column(db.String(256), nullable=False)
    transaction_id = db.Column(db.String(256), nullable=False)
    verified = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<BlockchainVerification {self.id}>'

# إنشاء مسارات التطبيق
@app.route('/')
def index():
    """الصفحة الرئيسية"""
    return render_template('index.html')

@app.route('/health')
def health():
    """
    نقطة نهاية للتحقق من صحة النظام
    """
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0"
    })

@app.route('/static/<path:path>')
def serve_static(path):
    """تقديم الملفات الثابتة"""
    return send_from_directory('app/static', path)

# معالجة الأخطاء
@app.errorhandler(404)
def page_not_found(e):
    """معالجة خطأ 404 - الصفحة غير موجودة"""
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(e):
    """معالجة خطأ 500 - خطأ في الخادم"""
    logger.error(f"حدث خطأ في الخادم: {str(e)}")
    return render_template('errors/500.html'), 500

# تشغيل التطبيق
if __name__ == '__main__':
    # التأكد من وجود جداول قاعدة البيانات
    with app.app_context():
        db.create_all()
        logger.info("تم التحقق من جداول قاعدة البيانات")
    
    # تشغيل التطبيق
    app.run(host='0.0.0.0', port=5000, debug=True)