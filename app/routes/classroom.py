"""
مسارات إدارة الفصول الدراسية في نظام تقييم BTEC
"""

import logging
from flask import render_template, redirect, url_for, request, flash, session, jsonify, abort
from app.routes import main_bp

from app.models.classroom import Classroom
from app.models.user import User

logger = logging.getLogger(__name__)

@main_bp.route('/classrooms')
def list_classrooms():
    """صفحة عرض الفصول الدراسية"""
    # التحقق من تسجيل الدخول
    if 'user_id' not in session:
        flash('يجب تسجيل الدخول للوصول إلى هذه الصفحة', 'error')
        return redirect(url_for('auth.login'))
    
    # الحصول على الفصول الدراسية حسب دور المستخدم
    user = User.get_by_id(session['user_id'])
    if not user:
        session.clear()
        flash('حدث خطأ في جلستك. يرجى تسجيل الدخول مرة أخرى.', 'error')
        return redirect(url_for('auth.login'))
    
    if user.role == 'admin':
        # المسؤول يرى جميع الفصول الدراسية
        classrooms = Classroom.get_all()
    elif user.role == 'teacher':
        # المدرس يرى الفصول الدراسية التي يدرسها
        classrooms = Classroom.get_by_teacher(user.id)
    else:
        # الطالب يرى الفصول الدراسية المتاحة (يمكن تطوير هذا لاحقًا للاشتراك في الفصول)
        classrooms = Classroom.get_active()
    
    return render_template('classroom/index.html', classrooms=classrooms, user=user)

@main_bp.route('/classrooms/<int:classroom_id>')
def view_classroom(classroom_id):
    """صفحة عرض تفاصيل الفصل الدراسي"""
    # التحقق من تسجيل الدخول
    if 'user_id' not in session:
        flash('يجب تسجيل الدخول للوصول إلى هذه الصفحة', 'error')
        return redirect(url_for('auth.login'))
    
    # الحصول على الفصل الدراسي
    classroom = Classroom.get_by_id(classroom_id)
    if not classroom:
        flash('الفصل الدراسي غير موجود', 'error')
        return redirect(url_for('main.list_classrooms'))
    
    # الحصول على المعلومات المرتبطة
    teacher = User.get_by_id(classroom.teacher_id)
    
    return render_template('classroom/view.html', classroom=classroom, teacher=teacher)

@main_bp.route('/classrooms/create', methods=['GET', 'POST'])
def create_classroom():
    """صفحة إنشاء فصل دراسي جديد"""
    # التحقق من تسجيل الدخول ودور المستخدم
    if 'user_id' not in session or session.get('user_role') not in ['admin', 'teacher']:
        flash('ليس لديك صلاحية للوصول إلى هذه الصفحة', 'error')
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        # الحصول على البيانات من النموذج
        name = request.form.get('name')
        description = request.form.get('description')
        schedule = request.form.get('schedule')
        course_code = request.form.get('course_code')
        max_students = request.form.get('max_students', type=int)
        
        # التحقق من صحة البيانات
        if not name or not course_code:
            flash('اسم الفصل ورمز المساق مطلوبان', 'error')
            return render_template('classroom/create.html')
        
        # إنشاء فصل دراسي جديد
        classroom = Classroom(
            name=name,
            description=description,
            schedule=schedule,
            teacher_id=session['user_id'],
            course_code=course_code,
            max_students=max_students,
            is_active=True
        )
        
        if classroom.save():
            flash('تم إنشاء الفصل الدراسي بنجاح', 'success')
            return redirect(url_for('main.view_classroom', classroom_id=classroom.id))
        else:
            flash('حدث خطأ أثناء إنشاء الفصل الدراسي', 'error')
    
    return render_template('classroom/create.html')

@main_bp.route('/classrooms/<int:classroom_id>/edit', methods=['GET', 'POST'])
def edit_classroom(classroom_id):
    """صفحة تعديل فصل دراسي"""
    # التحقق من تسجيل الدخول ودور المستخدم
    if 'user_id' not in session or session.get('user_role') not in ['admin', 'teacher']:
        flash('ليس لديك صلاحية للوصول إلى هذه الصفحة', 'error')
        return redirect(url_for('main.index'))
    
    # الحصول على الفصل الدراسي
    classroom = Classroom.get_by_id(classroom_id)
    if not classroom:
        flash('الفصل الدراسي غير موجود', 'error')
        return redirect(url_for('main.list_classrooms'))
    
    # التحقق من صلاحية الوصول
    if session.get('user_role') != 'admin' and classroom.teacher_id != session['user_id']:
        flash('ليس لديك صلاحية لتعديل هذا الفصل الدراسي', 'error')
        return redirect(url_for('main.list_classrooms'))
    
    if request.method == 'POST':
        # الحصول على البيانات من النموذج
        name = request.form.get('name')
        description = request.form.get('description')
        schedule = request.form.get('schedule')
        course_code = request.form.get('course_code')
        max_students = request.form.get('max_students', type=int)
        is_active = 'is_active' in request.form  # للحصول على قيمة مربع الاختيار
        
        # التحقق من صحة البيانات
        if not name or not course_code:
            flash('اسم الفصل ورمز المساق مطلوبان', 'error')
            return render_template('classroom/edit.html', classroom=classroom)
        
        # تحديث الفصل الدراسي
        classroom.name = name
        classroom.description = description
        classroom.schedule = schedule
        classroom.course_code = course_code
        classroom.max_students = max_students
        classroom.is_active = is_active
        
        if classroom.save():
            flash('تم تحديث الفصل الدراسي بنجاح', 'success')
            return redirect(url_for('main.view_classroom', classroom_id=classroom.id))
        else:
            flash('حدث خطأ أثناء تحديث الفصل الدراسي', 'error')
    
    return render_template('classroom/edit.html', classroom=classroom)

@main_bp.route('/classrooms/<int:classroom_id>/delete', methods=['POST'])
def delete_classroom(classroom_id):
    """حذف فصل دراسي"""
    # التحقق من تسجيل الدخول ودور المستخدم
    if 'user_id' not in session or session.get('user_role') not in ['admin', 'teacher']:
        flash('ليس لديك صلاحية للوصول إلى هذه الصفحة', 'error')
        return redirect(url_for('main.index'))
    
    # الحصول على الفصل الدراسي
    classroom = Classroom.get_by_id(classroom_id)
    if not classroom:
        flash('الفصل الدراسي غير موجود', 'error')
        return redirect(url_for('main.list_classrooms'))
    
    # التحقق من صلاحية الوصول
    if session.get('user_role') != 'admin' and classroom.teacher_id != session['user_id']:
        flash('ليس لديك صلاحية لحذف هذا الفصل الدراسي', 'error')
        return redirect(url_for('main.list_classrooms'))
    
    # حذف الفصل الدراسي
    if classroom.delete():
        flash('تم حذف الفصل الدراسي بنجاح', 'success')
    else:
        flash('حدث خطأ أثناء حذف الفصل الدراسي', 'error')
    
    return redirect(url_for('main.list_classrooms'))