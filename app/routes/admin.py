"""
مسارات الإدارة في نظام تقييم BTEC
"""

import logging
from flask import render_template, redirect, url_for, request, flash, session, jsonify, abort

from app.routes import admin_bp
from app.models.user import User
from app.models.evaluation import Evaluation
from app.models.rubric import Rubric

logger = logging.getLogger(__name__)

@admin_bp.route('/')
def index():
    """لوحة التحكم الرئيسية للمسؤول"""
    # التحقق من تسجيل الدخول ودور المستخدم
    if 'user_id' not in session or session.get('user_role') != 'admin':
        flash('ليس لديك صلاحية الوصول إلى هذه الصفحة', 'error')
        return redirect(url_for('main.index'))
    
    # إحصائيات النظام
    user_count = User.count_all()
    student_count = User.count_by_role('student')
    teacher_count = User.count_by_role('teacher')
    admin_count = User.count_by_role('admin')
    
    evaluation_count = Evaluation.count_all()
    pending_count = Evaluation.count_by_status('pending')
    completed_count = Evaluation.count_by_status('completed')
    
    rubric_count = Rubric.count_all()
    
    return render_template('admin/index.html',
                          user_count=user_count,
                          student_count=student_count,
                          teacher_count=teacher_count,
                          admin_count=admin_count,
                          evaluation_count=evaluation_count,
                          pending_count=pending_count,
                          completed_count=completed_count,
                          rubric_count=rubric_count)

@admin_bp.route('/users')
def list_users():
    """صفحة إدارة المستخدمين"""
    # التحقق من تسجيل الدخول ودور المستخدم
    if 'user_id' not in session or session.get('user_role') != 'admin':
        flash('ليس لديك صلاحية الوصول إلى هذه الصفحة', 'error')
        return redirect(url_for('main.index'))
    
    # الحصول على قائمة المستخدمين
    users = User.get_all()
    
    return render_template('admin/users.html', users=users)

@admin_bp.route('/users/create', methods=['GET', 'POST'])
def create_user():
    """صفحة إنشاء مستخدم جديد"""
    # التحقق من تسجيل الدخول ودور المستخدم
    if 'user_id' not in session or session.get('user_role') != 'admin':
        flash('ليس لديك صلاحية الوصول إلى هذه الصفحة', 'error')
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        # الحصول على البيانات من النموذج
        email = request.form.get('email')
        password = request.form.get('password')
        name = request.form.get('name')
        role = request.form.get('role')
        
        # التحقق من صحة البيانات
        if not email or not password or not name or not role:
            flash('جميع الحقول مطلوبة', 'error')
            return render_template('admin/create_user.html')
        
        if role not in ['admin', 'teacher', 'student']:
            flash('الدور غير صالح', 'error')
            return render_template('admin/create_user.html')
        
        # التحقق مما إذا كان البريد الإلكتروني مستخدمًا بالفعل
        existing_user = User.get_by_email(email)
        if existing_user:
            flash('البريد الإلكتروني مستخدم بالفعل', 'error')
            return render_template('admin/create_user.html')
        
        # إنشاء مستخدم جديد
        user = User(email=email, name=name, role=role)
        user.set_password(password)
        if user.save():
            flash('تم إنشاء المستخدم بنجاح', 'success')
            return redirect(url_for('admin.list_users'))
        else:
            flash('حدث خطأ أثناء إنشاء المستخدم. يرجى المحاولة مرة أخرى.', 'error')
    
    return render_template('admin/create_user.html')

@admin_bp.route('/users/edit/<int:user_id>', methods=['GET', 'POST'])
def edit_user(user_id):
    """صفحة تعديل مستخدم"""
    # التحقق من تسجيل الدخول ودور المستخدم
    if 'user_id' not in session or session.get('user_role') != 'admin':
        flash('ليس لديك صلاحية الوصول إلى هذه الصفحة', 'error')
        return redirect(url_for('main.index'))
    
    # الحصول على المستخدم المراد تعديله
    user = User.get_by_id(user_id)
    if not user:
        flash('المستخدم غير موجود', 'error')
        return redirect(url_for('admin.list_users'))
    
    if request.method == 'POST':
        # الحصول على البيانات من النموذج
        email = request.form.get('email')
        name = request.form.get('name')
        role = request.form.get('role')
        password = request.form.get('password')
        
        # التحقق من صحة البيانات
        if not email or not name or not role:
            flash('الحقول الأساسية مطلوبة', 'error')
            return render_template('admin/edit_user.html', user=user)
        
        if role not in ['admin', 'teacher', 'student']:
            flash('الدور غير صالح', 'error')
            return render_template('admin/edit_user.html', user=user)
        
        # التحقق مما إذا كان البريد الإلكتروني مستخدمًا بالفعل بواسطة مستخدم آخر
        if email != user.email:
            existing_user = User.get_by_email(email)
            if existing_user and existing_user.id != user.id:
                flash('البريد الإلكتروني مستخدم بالفعل', 'error')
                return render_template('admin/edit_user.html', user=user)
        
        # تحديث بيانات المستخدم
        user.email = email
        user.name = name
        user.role = role
        
        # تحديث كلمة المرور إذا تم تقديمها
        if password:
            user.set_password(password)
        
        if user.save():
            flash('تم تحديث المستخدم بنجاح', 'success')
            return redirect(url_for('admin.list_users'))
        else:
            flash('حدث خطأ أثناء تحديث المستخدم. يرجى المحاولة مرة أخرى.', 'error')
    
    return render_template('admin/edit_user.html', user=user)

@admin_bp.route('/users/delete/<int:user_id>', methods=['POST'])
def delete_user(user_id):
    """حذف مستخدم"""
    # التحقق من تسجيل الدخول ودور المستخدم
    if 'user_id' not in session or session.get('user_role') != 'admin':
        flash('ليس لديك صلاحية الوصول إلى هذه الصفحة', 'error')
        return redirect(url_for('main.index'))
    
    # منع حذف المستخدم الحالي
    if user_id == session['user_id']:
        flash('لا يمكنك حذف حسابك الخاص', 'error')
        return redirect(url_for('admin.list_users'))
    
    # الحصول على المستخدم المراد حذفه
    user = User.get_by_id(user_id)
    if not user:
        flash('المستخدم غير موجود', 'error')
        return redirect(url_for('admin.list_users'))
    
    # حذف المستخدم
    if user.delete():
        flash('تم حذف المستخدم بنجاح', 'success')
    else:
        flash('حدث خطأ أثناء حذف المستخدم', 'error')
    
    return redirect(url_for('admin.list_users'))

@admin_bp.route('/rubrics')
def list_rubrics():
    """صفحة إدارة معايير التقييم"""
    # التحقق من تسجيل الدخول ودور المستخدم
    if 'user_id' not in session or session.get('user_role') != 'admin':
        flash('ليس لديك صلاحية الوصول إلى هذه الصفحة', 'error')
        return redirect(url_for('main.index'))
    
    # الحصول على قائمة معايير التقييم
    rubrics = Rubric.get_all()
    
    return render_template('admin/rubrics.html', rubrics=rubrics)

@admin_bp.route('/rubrics/create', methods=['GET', 'POST'])
def create_rubric():
    """صفحة إنشاء معيار تقييم جديد"""
    # التحقق من تسجيل الدخول ودور المستخدم
    if 'user_id' not in session or session.get('user_role') != 'admin':
        flash('ليس لديك صلاحية الوصول إلى هذه الصفحة', 'error')
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        # الحصول على البيانات من النموذج
        name = request.form.get('name')
        description = request.form.get('description')
        
        # التحقق من صحة البيانات
        if not name:
            flash('اسم معيار التقييم مطلوب', 'error')
            return render_template('admin/create_rubric.html')
        
        # إنشاء معيار تقييم جديد
        rubric = Rubric(
            name=name,
            description=description,
            created_by=session['user_id']
        )
        
        if rubric.save():
            flash('تم إنشاء معيار التقييم بنجاح', 'success')
            return redirect(url_for('admin.list_rubrics'))
        else:
            flash('حدث خطأ أثناء إنشاء معيار التقييم. يرجى المحاولة مرة أخرى.', 'error')
    
    return render_template('admin/create_rubric.html')

@admin_bp.route('/rubrics/edit/<int:rubric_id>', methods=['GET', 'POST'])
def edit_rubric(rubric_id):
    """صفحة تعديل معيار تقييم"""
    # التحقق من تسجيل الدخول ودور المستخدم
    if 'user_id' not in session or session.get('user_role') != 'admin':
        flash('ليس لديك صلاحية الوصول إلى هذه الصفحة', 'error')
        return redirect(url_for('main.index'))
    
    # الحصول على معيار التقييم المراد تعديله
    rubric = Rubric.get_by_id(rubric_id)
    if not rubric:
        flash('معيار التقييم غير موجود', 'error')
        return redirect(url_for('admin.list_rubrics'))
    
    if request.method == 'POST':
        # الحصول على البيانات من النموذج
        name = request.form.get('name')
        description = request.form.get('description')
        
        # التحقق من صحة البيانات
        if not name:
            flash('اسم معيار التقييم مطلوب', 'error')
            return render_template('admin/edit_rubric.html', rubric=rubric)
        
        # تحديث بيانات معيار التقييم
        rubric.name = name
        rubric.description = description
        
        if rubric.save():
            flash('تم تحديث معيار التقييم بنجاح', 'success')
            return redirect(url_for('admin.list_rubrics'))
        else:
            flash('حدث خطأ أثناء تحديث معيار التقييم. يرجى المحاولة مرة أخرى.', 'error')
    
    return render_template('admin/edit_rubric.html', rubric=rubric)

@admin_bp.route('/rubrics/delete/<int:rubric_id>', methods=['POST'])
def delete_rubric(rubric_id):
    """حذف معيار تقييم"""
    # التحقق من تسجيل الدخول ودور المستخدم
    if 'user_id' not in session or session.get('user_role') != 'admin':
        flash('ليس لديك صلاحية الوصول إلى هذه الصفحة', 'error')
        return redirect(url_for('main.index'))
    
    # الحصول على معيار التقييم المراد حذفه
    rubric = Rubric.get_by_id(rubric_id)
    if not rubric:
        flash('معيار التقييم غير موجود', 'error')
        return redirect(url_for('admin.list_rubrics'))
    
    # حذف معيار التقييم
    if rubric.delete():
        flash('تم حذف معيار التقييم بنجاح', 'success')
    else:
        flash('حدث خطأ أثناء حذف معيار التقييم', 'error')
    
    return redirect(url_for('admin.list_rubrics'))

@admin_bp.route('/evaluations')
def list_evaluations():
    """صفحة إدارة التقييمات"""
    # التحقق من تسجيل الدخول ودور المستخدم
    if 'user_id' not in session or session.get('user_role') != 'admin':
        flash('ليس لديك صلاحية الوصول إلى هذه الصفحة', 'error')
        return redirect(url_for('main.index'))
    
    # الحصول على قائمة التقييمات
    evaluations = Evaluation.get_all()
    
    return render_template('admin/evaluations.html', evaluations=evaluations)