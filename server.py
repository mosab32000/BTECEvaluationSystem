from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import os
from dotenv import load_dotenv

# تحميل متغيرات البيئة
load_dotenv()

# إنشاء تطبيق Flask
app = Flask(__name__)

# تكوين قاعدة البيانات
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = os.environ.get('SECRET_KEY', 'you-will-never-guess')

# إنشاء كائن قاعدة البيانات
db = SQLAlchemy(app)

# تعريف النماذج
class User(db.Model):
    """نموذج المستخدم في نظام تقييم BTEC."""
    __tablename__ = 'user'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), index=True, unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    name = db.Column(db.String(100))
    role = db.Column(db.String(20), default='user')
    is_active = db.Column(db.Boolean, default=True)
    
    def __repr__(self):
        return f'<User {self.email}>'

# إنشاء الجداول في قاعدة البيانات
with app.app_context():
    db.create_all()

# مسار الصفحة الرئيسية
@app.route('/')
def index():
    return jsonify({"message": "مرحبًا بك في نظام تقييم BTEC!"})

# مسار للتحقق من صحة النظام
@app.route('/health')
def health():
    return jsonify({"status": "ok"})

# تشغيل التطبيق
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000, debug=True)