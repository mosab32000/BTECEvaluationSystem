"""
مسارات الواجهة الأمامية لنظام تقييم BTEC
"""

from flask import render_template, redirect, url_for, session, request, Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

frontend = Blueprint('frontend', __name__)

@frontend.route('/')
def index():
    """الصفحة الرئيسية"""
    return render_template('index.html')

@frontend.route('/login')
def login():
    """صفحة تسجيل الدخول"""
    # إذا كان المستخدم مسجل دخوله بالفعل، توجيهه إلى لوحة التحكم
    if 'user_id' in session:
        return redirect(url_for('frontend.dashboard'))
    return render_template('login.html')

@frontend.route('/register')
def register():
    """صفحة التسجيل"""
    # إذا كان المستخدم مسجل دخوله بالفعل، توجيهه إلى لوحة التحكم
    if 'user_id' in session:
        return redirect(url_for('frontend.dashboard'))
    return render_template('register.html')

@frontend.route('/dashboard')
def dashboard():
    """صفحة لوحة التحكم"""
    # إذا لم يكن المستخدم مسجل دخوله، توجيهه إلى صفحة تسجيل الدخول
    if 'user_id' not in session:
        return redirect(url_for('frontend.login'))
    return render_template('dashboard.html')

@frontend.route('/evaluate')
def evaluate():
    """صفحة تقييم مهمة جديدة"""
    # إذا لم يكن المستخدم مسجل دخوله، توجيهه إلى صفحة تسجيل الدخول
    if 'user_id' not in session:
        return redirect(url_for('frontend.login'))
    return render_template('evaluate.html')

@frontend.route('/evaluations')
def evaluations():
    """صفحة عرض جميع التقييمات"""
    # إذا لم يكن المستخدم مسجل دخوله، توجيهه إلى صفحة تسجيل الدخول
    if 'user_id' not in session:
        return redirect(url_for('frontend.login'))
    return render_template('evaluations.html')

@frontend.route('/evaluations/<evaluation_id>')
def evaluation_detail(evaluation_id):
    """صفحة عرض تفاصيل تقييم محدد"""
    # إذا لم يكن المستخدم مسجل دخوله، توجيهه إلى صفحة تسجيل الدخول
    if 'user_id' not in session:
        return redirect(url_for('frontend.login'))
    return render_template('evaluation_detail.html', evaluation_id=evaluation_id)

@frontend.route('/verify')
def verify():
    """صفحة التحقق من صحة تقييم"""
    # إذا لم يكن المستخدم مسجل دخوله، توجيهه إلى صفحة تسجيل الدخول
    if 'user_id' not in session:
        return redirect(url_for('frontend.login'))
    return render_template('verify.html')

@frontend.route('/admin')
def admin_dashboard():
    """لوحة التحكم الإدارية"""
    # إذا لم يكن المستخدم مسجل دخوله أو ليس لديه صلاحيات الإدارة، توجيهه إلى صفحة مناسبة
    if 'user_id' not in session:
        return redirect(url_for('frontend.login'))
    if session.get('user_role') != 'admin':
        return redirect(url_for('frontend.dashboard'))
    return render_template('admin_dashboard.html')

@frontend.route('/logout')
def logout():
    """تسجيل الخروج"""
    # إزالة بيانات المستخدم من الجلسة
    session.pop('user_id', None)
    session.pop('user_email', None)
    session.pop('user_name', None)
    session.pop('user_role', None)
    return redirect(url_for('frontend.index'))

@frontend.route('/about')
def about():
    """صفحة حول النظام"""
    return render_template('about.html')

@frontend.route('/terms')
def terms():
    """صفحة شروط الاستخدام"""
    return render_template('terms.html')

@frontend.route('/privacy')
def privacy():
    """صفحة سياسة الخصوصية"""
    return render_template('privacy.html')
