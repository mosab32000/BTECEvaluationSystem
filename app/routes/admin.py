"""
مسارات المسؤول
"""

from flask import Blueprint, jsonify, request, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import User, Evaluation, RubricTemplate, SystemMetrics
from app import db

admin = Blueprint('admin', __name__)

@admin.route('/stats', methods=['GET'])
@jwt_required()
def get_admin_stats():
    """
    الحصول على إحصائيات النظام (للمسؤولين فقط)
    """
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user or not user.is_admin():
        return jsonify(error="صلاحيات غير كافية", message="هذه العملية تتطلب صلاحيات المسؤول"), 403
    
    # عدد المستخدمين
    users_count = User.query.count()
    
    # عدد التقييمات
    evaluations_count = Evaluation.query.count()
    
    # عدد التقييمات المتحقق منها
    verified_count = Evaluation.query.filter_by(verification_status=True).count()
    
    # عدد قوالب معايير التقييم
    rubrics_count = RubricTemplate.query.count()
    
    # أحدث المستخدمين
    recent_users = User.query.order_by(User.created_at.desc()).limit(5).all()
    
    # أحدث التقييمات
    recent_evaluations = Evaluation.query.order_by(Evaluation.submitted_at.desc()).limit(5).all()
    
    # أحدث مقاييس النظام
    latest_metrics = SystemMetrics.query.order_by(SystemMetrics.timestamp.desc()).first()
    
    return jsonify(
        users_count=users_count,
        evaluations_count=evaluations_count,
        verified_count=verified_count,
        rubrics_count=rubrics_count,
        recent_users=[user.to_dict() for user in recent_users],
        recent_evaluations=[evaluation.to_dict() for evaluation in recent_evaluations],
        metrics=latest_metrics.to_dict() if latest_metrics else None
    ), 200

@admin.route('/users', methods=['GET'])
@jwt_required()
def get_users():
    """
    الحصول على قائمة المستخدمين (للمسؤولين فقط)
    """
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user or not user.is_admin():
        return jsonify(error="صلاحيات غير كافية", message="هذه العملية تتطلب صلاحيات المسؤول"), 403
    
    # معلمات البحث والترتيب والصفحات
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', current_app.config['ITEMS_PER_PAGE'], type=int)
    search = request.args.get('q', '')
    
    # بناء الاستعلام
    query = User.query
    
    # إضافة البحث إذا تم توفيره
    if search:
        query = query.filter(User.email.ilike(f'%{search}%') | User.name.ilike(f'%{search}%'))
    
    # تنفيذ الاستعلام مع الصفحات
    pagination = query.order_by(User.created_at.desc()).paginate(page=page, per_page=per_page, error_out=False)
    
    return jsonify(
        data=[user.to_dict() for user in pagination.items],
        pagination={
            'total': pagination.total,
            'pages': pagination.pages,
            'current_page': pagination.page,
            'per_page': pagination.per_page,
            'has_next': pagination.has_next,
            'has_prev': pagination.has_prev
        }
    ), 200

@admin.route('/users/<int:user_id>', methods=['GET'])
@jwt_required()
def get_user(user_id):
    """
    الحصول على تفاصيل مستخدم محدد (للمسؤولين فقط)
    """
    current_user_id = get_jwt_identity()
    admin_user = User.query.get(current_user_id)
    
    if not admin_user or not admin_user.is_admin():
        return jsonify(error="صلاحيات غير كافية", message="هذه العملية تتطلب صلاحيات المسؤول"), 403
    
    user = User.query.get(user_id)
    
    if not user:
        return jsonify(error="مستخدم غير موجود", message="المستخدم المطلوب غير موجود"), 404
    
    # عدد التقييمات للمستخدم
    evaluations_count = Evaluation.query.filter_by(user_id=user.id).count()
    
    # أحدث التقييمات للمستخدم
    recent_evaluations = Evaluation.query.filter_by(user_id=user.id).order_by(Evaluation.submitted_at.desc()).limit(5).all()
    
    return jsonify(
        user=user.to_dict(),
        evaluations_count=evaluations_count,
        recent_evaluations=[evaluation.to_dict() for evaluation in recent_evaluations]
    ), 200

@admin.route('/users/<int:user_id>', methods=['PUT'])
@jwt_required()
def update_user(user_id):
    """
    تحديث مستخدم محدد (للمسؤولين فقط)
    """
    current_user_id = get_jwt_identity()
    admin_user = User.query.get(current_user_id)
    
    if not admin_user or not admin_user.is_admin():
        return jsonify(error="صلاحيات غير كافية", message="هذه العملية تتطلب صلاحيات المسؤول"), 403
    
    user = User.query.get(user_id)
    
    if not user:
        return jsonify(error="مستخدم غير موجود", message="المستخدم المطلوب غير موجود"), 404
    
    data = request.get_json()
    
    if not data:
        return jsonify(error="بيانات غير صالحة", message="لم يتم توفير البيانات المطلوبة"), 400
    
    # تحديث الاسم إذا تم توفيره
    if 'name' in data:
        user.name = data['name']
    
    # تحديث البريد الإلكتروني إذا تم توفيره
    if 'email' in data:
        # تحقق من عدم وجود مستخدم آخر بنفس البريد الإلكتروني
        if User.query.filter(User.email == data['email'], User.id != user.id).first():
            return jsonify(error="البريد الإلكتروني موجود", message="البريد الإلكتروني مستخدم بالفعل"), 400
        user.email = data['email']
    
    # تحديث الدور إذا تم توفيره
    if 'role' in data:
        user.role = data['role']
    
    # تحديث حالة النشاط إذا تم توفيرها
    if 'is_active' in data:
        user.is_active = data['is_active']
    
    # تحديث كلمة المرور إذا تم توفيرها
    if 'password' in data and data['password']:
        user.set_password(data['password'])
    
    db.session.commit()
    
    return jsonify(
        message="تم تحديث المستخدم بنجاح",
        user=user.to_dict()
    ), 200

@admin.route('/users/<int:user_id>', methods=['DELETE'])
@jwt_required()
def delete_user(user_id):
    """
    حذف مستخدم محدد (للمسؤولين فقط)
    """
    current_user_id = get_jwt_identity()
    admin_user = User.query.get(current_user_id)
    
    if not admin_user or not admin_user.is_admin():
        return jsonify(error="صلاحيات غير كافية", message="هذه العملية تتطلب صلاحيات المسؤول"), 403
    
    # لا يمكن للمسؤول حذف نفسه
    if current_user_id == user_id:
        return jsonify(error="عملية غير مسموح بها", message="لا يمكنك حذف حسابك الخاص"), 400
    
    user = User.query.get(user_id)
    
    if not user:
        return jsonify(error="مستخدم غير موجود", message="المستخدم المطلوب غير موجود"), 404
    
    db.session.delete(user)
    db.session.commit()
    
    return jsonify(message="تم حذف المستخدم بنجاح"), 200
