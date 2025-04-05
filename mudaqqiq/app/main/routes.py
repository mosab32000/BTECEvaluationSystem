from datetime import datetime
from flask import render_template, flash, redirect, url_for, request, current_app, jsonify
from flask_login import current_user, login_required
from app.main import main
from app.models import Project, User, AuditResult, Notification, ActivityLog
from app.main.forms import ProfileForm
from app.utils import save_profile_image, log_activity
from app import db

@main.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()

@main.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    return render_template('index.html', title='الصفحة الرئيسية')

@main.route('/dashboard')
@login_required
def dashboard():
    # إحصائيات المستخدم
    if current_user.is_admin():
        # إحصائيات المدير
        total_users = User.query.count()
        total_projects = Project.query.count()
        pending_projects = Project.query.filter_by(status='قيد الانتظار').count()
        completed_audits = AuditResult.query.filter_by(status='مكتمل').count()
        
        recent_projects = Project.query.order_by(Project.submission_date.desc()).limit(5).all()
        recent_users = User.query.order_by(User.created_at.desc()).limit(5).all()
        recent_activity = ActivityLog.query.order_by(ActivityLog.timestamp.desc()).limit(10).all()
        
        return render_template(
            'admin/dashboard.html', 
            title='لوحة التحكم',
            total_users=total_users,
            total_projects=total_projects,
            pending_projects=pending_projects,
            completed_audits=completed_audits,
            recent_projects=recent_projects,
            recent_users=recent_users,
            recent_activity=recent_activity
        )
    else:
        # إحصائيات المستخدم العادي
        user_projects = Project.query.filter_by(user_id=current_user.id).count()
        pending_projects = Project.query.filter_by(user_id=current_user.id, status='قيد الانتظار').count()
        completed_projects = Project.query.filter_by(user_id=current_user.id, status='مكتمل').count()
        
        recent_projects = Project.query.filter_by(user_id=current_user.id).order_by(
            Project.submission_date.desc()).limit(5).all()
        
        recent_audits = AuditResult.query.join(Project).filter(
            Project.user_id == current_user.id,
            AuditResult.status == 'مكتمل'
        ).order_by(AuditResult.audit_date.desc()).limit(5).all()
        
        unread_notifications = Notification.query.filter_by(
            user_id=current_user.id,
            read=False
        ).count()
        
        return render_template(
            'dashboard.html',
            title='لوحة التحكم',
            user_projects=user_projects,
            pending_projects=pending_projects,
            completed_projects=completed_projects,
            recent_projects=recent_projects,
            recent_audits=recent_audits,
            unread_notifications=unread_notifications
        )

@main.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    form = ProfileForm()
    if form.validate_on_submit():
        if form.profile_image.data:
            picture_file = save_profile_image(form.profile_image.data)
            current_user.profile_image = picture_file
        
        current_user.full_name = form.full_name.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        
        log_activity(current_user, 'تحديث الملف الشخصي', ip_address=request.remote_addr)
        flash('تم تحديث ملفك الشخصي بنجاح!', 'success')
        return redirect(url_for('main.profile'))
    
    elif request.method == 'GET':
        form.full_name.data = current_user.full_name
        form.about_me.data = current_user.about_me
    
    return render_template('profile.html', title='الملف الشخصي', form=form)

@main.route('/notifications')
@login_required
def notifications():
    page = request.args.get('page', 1, type=int)
    notifications = Notification.query.filter_by(user_id=current_user.id).order_by(
        Notification.timestamp.desc()
    ).paginate(
        page=page, 
        per_page=current_app.config['PROJECTS_PER_PAGE'],
        error_out=False
    )
    
    # وضع علامة على الإشعارات كمقروءة
    unread = Notification.query.filter_by(user_id=current_user.id, read=False).all()
    for notification in unread:
        notification.read = True
    db.session.commit()
    
    return render_template(
        'notifications.html',
        title='الإشعارات',
        notifications=notifications
    )

@main.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    
    page = request.args.get('page', 1, type=int)
    projects = Project.query.filter_by(user_id=user.id).order_by(
        Project.submission_date.desc()
    ).paginate(
        page=page, 
        per_page=current_app.config['PROJECTS_PER_PAGE'],
        error_out=False
    )
    
    return render_template('user.html', user=user, projects=projects)

@main.route('/about')
def about():
    return render_template('about.html', title='عن المنصة')

@main.route('/contact')
def contact():
    return render_template('contact.html', title='اتصل بنا')
