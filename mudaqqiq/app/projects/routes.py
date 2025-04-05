from flask import render_template, redirect, url_for, flash, request, current_app, abort, send_from_directory
from flask_login import login_required, current_user
from app import db
from app.projects import projects
from app.projects.forms import ProjectForm, AuditForm
from app.models import Project, AuditCriteria, AuditResult, User
from app.utils import save_project_file, log_activity, create_notification
from datetime import datetime
import os

@projects.route('/')
@login_required
def index():
    page = request.args.get('page', 1, type=int)
    
    if current_user.is_admin():
        # المدراء يرون جميع المشاريع
        projects_list = Project.query.order_by(Project.submission_date.desc())
    else:
        # المستخدمون العاديون يرون مشاريعهم فقط
        projects_list = Project.query.filter_by(user_id=current_user.id).order_by(Project.submission_date.desc())
    
    projects_pagination = projects_list.paginate(
        page=page, 
        per_page=current_app.config['PROJECTS_PER_PAGE'],
        error_out=False
    )
    
    return render_template(
        'projects/list.html',
        title='المشاريع',
        projects=projects_pagination
    )

@projects.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    form = ProjectForm()
    
    if form.validate_on_submit():
        project = Project(
            title=form.title.data,
            description=form.description.data,
            project_type=form.project_type.data,
            user_id=current_user.id
        )
        
        db.session.add(project)
        db.session.commit()
        
        if form.project_file.data:
            file_path = save_project_file(form.project_file.data, project)
            project.file_path = file_path
            db.session.commit()
        
        log_activity(current_user, 'إنشاء مشروع جديد', details=f'مشروع: {project.title}', ip_address=request.remote_addr)
        
        # إشعار للمستخدم
        create_notification(
            current_user.id,
            f'تم إنشاء المشروع "{project.title}" بنجاح. سيتم مراجعته قريبًا.',
            'success'
        )
        
        # إشعار للمدراء
        admin_users = User.query.filter(User.roles.any(name='admin')).all()
        for admin in admin_users:
            create_notification(
                admin.id,
                f'تم إضافة مشروع جديد "{project.title}" بواسطة {current_user.username}.',
                'info'
            )
        
        flash('تم إنشاء المشروع بنجاح!', 'success')
        return redirect(url_for('projects.view', id=project.id))
    
    return render_template(
        'projects/create.html',
        title='إنشاء مشروع جديد',
        form=form
    )

@projects.route('/<int:id>')
@login_required
def view(id):
    project = Project.query.get_or_404(id)
    
    # التحقق من الصلاحيات - يمكن للمدراء رؤية أي مشروع
    if project.user_id != current_user.id and not current_user.is_admin():
        abort(403)
    
    # الحصول على نتائج التدقيق
    audit_results = AuditResult.query.filter_by(project_id=project.id).order_by(AuditResult.audit_date.desc()).all()
    
    return render_template(
        'projects/view.html',
        title=project.title,
        project=project,
        audit_results=audit_results
    )

@projects.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit(id):
    project = Project.query.get_or_404(id)
    
    # التحقق من الصلاحيات
    if project.user_id != current_user.id:
        abort(403)
    
    # لا يمكن تعديل المشاريع التي تم الانتهاء منها
    if project.status in ['مكتمل', 'مرفوض']:
        flash('لا يمكن تعديل هذا المشروع لأنه مكتمل أو مرفوض.', 'warning')
        return redirect(url_for('projects.view', id=project.id))
    
    form = ProjectForm()
    
    if form.validate_on_submit():
        project.title = form.title.data
        project.description = form.description.data
        project.project_type = form.project_type.data
        
        if form.project_file.data:
            # حذف الملف القديم إذا وجد
            if project.file_path:
                old_file_path = os.path.join(current_app.root_path, 'static', project.file_path)
                if os.path.exists(old_file_path):
                    os.remove(old_file_path)
            
            file_path = save_project_file(form.project_file.data, project)
            project.file_path = file_path
        
        db.session.commit()
        
        log_activity(current_user, 'تعديل مشروع', details=f'مشروع: {project.title}', ip_address=request.remote_addr)
        flash('تم تحديث المشروع بنجاح!', 'success')
        return redirect(url_for('projects.view', id=project.id))
    
    elif request.method == 'GET':
        form.title.data = project.title
        form.description.data = project.description
        form.project_type.data = project.project_type
    
    return render_template(
        'projects/create.html',
        title='تعديل المشروع',
        form=form,
        project=project
    )

@projects.route('/<int:id>/delete', methods=['POST'])
@login_required
def delete(id):
    project = Project.query.get_or_404(id)
    
    # التحقق من الصلاحيات
    if project.user_id != current_user.id and not current_user.is_admin():
        abort(403)
    
    # حذف الملف إذا وجد
    if project.file_path:
        file_path = os.path.join(current_app.root_path, 'static', project.file_path)
        if os.path.exists(file_path):
            os.remove(file_path)
    
    db.session.delete(project)
    db.session.commit()
    
    log_activity(current_user, 'حذف مشروع', details=f'مشروع: {project.title}', ip_address=request.remote_addr)
    flash('تم حذف المشروع بنجاح.', 'success')
    return redirect(url_for('projects.index'))

@projects.route('/file/<int:id>')
@login_required
def download_file(id):
    project = Project.query.get_or_404(id)
    
    # التحقق من الصلاحيات
    if project.user_id != current_user.id and not current_user.is_admin():
        abort(403)
    
    if not project.file_path:
        flash('لا يوجد ملف مرفق لهذا المشروع.', 'warning')
        return redirect(url_for('projects.view', id=project.id))
    
    # استخراج اسم المجلد واسم الملف
    file_dir = os.path.dirname(project.file_path)
    file_name = os.path.basename(project.file_path)
    
    # الحصول على المسار المطلق للمجلد
    base_dir = os.path.join(current_app.root_path, 'static')
    
    return send_from_directory(os.path.join(base_dir, file_dir), file_name, as_attachment=True)

@projects.route('/<int:id>/audit', methods=['GET', 'POST'])
@login_required
def audit(id):
    project = Project.query.get_or_404(id)
    
    # يمكن للمدراء فقط إجراء التدقيق
    if not current_user.is_admin():
        abort(403)
    
    form = AuditForm()
    
    # تحميل معايير التدقيق للاختيار
    form.criteria.choices = [(c.id, c.name) for c in AuditCriteria.query.all()]
    
    if form.validate_on_submit():
        result = AuditResult(
            project_id=project.id,
            auditor_id=current_user.id,
            score=form.score.data,
            feedback=form.feedback.data,
            result_details={
                'criteria': [AuditCriteria.query.get(c_id).name for c_id in form.criteria.data],
                'notes': form.notes.data,
                'recommendations': form.recommendations.data
            },
            status='مكتمل'
        )
        
        db.session.add(result)
        
        # تحديث حالة المشروع
        project.status = 'مكتمل'
        project.completion_date = datetime.utcnow()
        
        db.session.commit()
        
        log_activity(
            current_user, 
            'إجراء تدقيق', 
            details=f'مشروع: {project.title}, نتيجة: {form.score.data}', 
            ip_address=request.remote_addr
        )
        
        # إشعار صاحب المشروع
        create_notification(
            project.user_id,
            f'تم الانتهاء من تدقيق مشروعك "{project.title}". يمكنك الآن مشاهدة النتيجة.',
            'success'
        )
        
        flash('تم تدقيق المشروع بنجاح!', 'success')
        return redirect(url_for('projects.view', id=project.id))
    
    return render_template(
        'projects/audit.html',
        title=f'تدقيق مشروع: {project.title}',
        form=form,
        project=project
    )
