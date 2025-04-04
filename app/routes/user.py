"""
مسارات المستخدمين
"""

from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import User, Evaluation
from app import db

user = Blueprint('user', __name__)

@user.route('/stats', methods=['GET'])
@jwt_required()
def get_user_stats():
    """
    الحصول على إحصائيات المستخدم
    """
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user:
        return jsonify(error="مستخدم غير موجود", message="المستخدم غير موجود"), 404
    
    # عدد التقييمات
    evaluations_count = Evaluation.query.filter_by(user_id=user.id).count()
    
    # عدد التقييمات المتحقق منها
    verified_count = Evaluation.query.filter_by(user_id=user.id, verification_status=True).count()
    
    # أحدث التقييمات
    recent_evaluations = Evaluation.query.filter_by(user_id=user.id).order_by(Evaluation.submitted_at.desc()).limit(5).all()
    
    return jsonify(
        user_id=user.id,
        evaluations_count=evaluations_count,
        verified_count=verified_count,
        recent_evaluations=[evaluation.to_dict() for evaluation in recent_evaluations]
    ), 200

@user.route('/profile', methods=['GET'])
@jwt_required()
def get_user_profile():
    """
    الحصول على الملف الشخصي للمستخدم
    """
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user:
        return jsonify(error="مستخدم غير موجود", message="المستخدم غير موجود"), 404
    
    return jsonify(user.to_dict()), 200

@user.route('/profile', methods=['PUT'])
@jwt_required()
def update_user_profile():
    """
    تحديث الملف الشخصي للمستخدم
    """
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user:
        return jsonify(error="مستخدم غير موجود", message="المستخدم غير موجود"), 404
    
    data = request.get_json()
    
    if not data:
        return jsonify(error="بيانات غير صالحة", message="لم يتم توفير البيانات المطلوبة"), 400
    
    # تحديث الاسم إذا تم توفيره
    if 'name' in data:
        user.name = data['name']
    
    # تحديث كلمة المرور إذا تم توفيرها
    if 'password' in data and data['password']:
        user.set_password(data['password'])
    
    db.session.commit()
    
    return jsonify(
        message="تم تحديث الملف الشخصي بنجاح",
        user=user.to_dict()
    ), 200
