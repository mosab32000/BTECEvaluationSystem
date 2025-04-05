"""
مسارات الإدارة في نظام تقييم BTEC
"""
import logging
import json
from datetime import datetime
import os

from flask import Blueprint, request, jsonify, render_template, redirect
from flask import url_for, session, flash, current_app
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash

from app.models.user import User
from app.models.evaluation import Evaluation
from app.models.rubric import Rubric

# تهيئة السجل
logger = logging.getLogger(__name__)

# إنشاء blueprint للإدارة
bp = Blueprint('admin', __name__, url_prefix='/admin')

# التحقق من صلاحيات المسؤول
def admin_required(view):
    """
    وظيفة للتحقق من صلاحيات المسؤول
    """
    @login_required
    def wrapped_view(**kwargs):
        if current_user.role != 'admin':
            flash('عذراً، يجب أن تكون مسؤولاً للوصول إلى هذه الصفحة.', 'error')
            return redirect(url_for('index'))
        return view(**kwargs)
    
    # احتفظ باسم الدالة الأصلية ومعلوماتها
    wrapped_view.__name__ = view.__name__
    wrapped_view.__doc__ = view.__doc__
    return wrapped_view

@bp.route('/')
@admin_required
def index():
    """لوحة التحكم الرئيسية للمسؤول"""
    # إحصائيات النظام
    user_count = len(User.get_all())
    evaluation_count = len(Evaluation.get_all())
    
    # إحصائيات المستخدمين
    admin_count = len(User.get_by_role('admin'))
    evaluator_count = len(User.get_by_role('evaluator'))
    student_count = len(User.get_by_role('student'))
    
    # إحصائيات التقييمات
    pending_count = len(Evaluation.get_by_status('pending'))
    completed_count = len(Evaluation.get_by_status('completed'))
    
    return render_template(
        'admin/index.html',
        user_count=user_count,
        evaluation_count=evaluation_count,
        admin_count=admin_count,
        evaluator_count=evaluator_count,
        student_count=student_count,
        pending_count=pending_count,
        completed_count=completed_count
    )

@bp.route('/users')
@admin_required
def users():
    """إدارة المستخدمين"""
    users = User.get_all()
    return render_template('admin/users.html', users=users)

@bp.route('/users/create', methods=['GET', 'POST'])
@admin_required
def create_user():
    """إنشاء مستخدم جديد"""
    if request.method == 'POST':
        # الحصول على بيانات النموذج
        email = request.form.get('email')
        password = request.form.get('password')
        name = request.form.get('name')
        role = request.form.get('role')
        
        # التحقق من البيانات
        error = None
        if not email:
            error = 'البريد الإلكتروني مطلوب'
        elif not password:
            error = 'كلمة المرور مطلوبة'
        elif not role:
            error = 'الدور مطلوب'
        
        # التحقق من وجود المستخدم
        existing_user = User.get_by_email(email)
        if existing_user:
            error = 'البريد الإلكتروني مستخدم بالفعل'
        
        # إنشاء المستخدم إذا لم يكن هناك خطأ
        if error is None:
            user = User()
            user.email = email
            user.set_password(password)
            user.name = name
            user.role = role
            
            if user.save():
                flash(f'تم إنشاء المستخدم {email} بنجاح', 'success')
                return redirect(url_for('admin.users'))
            else:
                error = 'حدث خطأ أثناء إنشاء المستخدم'
        
        flash(error, 'error')
    
    return render_template('admin/create_user.html')

@bp.route('/users/<int:user_id>/edit', methods=['GET', 'POST'])
@admin_required
def edit_user(user_id):
    """تعديل مستخدم"""
    user = User.get_by_id(user_id)
    if not user:
        flash('المستخدم غير موجود', 'error')
        return redirect(url_for('admin.users'))
    
    if request.method == 'POST':
        # الحصول على بيانات النموذج
        email = request.form.get('email')
        name = request.form.get('name')
        role = request.form.get('role')
        is_active = request.form.get('is_active') == 'on'
        new_password = request.form.get('password')
        
        # التحقق من البيانات
        error = None
        if not email:
            error = 'البريد الإلكتروني مطلوب'
        elif not role:
            error = 'الدور مطلوب'
        
        # التحقق من وجود المستخدم بنفس البريد الإلكتروني
        if email != user.email:
            existing_user = User.get_by_email(email)
            if existing_user:
                error = 'البريد الإلكتروني مستخدم بالفعل'
        
        # تحديث المستخدم إذا لم يكن هناك خطأ
        if error is None:
            user.email = email
            user.name = name
            user.role = role
            
            # تعيين كلمة مرور جديدة إذا تم توفيرها
            if new_password:
                user.set_password(new_password)
            
            # تحديث حالة التنشيط
            user.is_active = is_active
            
            if user.save():
                flash(f'تم تحديث المستخدم {email} بنجاح', 'success')
                return redirect(url_for('admin.users'))
            else:
                error = 'حدث خطأ أثناء تحديث المستخدم'
        
        flash(error, 'error')
    
    return render_template('admin/edit_user.html', user=user)

@bp.route('/users/<int:user_id>/delete', methods=['POST'])
@admin_required
def delete_user(user_id):
    """حذف مستخدم"""
    user = User.get_by_id(user_id)
    if not user:
        flash('المستخدم غير موجود', 'error')
    elif user.id == current_user.id:
        flash('لا يمكنك حذف حسابك الشخصي', 'error')
    elif user.delete():
        flash(f'تم حذف المستخدم {user.email} بنجاح', 'success')
    else:
        flash('حدث خطأ أثناء حذف المستخدم', 'error')
    
    return redirect(url_for('admin.users'))

@bp.route('/rubrics')
@admin_required
def rubrics():
    """إدارة معايير التقييم"""
    rubrics = Rubric.get_all()
    return render_template('admin/rubrics.html', rubrics=rubrics)

@bp.route('/rubrics/create', methods=['GET', 'POST'])
@admin_required
def create_rubric():
    """إنشاء معيار تقييم جديد"""
    if request.method == 'POST':
        # الحصول على بيانات النموذج
        name = request.form.get('name')
        description = request.form.get('description')
        criteria_json = request.form.get('criteria_json')
        max_score = request.form.get('max_score')
        
        # التحقق من البيانات
        error = None
        if not name:
            error = 'اسم المعيار مطلوب'
        
        # التحقق من صحة معايير التقييم
        try:
            criteria = json.loads(criteria_json or '{}')
        except json.JSONDecodeError:
            error = 'تنسيق معايير التقييم غير صالح'
        
        # إنشاء معيار التقييم إذا لم يكن هناك خطأ
        if error is None:
            rubric = Rubric()
            rubric.name = name
            rubric.description = description
            rubric.criteria = criteria
            rubric.max_score = float(max_score) if max_score else 100
            rubric.created_by = current_user.id
            
            if rubric.save():
                flash(f'تم إنشاء معيار التقييم "{name}" بنجاح', 'success')
                return redirect(url_for('admin.rubrics'))
            else:
                error = 'حدث خطأ أثناء إنشاء معيار التقييم'
        
        flash(error, 'error')
    
    return render_template('admin/create_rubric.html')

@bp.route('/rubrics/<int:rubric_id>/edit', methods=['GET', 'POST'])
@admin_required
def edit_rubric(rubric_id):
    """تعديل معيار تقييم"""
    rubric = Rubric.get_by_id(rubric_id)
    if not rubric:
        flash('معيار التقييم غير موجود', 'error')
        return redirect(url_for('admin.rubrics'))
    
    if request.method == 'POST':
        # الحصول على بيانات النموذج
        name = request.form.get('name')
        description = request.form.get('description')
        criteria_json = request.form.get('criteria_json')
        max_score = request.form.get('max_score')
        
        # التحقق من البيانات
        error = None
        if not name:
            error = 'اسم المعيار مطلوب'
        
        # التحقق من صحة معايير التقييم
        try:
            criteria = json.loads(criteria_json or '{}')
        except json.JSONDecodeError:
            error = 'تنسيق معايير التقييم غير صالح'
        
        # تحديث معيار التقييم إذا لم يكن هناك خطأ
        if error is None:
            rubric.name = name
            rubric.description = description
            rubric.criteria = criteria
            rubric.max_score = float(max_score) if max_score else 100
            
            if rubric.save():
                flash(f'تم تحديث معيار التقييم "{name}" بنجاح', 'success')
                return redirect(url_for('admin.rubrics'))
            else:
                error = 'حدث خطأ أثناء تحديث معيار التقييم'
        
        flash(error, 'error')
    
    return render_template(
        'admin/edit_rubric.html',
        rubric=rubric,
        criteria_json=json.dumps(rubric.criteria, ensure_ascii=False, indent=2)
    )

@bp.route('/rubrics/<int:rubric_id>/delete', methods=['POST'])
@admin_required
def delete_rubric(rubric_id):
    """حذف معيار تقييم"""
    rubric = Rubric.get_by_id(rubric_id)
    if not rubric:
        flash('معيار التقييم غير موجود', 'error')
    elif rubric.delete():
        flash(f'تم حذف معيار التقييم "{rubric.name}" بنجاح', 'success')
    else:
        flash('حدث خطأ أثناء حذف معيار التقييم', 'error')
    
    return redirect(url_for('admin.rubrics'))

@bp.route('/evaluations')
@admin_required
def evaluations():
    """إدارة التقييمات"""
    evaluations = Evaluation.get_all(limit=50)
    return render_template('admin/evaluations.html', evaluations=evaluations)

@bp.route('/settings', methods=['GET', 'POST'])
@admin_required
def settings():
    """إعدادات النظام"""
    if request.method == 'POST':
        # TODO: تنفيذ حفظ الإعدادات
        flash('تم حفظ الإعدادات بنجاح', 'success')
        return redirect(url_for('admin.index'))
    
    return render_template('admin/settings.html')

@bp.route('/logs')
@admin_required
def logs():
    """سجلات النظام"""
    log_file = current_app.config.get('LOG_FILE')
    logs = []
    
    if os.path.exists(log_file):
        with open(log_file, 'r') as f:
            logs = f.readlines()[-100:]  # الحصول على آخر 100 سطر
    
    return render_template('admin/logs.html', logs=logs)