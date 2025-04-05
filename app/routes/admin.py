"""
وحدة مسارات المشرف لنظام تقييم BTEC
"""

from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, current_app
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash

from app.extensions import db, limiter
from app.models.user import User
from app.models.rubric import Rubric
from app.models.evaluation import Evaluation

admin_blueprint = Blueprint('admin', __name__)


# وسيط للتحقق من صلاحيات المشرف
def admin_required(view):
    """وسيط للتحقق من صلاحيات المشرف"""
    @login_required
    def wrapped_view(*args, **kwargs):
        if current_user.role != 'admin':
            flash('ليس لديك صلاحيات كافية للوصول إلى هذه الصفحة.', 'error')
            return redirect(url_for('main.index'))
        return view(*args, **kwargs)
    
    # الحفاظ على اسم الدالة وتوثيقها
    wrapped_view.__name__ = view.__name__
    wrapped_view.__doc__ = view.__doc__
    
    return wrapped_view


@admin_blueprint.route('/')
@admin_required
def dashboard():
    """لوحة تحكم المشرف"""
    user_count = User.query.count()
    active_users = User.query.filter_by(is_active=True).count()
    evaluation_count = Evaluation.query.count()
    pending_evaluations = Evaluation.query.filter_by(status='pending').count()
    
    recent_users = User.query.order_by(User.created_at.desc()).limit(5).all()
    recent_evaluations = Evaluation.query.order_by(Evaluation.created_at.desc()).limit(5).all()
    
    return render_template(
        'admin/dashboard.html',
        user_count=user_count,
        active_users=active_users,
        evaluation_count=evaluation_count,
        pending_evaluations=pending_evaluations,
        recent_users=recent_users,
        recent_evaluations=recent_evaluations
    )


@admin_blueprint.route('/users')
@admin_required
def users():
    """إدارة المستخدمين"""
    users_list = User.query.all()
    return render_template('admin/users.html', users=users_list)


@admin_blueprint.route('/users/new', methods=['GET', 'POST'])
@admin_required
@limiter.limit("10/hour")
def new_user():
    """إنشاء مستخدم جديد"""
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        role = request.form.get('role')
        
        if not all([name, email, password, role]):
            flash('جميع الحقول مطلوبة.', 'error')
            return render_template('admin/new_user.html')
        
        user_exists = User.query.filter_by(email=email).first() is not None
        
        if user_exists:
            flash('البريد الإلكتروني مسجل بالفعل.', 'error')
            return render_template('admin/new_user.html')
        
        new_user = User(
            name=name,
            email=email,
            password_hash=generate_password_hash(password),
            role=role
        )
        
        db.session.add(new_user)
        db.session.commit()
        
        flash(f'تم إنشاء المستخدم {name} بنجاح.', 'success')
        return redirect(url_for('admin.users'))
    
    return render_template('admin/new_user.html')


@admin_blueprint.route('/users/edit/<int:user_id>', methods=['GET', 'POST'])
@admin_required
def edit_user(user_id):
    """تعديل مستخدم"""
    user = User.query.get_or_404(user_id)
    
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        role = request.form.get('role')
        is_active = 'is_active' in request.form
        password = request.form.get('password')
        
        if not all([name, email, role]):
            flash('الاسم والبريد الإلكتروني والدور مطلوبة.', 'error')
            return render_template('admin/edit_user.html', user=user)
        
        # التحقق من البريد الإلكتروني الفريد (إذا تم تغييره)
        if email != user.email and User.query.filter_by(email=email).first():
            flash('البريد الإلكتروني مسجل بالفعل.', 'error')
            return render_template('admin/edit_user.html', user=user)
        
        user.name = name
        user.email = email
        user.role = role
        user.is_active = is_active
        
        if password:  # تحديث كلمة المرور فقط إذا تم تقديمها
            user.password_hash = generate_password_hash(password)
        
        db.session.commit()
        
        flash('تم تحديث بيانات المستخدم بنجاح.', 'success')
        return redirect(url_for('admin.users'))
    
    return render_template('admin/edit_user.html', user=user)


@admin_blueprint.route('/users/delete/<int:user_id>', methods=['POST'])
@admin_required
def delete_user(user_id):
    """حذف مستخدم"""
    user = User.query.get_or_404(user_id)
    
    if user.id == current_user.id:
        flash('لا يمكنك حذف حسابك الخاص.', 'error')
        return redirect(url_for('admin.users'))
    
    db.session.delete(user)
    db.session.commit()
    
    flash('تم حذف المستخدم بنجاح.', 'success')
    return redirect(url_for('admin.users'))


@admin_blueprint.route('/rubrics')
@admin_required
def rubrics():
    """إدارة معايير التقييم"""
    rubrics_list = Rubric.query.all()
    return render_template('admin/rubrics.html', rubrics=rubrics_list)


@admin_blueprint.route('/evaluations')
@admin_required
def evaluations():
    """إدارة التقييمات"""
    evaluations_list = Evaluation.query.all()
    return render_template('admin/evaluations.html', evaluations=evaluations_list)


@admin_blueprint.route('/system')
@admin_required
def system():
    """إعدادات النظام"""
    return render_template('admin/system.html')


@admin_blueprint.route('/logs')
@admin_required
def logs():
    """سجلات النظام"""
    return render_template('admin/logs.html')


@admin_blueprint.route('/api/users', methods=['GET'])
@admin_required
def api_users():
    """واجهة برمجة تطبيقات للمستخدمين"""
    users_list = User.query.all()
    
    result = []
    for user in users_list:
        result.append({
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "role": user.role,
            "is_active": user.is_active,
            "last_login": user.last_login.isoformat() if user.last_login else None,
            "created_at": user.created_at.isoformat() if user.created_at else None
        })
    
    return jsonify(result), 200


@admin_blueprint.route('/api/system/stats', methods=['GET'])
@admin_required
def api_system_stats():
    """إحصائيات النظام"""
    user_count = User.query.count()
    teacher_count = User.query.filter_by(role='teacher').count()
    student_count = User.query.filter_by(role='student').count()
    evaluation_count = Evaluation.query.count()
    rubric_count = Rubric.query.count()
    
    return jsonify({
        "users": {
            "total": user_count,
            "teachers": teacher_count,
            "students": student_count,
            "admins": User.query.filter_by(role='admin').count()
        },
        "evaluations": {
            "total": evaluation_count,
            "pending": Evaluation.query.filter_by(status='pending').count(),
            "completed": Evaluation.query.filter_by(status='completed').count(),
            "rejected": Evaluation.query.filter_by(status='rejected').count()
        },
        "rubrics": rubric_count,
        "system": {
            "version": current_app.config.get('VERSION', '1.0.0'),
            "env": current_app.config.get('FLASK_ENV', 'production')
        }
    }), 200