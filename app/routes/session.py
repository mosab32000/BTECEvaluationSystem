"""
مسارات إدارة الحصص التفاعلية في نظام تقييم BTEC
"""

import logging
import datetime
from flask import render_template, redirect, url_for, request, flash, session as flask_session, jsonify, abort
from app.routes import main_bp

from app.models.session import Session
from app.models.classroom import Classroom
from app.models.participant import Participant
from app.models.user import User

logger = logging.getLogger(__name__)

@main_bp.route('/sessions')
def list_sessions():
    """صفحة عرض الحصص التفاعلية"""
    # التحقق من تسجيل الدخول
    if 'user_id' not in flask_session:
        flash('يجب تسجيل الدخول للوصول إلى هذه الصفحة', 'error')
        return redirect(url_for('auth.login'))
    
    # الحصول على الحصص التفاعلية حسب دور المستخدم
    user = User.get_by_id(flask_session['user_id'])
    if not user:
        flask_session.clear()
        flash('حدث خطأ في جلستك. يرجى تسجيل الدخول مرة أخرى.', 'error')
        return redirect(url_for('auth.login'))
    
    if user.role == 'admin':
        # المسؤول يرى جميع الحصص التفاعلية
        sessions = Session.query.all()
    elif user.role == 'teacher':
        # المدرس يرى الحصص التفاعلية التي يقوم بتدريسها
        sessions = Session.get_by_teacher(user.id)
    else:
        # الطالب يرى الحصص التفاعلية النشطة والقادمة
        upcoming_sessions = Session.get_upcoming(48)  # الحصص القادمة خلال 48 ساعة
        active_sessions = Session.get_active()
        sessions = upcoming_sessions + active_sessions
    
    return render_template('session/index.html', sessions=sessions, user=user)

@main_bp.route('/sessions/<int:session_id>')
def view_session(session_id):
    """صفحة عرض تفاصيل الحصة التفاعلية"""
    # التحقق من تسجيل الدخول
    if 'user_id' not in flask_session:
        flash('يجب تسجيل الدخول للوصول إلى هذه الصفحة', 'error')
        return redirect(url_for('auth.login'))
    
    # الحصول على الحصة التفاعلية
    interactive_session = Session.get_by_id(session_id)
    if not interactive_session:
        flash('الحصة التفاعلية غير موجودة', 'error')
        return redirect(url_for('main.list_sessions'))
    
    # الحصول على المعلومات المرتبطة
    classroom = Classroom.get_by_id(interactive_session.classroom_id)
    teacher = User.get_by_id(interactive_session.teacher_id)
    
    # التحقق مما إذا كان المستخدم مشارك بالفعل
    is_participant = False
    if 'user_id' in flask_session:
        participant = Participant.get_by_session_and_user(session_id, flask_session['user_id'])
        is_participant = participant is not None
    
    return render_template('session/view.html', 
                           session=interactive_session, 
                           classroom=classroom,
                           teacher=teacher,
                           is_participant=is_participant)

@main_bp.route('/sessions/create', methods=['GET', 'POST'])
def create_session():
    """صفحة إنشاء حصة تفاعلية جديدة"""
    # التحقق من تسجيل الدخول ودور المستخدم
    if 'user_id' not in flask_session or flask_session.get('user_role') not in ['admin', 'teacher']:
        flash('ليس لديك صلاحية للوصول إلى هذه الصفحة', 'error')
        return redirect(url_for('main.index'))
    
    # الحصول على الفصول الدراسية المتاحة للمدرس
    user_id = flask_session['user_id']
    if flask_session.get('user_role') == 'admin':
        classrooms = Classroom.get_all()
    else:
        classrooms = Classroom.get_by_teacher(user_id)
    
    if not classrooms:
        flash('يجب إنشاء فصل دراسي أولاً قبل إنشاء حصة تفاعلية', 'warning')
        return redirect(url_for('main.create_classroom'))
    
    if request.method == 'POST':
        # الحصول على البيانات من النموذج
        title = request.form.get('title')
        description = request.form.get('description')
        classroom_id = request.form.get('classroom_id', type=int)
        start_time_str = request.form.get('start_time')
        end_time_str = request.form.get('end_time')
        session_type = request.form.get('session_type')
        session_url = request.form.get('session_url')
        meeting_id = request.form.get('meeting_id', '')
        password = request.form.get('password', '')
        
        # التحقق من صحة البيانات
        if not title or not classroom_id or not start_time_str or not end_time_str or not session_type:
            flash('جميع الحقول المطلوبة يجب ملؤها', 'error')
            return render_template('session/create.html', classrooms=classrooms)
        
        # تحويل أوقات البدء والانتهاء
        try:
            start_time = datetime.datetime.fromisoformat(start_time_str)
            end_time = datetime.datetime.fromisoformat(end_time_str)
        except ValueError:
            flash('تنسيق الوقت غير صحيح', 'error')
            return render_template('session/create.html', classrooms=classrooms)
        
        # التحقق من أن وقت البدء قبل وقت الانتهاء
        if start_time >= end_time:
            flash('يجب أن يكون وقت البدء قبل وقت الانتهاء', 'error')
            return render_template('session/create.html', classrooms=classrooms)
        
        # إنشاء حصة تفاعلية جديدة
        interactive_session = Session(
            title=title,
            description=description,
            classroom_id=classroom_id,
            teacher_id=user_id,
            start_time=start_time,
            end_time=end_time,
            session_type=session_type,
            session_url=session_url,
            meeting_id=meeting_id,
            password=password,
            status='scheduled'
        )
        
        if interactive_session.save():
            flash('تم إنشاء الحصة التفاعلية بنجاح', 'success')
            return redirect(url_for('main.view_session', session_id=interactive_session.id))
        else:
            flash('حدث خطأ أثناء إنشاء الحصة التفاعلية', 'error')
    
    return render_template('session/create.html', classrooms=classrooms)

@main_bp.route('/sessions/<int:session_id>/edit', methods=['GET', 'POST'])
def edit_session(session_id):
    """صفحة تعديل حصة تفاعلية"""
    # التحقق من تسجيل الدخول ودور المستخدم
    if 'user_id' not in flask_session or flask_session.get('user_role') not in ['admin', 'teacher']:
        flash('ليس لديك صلاحية للوصول إلى هذه الصفحة', 'error')
        return redirect(url_for('main.index'))
    
    # الحصول على الحصة التفاعلية
    interactive_session = Session.get_by_id(session_id)
    if not interactive_session:
        flash('الحصة التفاعلية غير موجودة', 'error')
        return redirect(url_for('main.list_sessions'))
    
    # التحقق من صلاحية الوصول
    if flask_session.get('user_role') != 'admin' and interactive_session.teacher_id != flask_session['user_id']:
        flash('ليس لديك صلاحية لتعديل هذه الحصة التفاعلية', 'error')
        return redirect(url_for('main.list_sessions'))
    
    # الحصول على الفصول الدراسية المتاحة
    if flask_session.get('user_role') == 'admin':
        classrooms = Classroom.get_all()
    else:
        classrooms = Classroom.get_by_teacher(flask_session['user_id'])
    
    if request.method == 'POST':
        # الحصول على البيانات من النموذج
        title = request.form.get('title')
        description = request.form.get('description')
        classroom_id = request.form.get('classroom_id', type=int)
        start_time_str = request.form.get('start_time')
        end_time_str = request.form.get('end_time')
        session_type = request.form.get('session_type')
        session_url = request.form.get('session_url')
        meeting_id = request.form.get('meeting_id', '')
        password = request.form.get('password', '')
        status = request.form.get('status')
        
        # التحقق من صحة البيانات
        if not title or not classroom_id or not start_time_str or not end_time_str or not session_type or not status:
            flash('جميع الحقول المطلوبة يجب ملؤها', 'error')
            return render_template('session/edit.html', session=interactive_session, classrooms=classrooms)
        
        # تحويل أوقات البدء والانتهاء
        try:
            start_time = datetime.datetime.fromisoformat(start_time_str)
            end_time = datetime.datetime.fromisoformat(end_time_str)
        except ValueError:
            flash('تنسيق الوقت غير صحيح', 'error')
            return render_template('session/edit.html', session=interactive_session, classrooms=classrooms)
        
        # التحقق من أن وقت البدء قبل وقت الانتهاء
        if start_time >= end_time:
            flash('يجب أن يكون وقت البدء قبل وقت الانتهاء', 'error')
            return render_template('session/edit.html', session=interactive_session, classrooms=classrooms)
        
        # تحديث الحصة التفاعلية
        interactive_session.title = title
        interactive_session.description = description
        interactive_session.classroom_id = classroom_id
        interactive_session.start_time = start_time
        interactive_session.end_time = end_time
        interactive_session.session_type = session_type
        interactive_session.session_url = session_url
        interactive_session.meeting_id = meeting_id
        
        # تحديث كلمة المرور فقط إذا تم تغييرها
        if password:
            interactive_session.password = password
        
        interactive_session.status = status
        
        if interactive_session.save():
            flash('تم تحديث الحصة التفاعلية بنجاح', 'success')
            return redirect(url_for('main.view_session', session_id=interactive_session.id))
        else:
            flash('حدث خطأ أثناء تحديث الحصة التفاعلية', 'error')
    
    return render_template('session/edit.html', session=interactive_session, classrooms=classrooms)

@main_bp.route('/sessions/<int:session_id>/join', methods=['POST'])
def join_session(session_id):
    """الانضمام إلى حصة تفاعلية"""
    # التحقق من تسجيل الدخول
    if 'user_id' not in flask_session:
        flash('يجب تسجيل الدخول للوصول إلى هذه الصفحة', 'error')
        return redirect(url_for('auth.login'))
    
    # الحصول على الحصة التفاعلية
    interactive_session = Session.get_by_id(session_id)
    if not interactive_session:
        flash('الحصة التفاعلية غير موجودة', 'error')
        return redirect(url_for('main.list_sessions'))
    
    # التحقق من حالة الحصة
    if interactive_session.status != 'active':
        flash('لا يمكن الانضمام إلى الحصة، الحصة غير نشطة حاليًا', 'error')
        return redirect(url_for('main.view_session', session_id=session_id))
    
    # التحقق من عدم الانضمام بالفعل
    existing_participant = Participant.get_by_session_and_user(session_id, flask_session['user_id'])
    if existing_participant:
        # تحديث وقت الانضمام إذا انضم سابقًا ثم غادر
        if existing_participant.leave_time:
            existing_participant.join_time = datetime.datetime.utcnow()
            existing_participant.leave_time = None
            if existing_participant.save():
                flash('تم الانضمام مرة أخرى إلى الحصة التفاعلية', 'success')
            else:
                flash('حدث خطأ أثناء تحديث حالة الانضمام', 'error')
        else:
            flash('أنت بالفعل منضم إلى هذه الحصة التفاعلية', 'info')
        
        # توجيه إلى صفحة الحصة التفاعلية (أو رابط خارجي إذا كان متاحًا)
        if interactive_session.session_url:
            return redirect(interactive_session.session_url)
        else:
            return redirect(url_for('main.view_session', session_id=session_id))
    
    # إنشاء مشارك جديد
    participant = Participant(
        session_id=session_id,
        user_id=flask_session['user_id'],
        join_time=datetime.datetime.utcnow(),
        attendance_status='present'
    )
    
    if participant.save():
        flash('تم الانضمام إلى الحصة التفاعلية بنجاح', 'success')
        
        # توجيه إلى صفحة الحصة التفاعلية (أو رابط خارجي إذا كان متاحًا)
        if interactive_session.session_url:
            return redirect(interactive_session.session_url)
        else:
            return redirect(url_for('main.view_session', session_id=session_id))
    else:
        flash('حدث خطأ أثناء الانضمام إلى الحصة التفاعلية', 'error')
        return redirect(url_for('main.view_session', session_id=session_id))

@main_bp.route('/sessions/<int:session_id>/leave', methods=['POST'])
def leave_session(session_id):
    """مغادرة حصة تفاعلية"""
    # التحقق من تسجيل الدخول
    if 'user_id' not in flask_session:
        flash('يجب تسجيل الدخول للوصول إلى هذه الصفحة', 'error')
        return redirect(url_for('auth.login'))
    
    # التحقق من الانضمام بالفعل
    participant = Participant.get_by_session_and_user(session_id, flask_session['user_id'])
    if not participant:
        flash('أنت غير منضم إلى هذه الحصة التفاعلية', 'error')
        return redirect(url_for('main.list_sessions'))
    
    # تحديث وقت المغادرة
    participant.leave_time = datetime.datetime.utcnow()
    
    if participant.save():
        flash('تم تسجيل مغادرتك للحصة التفاعلية', 'success')
    else:
        flash('حدث خطأ أثناء تسجيل المغادرة', 'error')
    
    return redirect(url_for('main.list_sessions'))

@main_bp.route('/sessions/<int:session_id>/delete', methods=['POST'])
def delete_session(session_id):
    """حذف حصة تفاعلية"""
    # التحقق من تسجيل الدخول ودور المستخدم
    if 'user_id' not in flask_session or flask_session.get('user_role') not in ['admin', 'teacher']:
        flash('ليس لديك صلاحية للوصول إلى هذه الصفحة', 'error')
        return redirect(url_for('main.index'))
    
    # الحصول على الحصة التفاعلية
    interactive_session = Session.get_by_id(session_id)
    if not interactive_session:
        flash('الحصة التفاعلية غير موجودة', 'error')
        return redirect(url_for('main.list_sessions'))
    
    # التحقق من صلاحية الوصول
    if flask_session.get('user_role') != 'admin' and interactive_session.teacher_id != flask_session['user_id']:
        flash('ليس لديك صلاحية لحذف هذه الحصة التفاعلية', 'error')
        return redirect(url_for('main.list_sessions'))
    
    # حذف الحصة التفاعلية
    if interactive_session.delete():
        flash('تم حذف الحصة التفاعلية بنجاح', 'success')
    else:
        flash('حدث خطأ أثناء حذف الحصة التفاعلية', 'error')
    
    return redirect(url_for('main.list_sessions'))