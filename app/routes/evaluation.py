"""
مسارات عمليات التقييم
"""
import json
import logging
from datetime import datetime

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from app import db
from app.models.evaluation import Evaluation
from app.models.rubric import Rubric
from app.models.user import User
from app.core.ai_evaluator import AIEvaluator
from app.core.blockchain_verifier import BlockchainVerifier
from app.core.security import sanitize_input
from app.database import log_audit, update_metrics

# إنشاء المقيم الذكي ومتحقق البلوكتشين
ai_evaluator = AIEvaluator()
blockchain_verifier = BlockchainVerifier()

# إنشاء Blueprint للتقييم
eval_bp = Blueprint('evaluation', __name__, url_prefix='/evaluation')

@eval_bp.route('/submit', methods=['POST'])
@jwt_required()
def submit_task():
    """
    تقديم مهمة للتقييم
    """
    current_user_id = get_jwt_identity()
    data = request.json
    
    # التحقق من وجود البيانات المطلوبة
    if not data or not data.get('content'):
        return jsonify({
            'status': 'error',
            'message': 'محتوى المهمة مطلوب'
        }), 400
    
    # تنقية المدخلات
    content = sanitize_input(data.get('content', ''))
    title = sanitize_input(data.get('title', 'تقييم جديد'))
    description = sanitize_input(data.get('description', ''))
    
    # البحث عن معايير التقييم إذا تم تحديدها
    rubric_id = data.get('rubric_id')
    rubric = None
    
    if rubric_id:
        rubric = Rubric.query.get(rubric_id)
    
    try:
        # تقييم المهمة باستخدام الذكاء الاصطناعي
        evaluation_result = ai_evaluator.evaluate_task(content, rubric.criteria if rubric else None)
        
        # إنشاء كائن التقييم
        evaluation = Evaluation(
            title=title,
            description=description,
            content=content,
            rubric_id=rubric_id,
            user_id=current_user_id,
            result=evaluation_result,
            grade=evaluation_result.get('grade', 'NA'),
            feedback=evaluation_result.get('feedback', ''),
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        # حفظ التقييم في قاعدة البيانات
        db.session.add(evaluation)
        db.session.commit()
        
        # تحقق من التقييم على البلوكتشين
        verification_result = blockchain_verifier.verify_evaluation(evaluation)
        
        # تحديث معلومات التحقق
        evaluation.verification_hash = verification_result.get('hash', '')
        evaluation.verification_status = verification_result.get('success', False)
        evaluation.is_verified = verification_result.get('success', False)
        db.session.commit()
        
        # تسجيل الحدث وتحديث المقاييس
        log_audit('evaluation_created', f"User ID: {current_user_id}", {
            'evaluation_id': evaluation.id,
            'title': title,
            'grade': evaluation.grade
        })
        update_metrics(evaluation=True, blockchain=True)
        
        # إرجاع النتيجة
        return jsonify({
            'status': 'success',
            'message': 'تم تقييم المهمة بنجاح',
            'evaluation': evaluation.to_dict(),
            'verification': verification_result
        }), 201
        
    except Exception as e:
        db.session.rollback()
        logging.error(f"خطأ في تقييم المهمة: {str(e)}")
        
        # تسجيل الخطأ
        log_audit('evaluation_error', f"User ID: {current_user_id}", str(e))
        update_metrics(error=True)
        
        return jsonify({
            'status': 'error',
            'message': f'حدث خطأ أثناء تقييم المهمة: {str(e)}'
        }), 500

@eval_bp.route('/<int:evaluation_id>', methods=['GET'])
@jwt_required()
def get_evaluation(evaluation_id):
    """
    الحصول على تفاصيل تقييم محدد
    """
    current_user_id = get_jwt_identity()
    
    # البحث عن التقييم
    evaluation = Evaluation.query.get(evaluation_id)
    
    if not evaluation:
        return jsonify({
            'status': 'error',
            'message': 'التقييم غير موجود'
        }), 404
    
    # التحقق من أن المستخدم الحالي هو صاحب التقييم أو مسؤول
    user = User.query.get(current_user_id)
    
    if evaluation.user_id != current_user_id and user.role != 'admin':
        return jsonify({
            'status': 'error',
            'message': 'غير مصرح لك بالوصول إلى هذا التقييم'
        }), 403
    
    # تحديث مقاييس النظام
    update_metrics(api_call=True)
    
    # إرجاع التقييم
    return jsonify({
        'status': 'success',
        'evaluation': evaluation.to_dict()
    }), 200

@eval_bp.route('/user', methods=['GET'])
@jwt_required()
def get_user_evaluations():
    """
    الحصول على قائمة تقييمات المستخدم الحالي
    """
    current_user_id = get_jwt_identity()
    
    # الحصول على معلمات الاستعلام
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    # البحث عن تقييمات المستخدم
    evaluations = Evaluation.query.filter_by(user_id=current_user_id) \
        .order_by(Evaluation.created_at.desc()) \
        .paginate(page=page, per_page=per_page)
    
    # تحديث مقاييس النظام
    update_metrics(api_call=True)
    
    # إرجاع التقييمات
    return jsonify({
        'status': 'success',
        'evaluations': [evaluation.to_dict() for evaluation in evaluations.items],
        'pagination': {
            'total': evaluations.total,
            'pages': evaluations.pages,
            'page': page,
            'per_page': per_page,
            'prev_page': evaluations.prev_num,
            'next_page': evaluations.next_num,
            'has_prev': evaluations.has_prev,
            'has_next': evaluations.has_next
        }
    }), 200

@eval_bp.route('/verify/<int:evaluation_id>', methods=['POST'])
@jwt_required()
def verify_evaluation(evaluation_id):
    """
    التحقق من صحة تقييم
    """
    current_user_id = get_jwt_identity()
    
    # البحث عن التقييم
    evaluation = Evaluation.query.get(evaluation_id)
    
    if not evaluation:
        return jsonify({
            'status': 'error',
            'message': 'التقييم غير موجود'
        }), 404
    
    # التحقق من أن المستخدم الحالي هو صاحب التقييم أو مسؤول
    user = User.query.get(current_user_id)
    
    if evaluation.user_id != current_user_id and user.role != 'admin':
        return jsonify({
            'status': 'error',
            'message': 'غير مصرح لك بالتحقق من هذا التقييم'
        }), 403
    
    try:
        # التحقق من التقييم على البلوكتشين
        verification_result = blockchain_verifier.verify_evaluation(evaluation)
        
        # تحديث معلومات التحقق
        evaluation.verification_hash = verification_result.get('hash', '')
        evaluation.verification_status = verification_result.get('success', False)
        evaluation.is_verified = verification_result.get('success', False)
        db.session.commit()
        
        # تسجيل الحدث وتحديث المقاييس
        log_audit('evaluation_verified', f"User ID: {current_user_id}", {
            'evaluation_id': evaluation.id,
            'verification_result': verification_result
        })
        update_metrics(blockchain=True)
        
        # إرجاع النتيجة
        return jsonify({
            'status': 'success',
            'message': 'تم التحقق من التقييم بنجاح',
            'verification': verification_result
        }), 200
        
    except Exception as e:
        db.session.rollback()
        logging.error(f"خطأ في التحقق من التقييم: {str(e)}")
        
        # تسجيل الخطأ
        log_audit('verification_error', f"User ID: {current_user_id}", str(e))
        update_metrics(error=True)
        
        return jsonify({
            'status': 'error',
            'message': f'حدث خطأ أثناء التحقق من التقييم: {str(e)}'
        }), 500

@eval_bp.route('/rubrics', methods=['GET'])
@jwt_required()
def get_rubric_templates():
    """
    الحصول على قائمة قوالب معايير التقييم
    """
    current_user_id = get_jwt_identity()
    
    # البحث عن المعايير العامة والمعايير التي أنشأها المستخدم الحالي
    rubrics = Rubric.query.filter(
        (Rubric.is_default == True) | (Rubric.creator_id == current_user_id)
    ).all()
    
    # تحديث مقاييس النظام
    update_metrics(api_call=True)
    
    # إرجاع المعايير
    return jsonify({
        'status': 'success',
        'rubrics': [rubric.to_dict() for rubric in rubrics]
    }), 200

@eval_bp.route('/rubric/<int:rubric_id>', methods=['GET'])
@jwt_required()
def get_rubric_template(rubric_id):
    """
    الحصول على تفاصيل قالب معايير تقييم محدد
    """
    current_user_id = get_jwt_identity()
    
    # البحث عن معيار التقييم
    rubric = Rubric.query.get(rubric_id)
    
    if not rubric:
        return jsonify({
            'status': 'error',
            'message': 'معيار التقييم غير موجود'
        }), 404
    
    # التحقق من أن المعيار عام أو أنشأه المستخدم الحالي
    if not rubric.is_default and rubric.creator_id != current_user_id:
        user = User.query.get(current_user_id)
        if user.role != 'admin':
            return jsonify({
                'status': 'error',
                'message': 'غير مصرح لك بالوصول إلى هذا المعيار'
            }), 403
    
    # تحديث مقاييس النظام
    update_metrics(api_call=True)
    
    # إرجاع معيار التقييم
    return jsonify({
        'status': 'success',
        'rubric': rubric.to_dict()
    }), 200

@eval_bp.route('/rubric', methods=['POST'])
@jwt_required()
def create_rubric_template():
    """
    إنشاء قالب معايير تقييم جديد
    مسار محمي - يمكن للمسؤولين والمعلمين فقط إنشاء قوالب معايير تقييم
    """
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    # التحقق من أن المستخدم مسؤول أو معلم
    if user.role not in ['admin', 'teacher']:
        return jsonify({
            'status': 'error',
            'message': 'غير مصرح لك بإنشاء معايير تقييم'
        }), 403
    
    data = request.json
    
    # التحقق من وجود البيانات المطلوبة
    if not data or not data.get('name') or not data.get('criteria'):
        return jsonify({
            'status': 'error',
            'message': 'اسم ومعايير التقييم مطلوبة'
        }), 400
    
    # تنقية المدخلات
    name = sanitize_input(data.get('name', ''))
    description = sanitize_input(data.get('description', ''))
    
    try:
        # إنشاء معيار تقييم جديد
        rubric = Rubric(
            name=name,
            description=description,
            criteria=data.get('criteria', {}),
            is_default=data.get('is_default', False),
            creator_id=current_user_id,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        # حفظ معيار التقييم في قاعدة البيانات
        db.session.add(rubric)
        db.session.commit()
        
        # تسجيل الحدث
        log_audit('rubric_created', f"User ID: {current_user_id}", {
            'rubric_id': rubric.id,
            'name': name
        })
        
        # إرجاع النجاح
        return jsonify({
            'status': 'success',
            'message': 'تم إنشاء معيار التقييم بنجاح',
            'rubric': rubric.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        logging.error(f"خطأ في إنشاء معيار التقييم: {str(e)}")
        
        # تسجيل الخطأ
        log_audit('rubric_creation_error', f"User ID: {current_user_id}", str(e))
        
        return jsonify({
            'status': 'error',
            'message': f'حدث خطأ أثناء إنشاء معيار التقييم: {str(e)}'
        }), 500
