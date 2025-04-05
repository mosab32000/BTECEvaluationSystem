"""
وحدة مسارات واجهة برمجة التطبيقات (API) لنظام تقييم BTEC
"""

from datetime import datetime, timedelta
import json

from flask import Blueprint, jsonify, request, current_app
from flask_jwt_extended import (
    create_access_token, create_refresh_token, 
    jwt_required, get_jwt_identity, get_jwt
)
from werkzeug.security import check_password_hash

from app.extensions import db, jwt, limiter
from app.models.user import User
from app.models.evaluation import Evaluation
from app.models.rubric import Rubric

api_blueprint = Blueprint('api', __name__)


# قائمة الرموز المحظورة
blacklist = set()


@jwt.token_in_blocklist_loader
def check_if_token_in_blacklist(jwt_header, jwt_payload):
    """التحقق مما إذا كان الرمز في القائمة السوداء"""
    jti = jwt_payload['jti']
    return jti in blacklist


@api_blueprint.route('/auth/login', methods=['POST'])
@limiter.limit("10/minute")
def api_login():
    """تسجيل الدخول عبر API"""
    if not request.is_json:
        return jsonify({"error": "Missing JSON in request"}), 400
    
    email = request.json.get('email', None)
    password = request.json.get('password', None)
    
    if not email or not password:
        return jsonify({"error": "Missing email or password"}), 400
    
    user = User.query.filter_by(email=email).first()
    
    if not user or not check_password_hash(user.password_hash, password):
        return jsonify({"error": "Invalid credentials"}), 401
    
    if not user.is_active:
        return jsonify({"error": "Account is disabled"}), 403
    
    # تحديث وقت آخر تسجيل دخول
    user.last_login = datetime.utcnow()
    db.session.commit()
    
    # إنشاء رموز الوصول والتحديث
    access_token = create_access_token(identity=user.id)
    refresh_token = create_refresh_token(identity=user.id)
    
    return jsonify({
        "message": "Login successful",
        "access_token": access_token,
        "refresh_token": refresh_token,
        "user": {
            "id": user.id,
            "email": user.email,
            "name": user.name,
            "role": user.role
        }
    }), 200


@api_blueprint.route('/auth/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """تحديث رمز الوصول"""
    current_user_id = get_jwt_identity()
    new_access_token = create_access_token(identity=current_user_id)
    
    return jsonify({
        "access_token": new_access_token
    }), 200


@api_blueprint.route('/auth/logout', methods=['POST'])
@jwt_required()
def api_logout():
    """تسجيل الخروج عبر API"""
    jti = get_jwt()['jti']
    blacklist.add(jti)
    
    return jsonify({"message": "Successfully logged out"}), 200


@api_blueprint.route('/user', methods=['GET'])
@jwt_required()
def get_user():
    """الحصول على معلومات المستخدم الحالي"""
    current_user_id = get_jwt_identity()
    user = User.query.get_or_404(current_user_id)
    
    return jsonify({
        "id": user.id,
        "email": user.email,
        "name": user.name,
        "role": user.role,
        "is_active": user.is_active,
        "created_at": user.created_at.isoformat() if user.created_at else None,
        "last_login": user.last_login.isoformat() if user.last_login else None
    }), 200


@api_blueprint.route('/evaluations', methods=['GET'])
@jwt_required()
def get_evaluations():
    """الحصول على قائمة التقييمات للمستخدم الحالي"""
    current_user_id = get_jwt_identity()
    user = User.query.get_or_404(current_user_id)
    
    if user.role == 'student':
        evaluations = Evaluation.query.filter_by(student_id=user.id).all()
    elif user.role in ['teacher', 'admin']:
        evaluations = Evaluation.query.filter_by(evaluator_id=user.id).all()
    else:
        return jsonify({"error": "Unauthorized access"}), 403
    
    result = []
    for evaluation in evaluations:
        result.append({
            "id": evaluation.id,
            "student_id": evaluation.student_id,
            "assignment_id": evaluation.assignment_id,
            "rubric_id": evaluation.rubric_id,
            "score": evaluation.score,
            "ai_score": evaluation.ai_score,
            "status": evaluation.status,
            "created_at": evaluation.created_at.isoformat() if evaluation.created_at else None,
            "updated_at": evaluation.updated_at.isoformat() if evaluation.updated_at else None
        })
    
    return jsonify(result), 200


@api_blueprint.route('/rubrics', methods=['GET'])
@jwt_required()
def get_rubrics():
    """الحصول على قائمة معايير التقييم"""
    rubrics = Rubric.query.all()
    
    result = []
    for rubric in rubrics:
        result.append({
            "id": rubric.id,
            "name": rubric.name,
            "description": rubric.description,
            "max_score": rubric.max_score,
            "created_by": rubric.created_by,
            "created_at": rubric.created_at.isoformat() if rubric.created_at else None,
            "updated_at": rubric.updated_at.isoformat() if rubric.updated_at else None
        })
    
    return jsonify(result), 200


@api_blueprint.route('/evaluate', methods=['POST'])
@jwt_required()
def create_evaluation():
    """إنشاء تقييم جديد"""
    if not request.is_json:
        return jsonify({"error": "Missing JSON in request"}), 400
    
    current_user_id = get_jwt_identity()
    user = User.query.get_or_404(current_user_id)
    
    # التحقق من صلاحيات المستخدم
    if user.role not in ['teacher', 'admin']:
        return jsonify({"error": "Unauthorized access"}), 403
    
    data = request.json
    student_id = data.get('student_id')
    assignment_id = data.get('assignment_id')
    rubric_id = data.get('rubric_id')
    submission_text = data.get('submission_text')
    
    # التحقق من وجود البيانات المطلوبة
    if not all([student_id, assignment_id, rubric_id, submission_text]):
        return jsonify({"error": "Missing required fields"}), 400
    
    # التحقق من وجود الطالب ومعيار التقييم
    student = User.query.get(student_id)
    rubric = Rubric.query.get(rubric_id)
    
    if not student or student.role != 'student':
        return jsonify({"error": "Invalid student ID"}), 400
    
    if not rubric:
        return jsonify({"error": "Invalid rubric ID"}), 400
    
    # إنشاء التقييم الجديد
    evaluation = Evaluation(
        student_id=student_id,
        assignment_id=assignment_id,
        rubric_id=rubric_id,
        submission_text=submission_text,
        evaluator_id=current_user_id,
        status='pending'
    )
    
    db.session.add(evaluation)
    db.session.commit()
    
    # TODO: استدعاء خدمة التقييم الآلي هنا
    
    return jsonify({
        "message": "Evaluation created successfully",
        "evaluation_id": evaluation.id
    }), 201