from flask import render_template, redirect, url_for, flash, request, current_app, abort
from flask_login import login_required, current_user
from app import db
from app.admin import admin
from app.models import User, Role, Project, AuditCriteria, AuditResult, ActivityLog
from app.admin.forms import AuditCriteriaForm, UserRoleForm
from app.utils import log_activity, create_notification
from functools import wraps

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin():
            abort(403)
        return f(*args, **kwargs)
    return decorated_function

@admin.route('/')
@login_required
@admin_required
def index():
    return redirect(url_for('main.dashboard'))

@admin.route('/users')
@login_required
@admin_required
def users():
    page = request.args.get('page', 1, type=int)
    users_list = User.query.order_by(User.username).paginate(
        page=page, 
        per_page=current_app.config['PROJECTS_PER_PAGE'],
        error_out=False
    )
    
    return render_template(
        'admin/users.html',
        title='إدارة المستخدمين',
        users=users_list
    )

@admin.route('/user/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_user(id):
    user = User.query.get_or_404(id)
    form = UserRoleForm()
    
    # تحميل جميع الأدوار للاختيار
    form.roles.choices = [(role.id, role.name) for role in Role.query.all()]
    
    if form.validate_on_submit():
        user.is_active = form.is_active.data
        
        # تحديث الأدوار
        user.roles = []
        for role_id in form.roles.data:
            role = Role.query.get(role_id)
            if role:
                user.roles.append(role)
        
        db.session.commit()
        
        log_activity(
            current_user, 
            'تعديل حساب مستخدم', 
            details=f'مستخدم: {user.username}', 
            ip_address=request.remote_addr
        )
        
        create_notification(
            user.id,
            'تم تحديث صلاحيات حسابك من قبل مدير النظام.',
            'info'
        )
        
        flash(f'تم تحديث حساب المستخدم {user.username} بنجاح.', 'success')
        return redirect(url_for('admin.users'))
    
    elif request.method == 'GET':
        form.is_active.data = user.is_active
        form.roles.data = [role.id for role in user.roles]
    
    return render_template(
        'admin/edit_user.html',
        title='تعديل حساب مستخدم',
        form=form,
        user=user
    )

@admin.route('/audit_criteria')
@login_required
@admin_required
def audit_criteria():
    page = request.args.get('page', 1, type=int)
    criteria_list = AuditCriteria.query.order_by(AuditCriteria.name).paginate(
        page=page, 
        per_page=current_app.config['PROJECTS_PER_PAGE'],
        error_out=False
    )
    
    return render_template(
        'admin/audit_criteria.html',
        title='معايير التدقيق',
        criteria=criteria_list
    )

@admin.route('/audit_criteria/create', methods=['GET', 'POST'])
@login_required
@admin_required
def create_audit_criteria():
    form = AuditCriteriaForm()
    
    # قائمة الفئات المتاحة
    form.category.choices = [(cat, cat) for cat in current_app.config['AUDIT_CRITERIA_CATEGORIES']]
    
    if form.validate_on_submit():
        criteria = AuditCriteria(
            name=form.name.data,
            description=form.description.data,
            category=form.category.data,
            weight=form.weight.data
        )
        
        db.session.add(criteria)
        db.session.commit()
        
        log_activity(
            current_user, 
            'إنشاء معيار تدقيق جديد', 
            details=f'معيار: {criteria.name}', 
            ip_address=request.remote_addr
        )
        
        flash('تم إنشاء معيار التدقيق بنجاح!', 'success')
        return redirect(url_for('admin.audit_criteria'))
    
    return render_template(
        'admin/create_criteria.html',
        title='إنشاء معيار تدقيق جديد',
        form=form
    )

@admin.route('/audit_criteria/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_audit_criteria(id):
    criteria = AuditCriteria.query.get_or_404(id)
    form = AuditCriteriaForm()
    
    # قائمة الفئات المتاحة
    form.category.choices = [(cat, cat) for cat in current_app.config['AUDIT_CRITERIA_CATEGORIES']]
    
    if form.validate_on_submit():
        criteria.name = form.name.data
        criteria.description = form.description.data
        criteria.category = form.category.data
        criteria.weight = form.weight.data
        
        db.session.commit()
        
        log_activity(
            current_user, 
            'تعديل معيار تدقيق', 
            details=f'معيار: {criteria.name}', 
            ip_address=request.remote_addr
        )
        
        flash('تم تحديث معيار التدقيق بنجاح!', 'success')
        return redirect(url_for('admin.audit_criteria'))
    
    elif request.method == 'GET':
        form.name.data = criteria.name
        form.description.data = criteria.description
        form.category.data = criteria.category
        form.weight.data = criteria.weight
    
    return render_template(
        'admin/create_criteria.html',
        title='تعديل معيار تدقيق',
        form=form,
        criteria=criteria
    )

@admin.route('/audit_criteria/<int:id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_audit_criteria(id):
    criteria = AuditCriteria.query.get_or_404(id)
    
    # التحقق من عدم استخدام المعيار في أي نتائج تدقيق
    # هذا يتطلب تعديل الكود إذا كانت هناك علاقة مباشرة بين نتائج التدقيق ومعايير التدقيق
    
    db.session.delete(criteria)
    db.session.commit()
    
    log_activity(
        current_user, 
        'حذف معيار تدقيق', 
        details=f'معيار: {criteria.name}', 
        ip_address=request.remote_addr
    )
    
    flash('تم حذف معيار التدقيق بنجاح.', 'success')
    return redirect(url_for('admin.audit_criteria'))

@admin.route('/activity_logs')
@login_required
@admin_required
def activity_logs():
    page = request.args.get('page', 1, type=int)
    logs = ActivityLog.query.order_by(ActivityLog.timestamp.desc()).paginate(
        page=page, 
        per_page=current_app.config['PROJECTS_PER_PAGE'],
        error_out=False
    )
    
    return render_template(
        'admin/activity_logs.html',
        title='سجلات النشاط',
        logs=logs
    )

@admin.route('/settings')
@login_required
@admin_required
def settings():
    return render_template(
        'admin/settings.html',
        title='إعدادات النظام'
    )

@admin.route('/reports')
@login_required
@admin_required
def reports():
    # إحصائيات عامة للتقارير
    total_users = User.query.count()
    total_projects = Project.query.count()
    completed_projects = Project.query.filter_by(status='مكتمل').count()
    pending_projects = Project.query.filter_by(status='قيد الانتظار').count()
    
    # متوسط درجات التقييم
    avg_score = db.session.query(db.func.avg(AuditResult.score)).scalar() or 0
    
    # عدد المشاريع حسب النوع
    projects_by_type = db.session.query(
        Project.project_type, 
        db.func.count(Project.id)
    ).group_by(Project.project_type).all()
    
    return render_template(
        'admin/reports.html',
        title='التقارير والإحصائيات',
        total_users=total_users,
        total_projects=total_projects,
        completed_projects=completed_projects,
        pending_projects=pending_projects,
        avg_score=round(avg_score, 2),
        projects_by_type=projects_by_type
    )
