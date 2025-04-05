"""
مسارات المسؤول في نظام تقييم BTEC
"""
import logging
import json
from datetime import datetime
import os

from flask import Blueprint, request, jsonify, render_template, redirect, url_for, flash, current_app, abort
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash

from app.models.user import User
from app.models.rubric import Rubric
from app.models.evaluation import Evaluation

# تهيئة السجل
logger = logging.getLogger(__name__)

# إنشاء Blueprint
bp = Blueprint('admin', __name__, url_prefix='/admin')

# دالة للتحقق من صلاحية المسؤول
def admin_required(func):
    """
    دالة للتحقق من صلاحية المسؤول
    """
    def wrapper(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'admin':
            flash("لا تملك صلاحية الوصول لهذه الصفحة", "error")
            return redirect(url_for('index'))
        return func(*args, **kwargs)
    
    wrapper.__name__ = func.__name__
    return wrapper

@bp.route('/')
@login_required
@admin_required
def admin_dashboard():
    """
    لوحة تحكم المسؤول
    
    Returns:
        Response: استجابة HTTP
    """
    # إحصاءات النظام
    stats = {
        'users': {
            'total': len(User.get_all(limit=1000)),
            'admins': len(User.get_by_role('admin')),
            'evaluators': len(User.get_by_role('evaluator')),
            'students': len(User.get_by_role('student'))
        },
        'evaluations': Evaluation.get_statistics(),
        'rubrics': len(Rubric.get_all(limit=1000))
    }
    
    return render_template('admin/dashboard.html', stats=stats)

@bp.route('/users')
@login_required
@admin_required
def manage_users():
    """
    إدارة المستخدمين
    
    Returns:
        Response: استجابة HTTP
    """
    # الحصول على قائمة المستخدمين
    users = User.get_all(limit=100)
    
    return render_template('admin/users.html', users=users)

@bp.route('/users/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_user():
    """
    إضافة مستخدم جديد
    
    Returns:
        Response: استجابة HTTP
    """
    if request.method == 'POST':
        # الحصول على بيانات المستخدم
        if request.is_json:
            data = request.get_json()
        else:
            data = request.form
        
        name = data.get('name')
        email = data.get('email')
        password = data.get('password')
        role = data.get('role', 'student')
        
        # التحقق من البيانات المطلوبة
        if not name or not email or not password:
            if request.is_json:
                return jsonify({"error": "يرجى تعبئة جميع الحقول المطلوبة"}), 400
            flash("يرجى تعبئة جميع الحقول المطلوبة", "error")
            return render_template('admin/add_user.html')
        
        # التحقق من عدم وجود المستخدم مسبقًا
        existing_user = User.get_by_email(email)
        if existing_user:
            if request.is_json:
                return jsonify({"error": "البريد الإلكتروني مستخدم بالفعل"}), 400
            flash("البريد الإلكتروني مستخدم بالفعل", "error")
            return render_template('admin/add_user.html')
        
        # التحقق من صحة الدور
        if role not in ['admin', 'evaluator', 'student']:
            if request.is_json:
                return jsonify({"error": "الدور غير صالح"}), 400
            flash("الدور غير صالح", "error")
            return render_template('admin/add_user.html')
        
        # إنشاء مستخدم جديد
        user = User(
            email=email,
            name=name,
            role=role,
            is_active=True
        )
        user.set_password(password)
        
        if user.save():
            logger.info(f"تم إنشاء مستخدم جديد: {email} (الدور: {role})")
            
            if request.is_json:
                return jsonify({"message": "تم إنشاء المستخدم بنجاح", "user": user.to_dict()}), 201
            
            flash("تم إنشاء المستخدم بنجاح", "success")
            return redirect(url_for('admin.manage_users'))
        else:
            logger.error(f"فشل في إنشاء مستخدم جديد: {email}")
            
            if request.is_json:
                return jsonify({"error": "فشل في إنشاء المستخدم"}), 500
            
            flash("فشل في إنشاء المستخدم، يرجى المحاولة مرة أخرى", "error")
            return render_template('admin/add_user.html')
    
    # عرض نموذج إضافة مستخدم
    return render_template('admin/add_user.html')

@bp.route('/users/edit/<int:user_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_user(user_id):
    """
    تعديل مستخدم موجود
    
    Args:
        user_id (int): معرف المستخدم
        
    Returns:
        Response: استجابة HTTP
    """
    user = User.get_by_id(user_id)
    
    if not user:
        if request.is_json:
            return jsonify({"error": "المستخدم غير موجود"}), 404
        flash("المستخدم غير موجود", "error")
        return redirect(url_for('admin.manage_users'))
    
    if request.method == 'POST':
        # الحصول على بيانات المستخدم
        if request.is_json:
            data = request.get_json()
        else:
            data = request.form
        
        name = data.get('name')
        email = data.get('email')
        password = data.get('password')
        role = data.get('role')
        is_active = data.get('is_active')
        
        # تحديث البيانات
        if name:
            user.name = name
        
        if email and email != user.email:
            # التحقق من عدم وجود مستخدم آخر بنفس البريد الإلكتروني
            existing_user = User.get_by_email(email)
            if existing_user and existing_user.id != user.id:
                if request.is_json:
                    return jsonify({"error": "البريد الإلكتروني مستخدم بالفعل"}), 400
                flash("البريد الإلكتروني مستخدم بالفعل", "error")
                return render_template('admin/edit_user.html', user=user)
            
            user.email = email
        
        if password:
            user.set_password(password)
        
        if role and role in ['admin', 'evaluator', 'student']:
            user.role = role
        
        if is_active is not None:
            user.is_active = is_active in ['true', 'True', True, 1, '1']
        
        if user.save():
            logger.info(f"تم تحديث المستخدم: {user.email}")
            
            if request.is_json:
                return jsonify({"message": "تم تحديث المستخدم بنجاح", "user": user.to_dict()}), 200
            
            flash("تم تحديث المستخدم بنجاح", "success")
            return redirect(url_for('admin.manage_users'))
        else:
            logger.error(f"فشل في تحديث المستخدم: {user.email}")
            
            if request.is_json:
                return jsonify({"error": "فشل في تحديث المستخدم"}), 500
            
            flash("فشل في تحديث المستخدم، يرجى المحاولة مرة أخرى", "error")
            return render_template('admin/edit_user.html', user=user)
    
    # عرض نموذج تعديل المستخدم
    return render_template('admin/edit_user.html', user=user)

@bp.route('/users/delete/<int:user_id>', methods=['POST'])
@login_required
@admin_required
def delete_user(user_id):
    """
    حذف مستخدم
    
    Args:
        user_id (int): معرف المستخدم
        
    Returns:
        Response: استجابة HTTP
    """
    user = User.get_by_id(user_id)
    
    if not user:
        if request.is_json:
            return jsonify({"error": "المستخدم غير موجود"}), 404
        flash("المستخدم غير موجود", "error")
        return redirect(url_for('admin.manage_users'))
    
    # منع حذف المستخدم الحالي
    if user.id == current_user.id:
        if request.is_json:
            return jsonify({"error": "لا يمكنك حذف حسابك الحالي"}), 400
        flash("لا يمكنك حذف حسابك الحالي", "error")
        return redirect(url_for('admin.manage_users'))
    
    # حذف المستخدم
    if user.delete():
        logger.info(f"تم حذف المستخدم: {user.email}")
        
        if request.is_json:
            return jsonify({"message": "تم حذف المستخدم بنجاح"}), 200
        
        flash("تم حذف المستخدم بنجاح", "success")
    else:
        logger.error(f"فشل في حذف المستخدم: {user.email}")
        
        if request.is_json:
            return jsonify({"error": "فشل في حذف المستخدم"}), 500
        
        flash("فشل في حذف المستخدم، يرجى المحاولة مرة أخرى", "error")
    
    return redirect(url_for('admin.manage_users'))

@bp.route('/rubrics')
@login_required
@admin_required
def manage_rubrics():
    """
    إدارة معايير التقييم
    
    Returns:
        Response: استجابة HTTP
    """
    # الحصول على قائمة معايير التقييم
    rubrics = Rubric.get_all(limit=100)
    
    return render_template('admin/rubrics.html', rubrics=rubrics)

@bp.route('/rubrics/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_rubric():
    """
    إضافة معيار تقييم جديد
    
    Returns:
        Response: استجابة HTTP
    """
    if request.method == 'POST':
        # الحصول على بيانات معيار التقييم
        if request.is_json:
            data = request.get_json()
        else:
            data = request.form
        
        name = data.get('name')
        description = data.get('description', '')
        criteria_json = data.get('criteria', '{}')
        max_score = data.get('max_score', 100)
        
        # التحقق من البيانات المطلوبة
        if not name:
            if request.is_json:
                return jsonify({"error": "يرجى تحديد اسم معيار التقييم"}), 400
            flash("يرجى تحديد اسم معيار التقييم", "error")
            return render_template('admin/add_rubric.html')
        
        # التحقق من صحة تنسيق المعايير
        try:
            if isinstance(criteria_json, str):
                criteria = json.loads(criteria_json)
            else:
                criteria = criteria_json
        except json.JSONDecodeError:
            if request.is_json:
                return jsonify({"error": "تنسيق المعايير غير صالح (JSON)"}), 400
            flash("تنسيق المعايير غير صالح (JSON)", "error")
            return render_template('admin/add_rubric.html')
        
        # التحقق من الدرجة القصوى
        try:
            max_score = float(max_score)
        except ValueError:
            if request.is_json:
                return jsonify({"error": "قيمة الدرجة القصوى غير صالحة"}), 400
            flash("قيمة الدرجة القصوى غير صالحة", "error")
            return render_template('admin/add_rubric.html')
        
        # إنشاء معيار تقييم جديد
        rubric = Rubric(
            name=name,
            description=description,
            criteria=criteria,
            max_score=max_score,
            created_by=current_user.id
        )
        
        if rubric.save():
            logger.info(f"تم إنشاء معيار تقييم جديد: {name}")
            
            if request.is_json:
                return jsonify({"message": "تم إنشاء معيار التقييم بنجاح", "rubric": rubric.to_dict()}), 201
            
            flash("تم إنشاء معيار التقييم بنجاح", "success")
            return redirect(url_for('admin.manage_rubrics'))
        else:
            logger.error(f"فشل في إنشاء معيار تقييم جديد: {name}")
            
            if request.is_json:
                return jsonify({"error": "فشل في إنشاء معيار التقييم"}), 500
            
            flash("فشل في إنشاء معيار التقييم، يرجى المحاولة مرة أخرى", "error")
            return render_template('admin/add_rubric.html')
    
    # عرض نموذج إضافة معيار تقييم
    return render_template('admin/add_rubric.html')

@bp.route('/rubrics/edit/<int:rubric_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_rubric(rubric_id):
    """
    تعديل معيار تقييم موجود
    
    Args:
        rubric_id (int): معرف معيار التقييم
        
    Returns:
        Response: استجابة HTTP
    """
    rubric = Rubric.get_by_id(rubric_id)
    
    if not rubric:
        if request.is_json:
            return jsonify({"error": "معيار التقييم غير موجود"}), 404
        flash("معيار التقييم غير موجود", "error")
        return redirect(url_for('admin.manage_rubrics'))
    
    if request.method == 'POST':
        # الحصول على بيانات معيار التقييم
        if request.is_json:
            data = request.get_json()
        else:
            data = request.form
        
        name = data.get('name')
        description = data.get('description')
        criteria_json = data.get('criteria')
        max_score = data.get('max_score')
        
        # تحديث البيانات
        if name:
            rubric.name = name
        
        if description:
            rubric.description = description
        
        if criteria_json:
            # التحقق من صحة تنسيق المعايير
            try:
                if isinstance(criteria_json, str):
                    criteria = json.loads(criteria_json)
                else:
                    criteria = criteria_json
                
                rubric.criteria = criteria
            except json.JSONDecodeError:
                if request.is_json:
                    return jsonify({"error": "تنسيق المعايير غير صالح (JSON)"}), 400
                flash("تنسيق المعايير غير صالح (JSON)", "error")
                return render_template('admin/edit_rubric.html', rubric=rubric)
        
        if max_score:
            # التحقق من الدرجة القصوى
            try:
                rubric.max_score = float(max_score)
            except ValueError:
                if request.is_json:
                    return jsonify({"error": "قيمة الدرجة القصوى غير صالحة"}), 400
                flash("قيمة الدرجة القصوى غير صالحة", "error")
                return render_template('admin/edit_rubric.html', rubric=rubric)
        
        if rubric.save():
            logger.info(f"تم تحديث معيار التقييم: {rubric.name}")
            
            if request.is_json:
                return jsonify({"message": "تم تحديث معيار التقييم بنجاح", "rubric": rubric.to_dict()}), 200
            
            flash("تم تحديث معيار التقييم بنجاح", "success")
            return redirect(url_for('admin.manage_rubrics'))
        else:
            logger.error(f"فشل في تحديث معيار التقييم: {rubric.name}")
            
            if request.is_json:
                return jsonify({"error": "فشل في تحديث معيار التقييم"}), 500
            
            flash("فشل في تحديث معيار التقييم، يرجى المحاولة مرة أخرى", "error")
            return render_template('admin/edit_rubric.html', rubric=rubric)
    
    # عرض نموذج تعديل معيار التقييم
    return render_template('admin/edit_rubric.html', rubric=rubric)

@bp.route('/rubrics/delete/<int:rubric_id>', methods=['POST'])
@login_required
@admin_required
def delete_rubric(rubric_id):
    """
    حذف معيار تقييم
    
    Args:
        rubric_id (int): معرف معيار التقييم
        
    Returns:
        Response: استجابة HTTP
    """
    rubric = Rubric.get_by_id(rubric_id)
    
    if not rubric:
        if request.is_json:
            return jsonify({"error": "معيار التقييم غير موجود"}), 404
        flash("معيار التقييم غير موجود", "error")
        return redirect(url_for('admin.manage_rubrics'))
    
    # حذف معيار التقييم
    if rubric.delete():
        logger.info(f"تم حذف معيار التقييم: {rubric.name}")
        
        if request.is_json:
            return jsonify({"message": "تم حذف معيار التقييم بنجاح"}), 200
        
        flash("تم حذف معيار التقييم بنجاح", "success")
    else:
        logger.error(f"فشل في حذف معيار التقييم: {rubric.name}")
        
        if request.is_json:
            return jsonify({"error": "فشل في حذف معيار التقييم"}), 500
        
        flash("فشل في حذف معيار التقييم، يرجى المحاولة مرة أخرى", "error")
    
    return redirect(url_for('admin.manage_rubrics'))

@bp.route('/evaluations')
@login_required
@admin_required
def manage_evaluations():
    """
    إدارة التقييمات
    
    Returns:
        Response: استجابة HTTP
    """
    # الحصول على قائمة التقييمات
    evaluations = Evaluation.get_all(limit=100)
    
    # الحصول على الطلاب والمقيمين ومعايير التقييم
    students = User.get_by_role('student')
    evaluators = User.get_by_role('evaluator')
    rubrics = Rubric.get_all()
    
    return render_template(
        'admin/evaluations.html',
        evaluations=evaluations,
        students=students,
        evaluators=evaluators,
        rubrics=rubrics
    )

@bp.route('/system')
@login_required
@admin_required
def system_settings():
    """
    إعدادات النظام
    
    Returns:
        Response: استجابة HTTP
    """
    # جمع معلومات النظام والإحصاءات
    users_count = len(User.get_all(limit=1000))
    rubrics_count = len(Rubric.get_all(limit=1000))
    evaluations_stats = Evaluation.get_statistics()
    
    # معلومات البيئة
    env_info = {
        'environment': os.environ.get('FLASK_ENV', 'development'),
        'debug': current_app.debug,
        'ai_enabled': current_app.config.get('AI_ENABLED', False),
        'blockchain_enabled': current_app.config.get('BLOCKCHAIN_ENABLED', False),
        'database_url': '***' + os.environ.get('DATABASE_URL', '')[-10:] if os.environ.get('DATABASE_URL') else 'Not Set',
        'log_level': current_app.config.get('LOG_LEVEL', 'INFO')
    }
    
    return render_template(
        'admin/system_settings.html',
        users_count=users_count,
        rubrics_count=rubrics_count,
        evaluations_stats=evaluations_stats,
        env_info=env_info
    )

# مسارات API للمسؤول
@bp.route('/api/users', methods=['GET'])
@login_required
@admin_required
def api_get_users():
    """
    الحصول على قائمة المستخدمين عبر API
    
    Returns:
        Response: استجابة HTTP
    """
    role = request.args.get('role')
    limit = request.args.get('limit', 100, type=int)
    offset = request.args.get('offset', 0, type=int)
    
    if role and role in ['admin', 'evaluator', 'student']:
        users = User.get_by_role(role, limit=limit, offset=offset)
    else:
        users = User.get_all(limit=limit, offset=offset)
    
    users_data = [user.to_dict() for user in users]
    
    return jsonify({
        "users": users_data,
        "count": len(users_data),
        "limit": limit,
        "offset": offset
    }), 200

@bp.route('/api/rubrics', methods=['GET'])
@login_required
@admin_required
def api_get_rubrics():
    """
    الحصول على قائمة معايير التقييم عبر API
    
    Returns:
        Response: استجابة HTTP
    """
    limit = request.args.get('limit', 100, type=int)
    offset = request.args.get('offset', 0, type=int)
    
    rubrics = Rubric.get_all(limit=limit, offset=offset)
    rubrics_data = [rubric.to_dict() for rubric in rubrics]
    
    return jsonify({
        "rubrics": rubrics_data,
        "count": len(rubrics_data),
        "limit": limit,
        "offset": offset
    }), 200

@bp.route('/api/system/stats', methods=['GET'])
@login_required
@admin_required
def api_get_system_stats():
    """
    الحصول على إحصاءات النظام عبر API
    
    Returns:
        Response: استجابة HTTP
    """
    # إحصاءات المستخدمين
    users_stats = {
        'total': len(User.get_all(limit=1000)),
        'admins': len(User.get_by_role('admin')),
        'evaluators': len(User.get_by_role('evaluator')),
        'students': len(User.get_by_role('student'))
    }
    
    # إحصاءات التقييمات
    evaluations_stats = Evaluation.get_statistics()
    
    # إحصاءات معايير التقييم
    rubrics_stats = {
        'total': len(Rubric.get_all(limit=1000))
    }
    
    return jsonify({
        "users": users_stats,
        "evaluations": evaluations_stats,
        "rubrics": rubrics_stats,
        "timestamp": datetime.now().isoformat()
    }), 200