"""
مسارات عمليات التقييم
"""
import datetime
import json
import logging
from functools import wraps

from flask import Blueprint, current_app, g, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from app import db, cache, limiter
from app.core.ai_evaluator import AIEvaluator
from app.core.blockchain_verifier import BlockchainVerifier
from app.core.security import sanitize_input, token_required
from app.database import log_audit, update_metrics
from app.models.evaluation import Evaluation
from app.models.rubric import RubricTemplate
from app.models.user import User

# إعداد المسارات
evaluation_bp = Blueprint('evaluation', __name__)
logger = logging.getLogger(__name__)

# إنشاء مثيلات من الفئات المستخدمة
ai_evaluator = AIEvaluator()
blockchain_verifier = BlockchainVerifier()

# إعداد محدد الطلبات
evaluation_limiter = limiter.shared_limit(
    "5 per minute, 20 per hour", 
    scope="evaluation"
)

@evaluation_bp.route('/submit', methods=['POST'])
@jwt_required()
@evaluation_limiter
def submit_task():
    """
    تقديم مهمة للتقييم
    
    طريقة الطلب: POST
    المسار: /api/evaluations/submit
    الرأس المطلوب:
        - Authorization: Bearer <access_token>
    الحقول المطلوبة:
        - task_text: نص المهمة
        - submission_id: معرف التقديم
    الحقول الاختيارية:
        - rubric_id: معرف قالب معايير التقييم
    """
    try:
        data = request.get_json()
        
        # التحقق من وجود البيانات المطلوبة
        if not data or not data.get('task_text') or not data.get('submission_id'):
            return jsonify({
                'status': 'error',
                'message': 'نص المهمة ومعرف التقديم مطلوبان'
            }), 400
        
        # تنظيف المدخلات
        task_text = sanitize_input(data.get('task_text'))
        submission_id = sanitize_input(data.get('submission_id'))
        rubric_id = data.get('rubric_id')
        
        # التحقق من طول نص المهمة
        if len(task_text) < 10:
            return jsonify({
                'status': 'error',
                'message': 'نص المهمة قصير جدًا'
            }), 400
        
        # الحصول على معرف المستخدم الحالي
        user_id = get_jwt_identity()
        
        # الحصول على قالب معايير التقييم
        rubric = None
        if rubric_id:
            rubric = RubricTemplate.get_by_id(rubric_id)
            if not rubric:
                # استخدام القالب الافتراضي إذا لم يتم العثور على القالب المطلوب
                rubric = RubricTemplate.get_default_template()
        else:
            # استخدام القالب الافتراضي
            rubric = RubricTemplate.get_default_template()
        
        # تحويل Rubric إلى قاموس
        rubric_dict = None
        if rubric:
            rubric_dict = rubric.to_dict()
        
        # تقييم المهمة باستخدام AI
        eval_start_time = datetime.datetime.now()
        evaluation_result = ai_evaluator.evaluate_task(task_text, rubric_dict)
        eval_end_time = datetime.datetime.now()
        eval_duration = (eval_end_time - eval_start_time).total_seconds()
        
        # إنشاء كائن تقييم جديد
        new_evaluation = Evaluation()
        new_evaluation.user_id = user_id
        new_evaluation.submission_id = submission_id
        new_evaluation.task_text = task_text
        new_evaluation.grade = evaluation_result.get('grade')
        new_evaluation.grade_numeric = evaluation_result.get('grade_numeric')
        new_evaluation.feedback = evaluation_result.get('feedback')
        
        # تعيين قوائم ودرجات معايير التقييم
        new_evaluation.set_strengths(evaluation_result.get('strengths', []))
        new_evaluation.set_areas_for_improvement(evaluation_result.get('areas_for_improvement', []))
        new_evaluation.set_criteria_scores(evaluation_result.get('criteria_scores', {}))
        
        # حفظ التقييم في قاعدة البيانات
        db.session.add(new_evaluation)
        db.session.commit()
        
        # تسجيل الحدث
        log_audit(
            event_type="task_evaluation",
            user=str(user_id),
            details={
                "evaluation_id": new_evaluation.id,
                "submission_id": submission_id,
                "duration": eval_duration,
                "grade": new_evaluation.grade
            }
        )
        
        # تحديث المقاييس
        update_metrics(
            evaluation=True,
            response_time=eval_duration
        )
        
        # إرجاع النتيجة
        evaluation_dict = new_evaluation.to_dict()
        evaluation_dict['processing_time'] = evaluation_result.get('processing_time')
        
        return jsonify({
            'status': 'success',
            'message': 'تم تقييم المهمة بنجاح',
            'evaluation': evaluation_dict
        }), 201
        
    except Exception as e:
        logger.error(f"Error in submit_task: {str(e)}")
        db.session.rollback()
        
        # تسجيل الخطأ
        log_audit(
            event_type="task_evaluation_error",
            user=str(get_jwt_identity()),
            details=str(e)
        )
        
        # تحديث المقاييس
        update_metrics(
            evaluation=True,
            error=True
        )
        
        return jsonify({
            'status': 'error',
            'message': 'حدث خطأ أثناء تقييم المهمة'
        }), 500

@evaluation_bp.route('/<int:evaluation_id>', methods=['GET'])
@jwt_required()
def get_evaluation(evaluation_id):
    """
    الحصول على تفاصيل تقييم محدد
    
    طريقة الطلب: GET
    المسار: /api/evaluations/<evaluation_id>
    الرأس المطلوب:
        - Authorization: Bearer <access_token>
    """
    try:
        # الحصول على المستخدم الحالي
        user_id = get_jwt_identity()
        user = User.get_by_id(user_id)
        
        # الحصول على التقييم
        evaluation = Evaluation.get_by_id(evaluation_id)
        
        if not evaluation:
            return jsonify({
                'status': 'error',
                'message': 'التقييم غير موجود'
            }), 404
        
        # التحقق من الصلاحيات: المسؤولون يمكنهم رؤية جميع التقييمات،
        # بينما يمكن للمستخدمين العاديين رؤية تقييماتهم فقط
        if evaluation.user_id != user_id and not user.is_admin():
            return jsonify({
                'status': 'error',
                'message': 'غير مصرح لك بالوصول إلى هذا التقييم'
            }), 403
        
        # إرجاع التقييم
        return jsonify({
            'status': 'success',
            'evaluation': evaluation.to_dict()
        }), 200
        
    except Exception as e:
        logger.error(f"Error in get_evaluation: {str(e)}")
        
        return jsonify({
            'status': 'error',
            'message': 'حدث خطأ أثناء الحصول على التقييم'
        }), 500

@evaluation_bp.route('', methods=['GET'])
@jwt_required()
def get_user_evaluations():
    """
    الحصول على قائمة تقييمات المستخدم الحالي
    
    طريقة الطلب: GET
    المسار: /api/evaluations
    الرأس المطلوب:
        - Authorization: Bearer <access_token>
    معلمات الاستعلام الاختيارية:
        - page: رقم الصفحة (الافتراضي: 1)
        - per_page: عدد العناصر في الصفحة (الافتراضي: 10)
    """
    try:
        # الحصول على المستخدم الحالي
        user_id = get_jwt_identity()
        
        # الحصول على معلمات الاستعلام
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        # التحقق من صحة معلمات الاستعلام
        if page < 1 or per_page < 1 or per_page > 100:
            return jsonify({
                'status': 'error',
                'message': 'معلمات الاستعلام غير صالحة'
            }), 400
        
        # الحصول على تقييمات المستخدم
        evaluations, total = Evaluation.get_user_evaluations(user_id, page, per_page)
        
        # تحويل التقييمات إلى قواميس
        evaluation_dicts = [evaluation.to_dict() for evaluation in evaluations]
        
        # إرجاع القائمة
        return jsonify({
            'status': 'success',
            'evaluations': evaluation_dicts,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': total,
                'pages': (total + per_page - 1) // per_page
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Error in get_user_evaluations: {str(e)}")
        
        return jsonify({
            'status': 'error',
            'message': 'حدث خطأ أثناء الحصول على قائمة التقييمات'
        }), 500

@evaluation_bp.route('/<int:evaluation_id>/verify', methods=['POST'])
@jwt_required()
def verify_evaluation(evaluation_id):
    """
    التحقق من صحة تقييم
    
    طريقة الطلب: POST
    المسار: /api/evaluations/<evaluation_id>/verify
    الرأس المطلوب:
        - Authorization: Bearer <access_token>
    """
    try:
        # الحصول على المستخدم الحالي
        user_id = get_jwt_identity()
        user = User.get_by_id(user_id)
        
        # الحصول على التقييم
        evaluation = Evaluation.get_by_id(evaluation_id)
        
        if not evaluation:
            return jsonify({
                'status': 'error',
                'message': 'التقييم غير موجود'
            }), 404
        
        # التحقق من الصلاحيات: المسؤولون والمعلمون يمكنهم التحقق من أي تقييم،
        # بينما يمكن للمستخدمين العاديين التحقق من تقييماتهم فقط
        if evaluation.user_id != user_id and not (user.is_admin() or user.is_teacher()):
            return jsonify({
                'status': 'error',
                'message': 'غير مصرح لك بالتحقق من هذا التقييم'
            }), 403
        
        # التحقق من أن التقييم لم يتم التحقق منه بالفعل
        if evaluation.verified:
            return jsonify({
                'status': 'error',
                'message': 'تم التحقق من هذا التقييم بالفعل'
            }), 400
        
        # التحقق من صحة التقييم باستخدام البلوكتشين
        verification_result = blockchain_verifier.verify_evaluation(evaluation.to_dict())
        
        # تحديث التقييم
        evaluation.verified = verification_result.get('verified', False)
        evaluation.set_verification_data(verification_result)
        
        # حفظ التغييرات
        db.session.commit()
        
        # تسجيل الحدث
        log_audit(
            event_type="evaluation_verification",
            user=str(user_id),
            details={
                "evaluation_id": evaluation.id,
                "submission_id": evaluation.submission_id,
                "verified": evaluation.verified,
                "verification_data": verification_result
            }
        )
        
        # تحديث المقاييس
        update_metrics(blockchain=True)
        
        # إرجاع النتيجة
        return jsonify({
            'status': 'success',
            'message': 'تم التحقق من التقييم بنجاح',
            'verification': verification_result
        }), 200
        
    except Exception as e:
        logger.error(f"Error in verify_evaluation: {str(e)}")
        db.session.rollback()
        
        # تسجيل الخطأ
        log_audit(
            event_type="evaluation_verification_error",
            user=str(get_jwt_identity()),
            details=str(e)
        )
        
        # تحديث المقاييس
        update_metrics(blockchain=True, error=True)
        
        return jsonify({
            'status': 'error',
            'message': 'حدث خطأ أثناء التحقق من التقييم'
        }), 500

@evaluation_bp.route('/rubrics', methods=['GET'])
@jwt_required()
def get_rubric_templates():
    """
    الحصول على قائمة قوالب معايير التقييم
    
    طريقة الطلب: GET
    المسار: /api/evaluations/rubrics
    الرأس المطلوب:
        - Authorization: Bearer <access_token>
    معلمات الاستعلام الاختيارية:
        - page: رقم الصفحة (الافتراضي: 1)
        - per_page: عدد العناصر في الصفحة (الافتراضي: 10)
    """
    try:
        # الحصول على معلمات الاستعلام
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        # التحقق من صحة معلمات الاستعلام
        if page < 1 or per_page < 1 or per_page > 100:
            return jsonify({
                'status': 'error',
                'message': 'معلمات الاستعلام غير صالحة'
            }), 400
        
        # الحصول على قوالب معايير التقييم
        templates, total = RubricTemplate.get_all_templates(page, per_page)
        
        # تحويل القوالب إلى قواميس
        template_dicts = [template.to_dict() for template in templates]
        
        # إرجاع القائمة
        return jsonify({
            'status': 'success',
            'rubrics': template_dicts,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': total,
                'pages': (total + per_page - 1) // per_page
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Error in get_rubric_templates: {str(e)}")
        
        return jsonify({
            'status': 'error',
            'message': 'حدث خطأ أثناء الحصول على قائمة قوالب معايير التقييم'
        }), 500

@evaluation_bp.route('/rubrics/<int:rubric_id>', methods=['GET'])
@jwt_required()
def get_rubric_template(rubric_id):
    """
    الحصول على تفاصيل قالب معايير تقييم محدد
    
    طريقة الطلب: GET
    المسار: /api/evaluations/rubrics/<rubric_id>
    الرأس المطلوب:
        - Authorization: Bearer <access_token>
    """
    try:
        # الحصول على قالب معايير التقييم
        template = RubricTemplate.get_by_id(rubric_id)
        
        if not template:
            return jsonify({
                'status': 'error',
                'message': 'قالب معايير التقييم غير موجود'
            }), 404
        
        # إرجاع القالب
        return jsonify({
            'status': 'success',
            'rubric': template.to_dict()
        }), 200
        
    except Exception as e:
        logger.error(f"Error in get_rubric_template: {str(e)}")
        
        return jsonify({
            'status': 'error',
            'message': 'حدث خطأ أثناء الحصول على قالب معايير التقييم'
        }), 500

@evaluation_bp.route('/rubrics', methods=['POST'])
@jwt_required()
@token_required(allowed_roles=['admin', 'teacher'])
def create_rubric_template():
    """
    إنشاء قالب معايير تقييم جديد
    مسار محمي - يمكن للمسؤولين والمعلمين فقط إنشاء قوالب معايير تقييم
    
    طريقة الطلب: POST
    المسار: /api/evaluations/rubrics
    الرأس المطلوب:
        - Authorization: Bearer <access_token>
    الحقول المطلوبة:
        - name: اسم القالب
        - criteria: معايير التقييم (مصفوفة)
    الحقول الاختيارية:
        - description: وصف القالب
        - is_default: ما إذا كان القالب افتراضيًا
    """
    try:
        data = request.get_json()
        
        # التحقق من وجود البيانات المطلوبة
        if not data or not data.get('name') or not data.get('criteria'):
            return jsonify({
                'status': 'error',
                'message': 'اسم القالب ومعايير التقييم مطلوبة'
            }), 400
        
        # تنظيف المدخلات
        name = sanitize_input(data.get('name'))
        description = sanitize_input(data.get('description', ''))
        criteria = data.get('criteria')
        is_default = data.get('is_default', False)
        
        # التحقق من أن معايير التقييم هي مصفوفة
        if not isinstance(criteria, list):
            return jsonify({
                'status': 'error',
                'message': 'معايير التقييم يجب أن تكون مصفوفة'
            }), 400
        
        # الحصول على المستخدم الحالي
        user_id = get_jwt_identity()
        
        # إنشاء قالب معايير تقييم جديد
        new_template = RubricTemplate()
        new_template.name = name
        new_template.description = description
        new_template.set_criteria(criteria)
        new_template.created_by = user_id
        new_template.is_default = is_default
        
        # إذا كان القالب افتراضيًا، جعل جميع القوالب الأخرى غير افتراضية
        if is_default:
            default_templates = RubricTemplate.query.filter_by(is_default=True).all()
            for template in default_templates:
                template.is_default = False
        
        # حفظ القالب في قاعدة البيانات
        db.session.add(new_template)
        db.session.commit()
        
        # تسجيل الحدث
        log_audit(
            event_type="rubric_template_created",
            user=str(user_id),
            details={
                "template_id": new_template.id,
                "name": name,
                "is_default": is_default
            }
        )
        
        # إرجاع القالب
        return jsonify({
            'status': 'success',
            'message': 'تم إنشاء قالب معايير التقييم بنجاح',
            'rubric': new_template.to_dict()
        }), 201
        
    except Exception as e:
        logger.error(f"Error in create_rubric_template: {str(e)}")
        db.session.rollback()
        
        # تسجيل الخطأ
        log_audit(
            event_type="rubric_template_create_error",
            user=str(get_jwt_identity()),
            details=str(e)
        )
        
        return jsonify({
            'status': 'error',
            'message': 'حدث خطأ أثناء إنشاء قالب معايير التقييم'
        }), 500