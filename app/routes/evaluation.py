"""
مسارات التقييم في نظام تقييم BTEC
"""
import json
import logging
from datetime import datetime

from flask import Blueprint, jsonify, request, current_app
from flask_jwt_extended import get_jwt_identity, jwt_required

from app import db
from app.models.evaluation import Evaluation, Course, Task
from app.models.rubric import RubricTemplate
from app.models.user import User
from app.core.ai_evaluator import AIEvaluator, AIEvaluatorArabic
from app.core.blockchain_verifier import BlockchainVerifier, blockchain_required
from app.routes.auth import admin_required, instructor_required

logger = logging.getLogger(__name__)

# إنشاء blueprint للتقييم
evaluation_bp = Blueprint('evaluation', __name__)

# مسارات التقييم
@evaluation_bp.route('/', methods=['POST'])
@jwt_required()
def create_evaluation():
    """
    إنشاء تقييم جديد
    """
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify(
                status='error',
                message='المستخدم غير موجود'
            ), 404
        
        # التحقق من أن المستخدم مدرس أو مسؤول
        if not (user.is_instructor() or user.is_admin()):
            return jsonify(
                status='error',
                message='يجب أن تكون مدرسًا أو مسؤولاً لإنشاء تقييم'
            ), 403
        
        data = request.get_json()
        
        # التحقق من البيانات
        required_fields = ['title', 'task_description', 'submission_text', 'student_id']
        for field in required_fields:
            if field not in data:
                return jsonify(
                    status='error',
                    message=f'الحقل {field} مطلوب'
                ), 400
        
        # التحقق من وجود الطالب
        student_id = data.get('student_id')
        student = User.query.get(student_id)
        
        if not student:
            return jsonify(
                status='error',
                message='الطالب غير موجود'
            ), 404
        
        # إنشاء التقييم
        evaluation = Evaluation()
        evaluation.title = data.get('title')
        evaluation.description = data.get('description')
        evaluation.task_description = data.get('task_description')
        evaluation.submission_text = data.get('submission_text')
        evaluation.evaluator_id = user_id
        evaluation.student_id = student_id
        
        # إذا تم توفير معيار تقييم
        if 'rubric_id' in data and data.get('rubric_id'):
            rubric_id = data.get('rubric_id')
            rubric = RubricTemplate.query.get(rubric_id)
            
            if not rubric:
                return jsonify(
                    status='error',
                    message='معيار التقييم غير موجود'
                ), 404
            
            evaluation.rubric_id = rubric_id
        
        # إذا تم توفير المساق
        if 'course_id' in data and data.get('course_id'):
            course_id = data.get('course_id')
            course = Course.query.get(course_id)
            
            if not course:
                return jsonify(
                    status='error',
                    message='المساق غير موجود'
                ), 404
            
            evaluation.course_id = course_id
        
        # إذا تم توفير وسائط متعددة
        if 'media_files' in data and data.get('media_files'):
            evaluation.media_files = data.get('media_files')
        
        # إذا تم طلب التقييم التلقائي
        if data.get('auto_evaluate', False):
            # استخدام الذكاء الاصطناعي للتقييم
            ai_evaluator = AIEvaluatorArabic()  # استخدام مقيّم اللغة العربية
            
            rubric = None
            if evaluation.rubric_id:
                rubric_template = RubricTemplate.query.get(evaluation.rubric_id)
                if rubric_template:
                    rubric = rubric_template.get_criteria()
            
            # إجراء التقييم
            evaluation_result = ai_evaluator.evaluate_task(
                evaluation.task_description,
                evaluation.submission_text,
                rubric=rubric,
                output_format='json'
            )
            
            if evaluation_result.get('success', False):
                evaluation.grade = evaluation_result.get('grade')
                evaluation.feedback = evaluation_result.get('feedback')
                
                # إذا تم توفير درجات لكل معيار
                if 'criteria_grades' in evaluation_result:
                    evaluation.criteria = {
                        'criteria_grades': evaluation_result.get('criteria_grades'),
                        'raw_response': evaluation_result.get('raw_response')
                    }
                
                evaluation.status = 'completed'
                evaluation.completed_at = datetime.utcnow()
            else:
                logger.error(f"خطأ في التقييم التلقائي: {evaluation_result.get('error')}")
        
        # حفظ التقييم
        db.session.add(evaluation)
        db.session.commit()
        
        return jsonify(
            status='success',
            message='تم إنشاء التقييم بنجاح',
            evaluation=evaluation.to_dict()
        ), 201
    
    except Exception as e:
        logger.error(f"خطأ في إنشاء التقييم: {str(e)}")
        db.session.rollback()
        return jsonify(
            status='error',
            message='حدث خطأ أثناء إنشاء التقييم',
            error=str(e)
        ), 500

@evaluation_bp.route('/', methods=['GET'])
@jwt_required()
def get_evaluations():
    """
    الحصول على قائمة التقييمات
    """
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify(
                status='error',
                message='المستخدم غير موجود'
            ), 404
        
        # معلمات التصفح
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        # معلمات التصفية
        filter_type = request.args.get('filter', 'all')  # all, evaluator, student
        status = request.args.get('status')
        course_id = request.args.get('course_id', type=int)
        
        # إعداد الاستعلام
        query = Evaluation.query
        
        # تطبيق التصفية
        if filter_type == 'evaluator':
            query = query.filter_by(evaluator_id=user_id)
        elif filter_type == 'student':
            query = query.filter_by(student_id=user_id)
        elif not (user.is_admin() or user.is_instructor()):
            # إذا لم يكن المستخدم مسؤولاً أو مدرساً، فلا يمكنه الوصول إلا إلى تقييماته
            query = query.filter((Evaluation.evaluator_id == user_id) | (Evaluation.student_id == user_id))
        
        # تصفية حسب الحالة
        if status:
            query = query.filter_by(status=status)
        
        # تصفية حسب المساق
        if course_id:
            query = query.filter_by(course_id=course_id)
        
        # ترتيب النتائج
        query = query.order_by(Evaluation.created_at.desc())
        
        # تنفيذ الاستعلام مع التصفح
        evaluations = query.paginate(page=page, per_page=per_page)
        
        return jsonify(
            status='success',
            evaluations=[evaluation.to_dict() for evaluation in evaluations.items],
            total=evaluations.total,
            pages=evaluations.pages,
            page=page,
            per_page=per_page
        ), 200
    
    except Exception as e:
        logger.error(f"خطأ في الحصول على قائمة التقييمات: {str(e)}")
        return jsonify(
            status='error',
            message='حدث خطأ أثناء الحصول على قائمة التقييمات',
            error=str(e)
        ), 500

@evaluation_bp.route('/<int:evaluation_id>', methods=['GET'])
@jwt_required()
def get_evaluation(evaluation_id):
    """
    الحصول على تفاصيل تقييم
    
    Args:
        evaluation_id: معرف التقييم
    """
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify(
                status='error',
                message='المستخدم غير موجود'
            ), 404
        
        # الحصول على التقييم
        evaluation = Evaluation.query.get(evaluation_id)
        
        if not evaluation:
            return jsonify(
                status='error',
                message='التقييم غير موجود'
            ), 404
        
        # التحقق من الصلاحيات
        if not (user.is_admin() or user.is_instructor() or evaluation.evaluator_id == user_id or evaluation.student_id == user_id):
            return jsonify(
                status='error',
                message='ليس لديك صلاحية للوصول إلى هذا التقييم'
            ), 403
        
        return jsonify(
            status='success',
            evaluation=evaluation.to_dict()
        ), 200
    
    except Exception as e:
        logger.error(f"خطأ في الحصول على تفاصيل التقييم: {str(e)}")
        return jsonify(
            status='error',
            message='حدث خطأ أثناء الحصول على تفاصيل التقييم',
            error=str(e)
        ), 500

@evaluation_bp.route('/<int:evaluation_id>', methods=['PUT'])
@jwt_required()
def update_evaluation(evaluation_id):
    """
    تحديث تقييم
    
    Args:
        evaluation_id: معرف التقييم
    """
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify(
                status='error',
                message='المستخدم غير موجود'
            ), 404
        
        # الحصول على التقييم
        evaluation = Evaluation.query.get(evaluation_id)
        
        if not evaluation:
            return jsonify(
                status='error',
                message='التقييم غير موجود'
            ), 404
        
        # التحقق من الصلاحيات (يجب أن يكون المقيّم أو مسؤول)
        if not (user.is_admin() or evaluation.evaluator_id == user_id):
            return jsonify(
                status='error',
                message='ليس لديك صلاحية لتحديث هذا التقييم'
            ), 403
        
        data = request.get_json()
        
        # تحديث البيانات
        if 'title' in data:
            evaluation.title = data['title']
        
        if 'description' in data:
            evaluation.description = data['description']
        
        if 'task_description' in data:
            evaluation.task_description = data['task_description']
        
        if 'submission_text' in data:
            evaluation.submission_text = data['submission_text']
        
        if 'grade' in data:
            evaluation.grade = data['grade']
        
        if 'status' in data:
            evaluation.status = data['status']
            
            # إذا تم تغيير الحالة إلى "مكتمل"، قم بتحديث وقت الإكمال
            if evaluation.status == 'completed' and not evaluation.completed_at:
                evaluation.completed_at = datetime.utcnow()
        
        if 'feedback' in data:
            evaluation.feedback = data['feedback']
        
        if 'criteria' in data:
            evaluation.criteria = data['criteria']
        
        if 'rubric_id' in data:
            evaluation.rubric_id = data['rubric_id']
        
        if 'course_id' in data:
            evaluation.course_id = data['course_id']
        
        if 'media_files' in data:
            evaluation.media_files = data['media_files']
        
        # إذا تم طلب التقييم التلقائي
        if data.get('auto_evaluate', False):
            # استخدام الذكاء الاصطناعي للتقييم
            ai_evaluator = AIEvaluatorArabic()  # استخدام مقيّم اللغة العربية
            
            rubric = None
            if evaluation.rubric_id:
                rubric_template = RubricTemplate.query.get(evaluation.rubric_id)
                if rubric_template:
                    rubric = rubric_template.get_criteria()
            
            # إجراء التقييم
            evaluation_result = ai_evaluator.evaluate_task(
                evaluation.task_description,
                evaluation.submission_text,
                rubric=rubric,
                output_format='json'
            )
            
            if evaluation_result.get('success', False):
                evaluation.grade = evaluation_result.get('grade')
                evaluation.feedback = evaluation_result.get('feedback')
                
                # إذا تم توفير درجات لكل معيار
                if 'criteria_grades' in evaluation_result:
                    evaluation.criteria = {
                        'criteria_grades': evaluation_result.get('criteria_grades'),
                        'raw_response': evaluation_result.get('raw_response')
                    }
                
                evaluation.status = 'completed'
                evaluation.completed_at = datetime.utcnow()
            else:
                logger.error(f"خطأ في التقييم التلقائي: {evaluation_result.get('error')}")
        
        # حفظ التغييرات
        db.session.commit()
        
        return jsonify(
            status='success',
            message='تم تحديث التقييم بنجاح',
            evaluation=evaluation.to_dict()
        ), 200
    
    except Exception as e:
        logger.error(f"خطأ في تحديث التقييم: {str(e)}")
        db.session.rollback()
        return jsonify(
            status='error',
            message='حدث خطأ أثناء تحديث التقييم',
            error=str(e)
        ), 500

@evaluation_bp.route('/<int:evaluation_id>', methods=['DELETE'])
@jwt_required()
def delete_evaluation(evaluation_id):
    """
    حذف تقييم
    
    Args:
        evaluation_id: معرف التقييم
    """
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify(
                status='error',
                message='المستخدم غير موجود'
            ), 404
        
        # الحصول على التقييم
        evaluation = Evaluation.query.get(evaluation_id)
        
        if not evaluation:
            return jsonify(
                status='error',
                message='التقييم غير موجود'
            ), 404
        
        # التحقق من الصلاحيات (يجب أن يكون المقيّم أو مسؤول)
        if not (user.is_admin() or evaluation.evaluator_id == user_id):
            return jsonify(
                status='error',
                message='ليس لديك صلاحية لحذف هذا التقييم'
            ), 403
        
        # حذف التقييم
        db.session.delete(evaluation)
        db.session.commit()
        
        return jsonify(
            status='success',
            message='تم حذف التقييم بنجاح'
        ), 200
    
    except Exception as e:
        logger.error(f"خطأ في حذف التقييم: {str(e)}")
        db.session.rollback()
        return jsonify(
            status='error',
            message='حدث خطأ أثناء حذف التقييم',
            error=str(e)
        ), 500

@evaluation_bp.route('/<int:evaluation_id>/verify', methods=['POST'])
@jwt_required()
@blockchain_required
def verify_evaluation(evaluation_id):
    """
    التحقق من صحة تقييم باستخدام البلوكتشين
    
    Args:
        evaluation_id: معرف التقييم
    """
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify(
                status='error',
                message='المستخدم غير موجود'
            ), 404
        
        # الحصول على التقييم
        evaluation = Evaluation.query.get(evaluation_id)
        
        if not evaluation:
            return jsonify(
                status='error',
                message='التقييم غير موجود'
            ), 404
        
        # التحقق من اكتمال التقييم
        if evaluation.status != 'completed':
            return jsonify(
                status='error',
                message='يجب أن يكون التقييم مكتملاً للتحقق منه'
            ), 400
        
        # التحقق من الصلاحيات (يجب أن يكون المقيّم أو مسؤول)
        if not (user.is_admin() or user.is_instructor() or evaluation.evaluator_id == user_id):
            return jsonify(
                status='error',
                message='ليس لديك صلاحية للتحقق من هذا التقييم'
            ), 403
        
        # إنشاء متحقق البلوكتشين
        verifier = BlockchainVerifier()
        
        # التحقق من صحة التقييم
        result = verifier.verify_evaluation(evaluation.to_dict())
        
        if result.get('verified', False):
            # تحديث بيانات التحقق
            evaluation.set_verification_data(result)
            
            return jsonify(
                status='success',
                message='تم التحقق من صحة التقييم بنجاح',
                verification=result
            ), 200
        else:
            # إذا لم يتم التحقق، قم بتخزين التقييم في البلوكتشين
            store_result = verifier.store_evaluation(evaluation.to_dict())
            
            if store_result.get('success', False):
                # تحديث بيانات التحقق
                evaluation.set_verification_data(store_result)
                
                return jsonify(
                    status='success',
                    message='تم تخزين التقييم في البلوكتشين بنجاح',
                    verification=store_result
                ), 200
            else:
                return jsonify(
                    status='error',
                    message='فشل تخزين التقييم في البلوكتشين',
                    error=store_result.get('error')
                ), 500
    
    except Exception as e:
        logger.error(f"خطأ في التحقق من صحة التقييم: {str(e)}")
        db.session.rollback()
        return jsonify(
            status='error',
            message='حدث خطأ أثناء التحقق من صحة التقييم',
            error=str(e)
        ), 500

@evaluation_bp.route('/ai-evaluate', methods=['POST'])
@jwt_required()
def ai_evaluate():
    """
    تقييم نص باستخدام الذكاء الاصطناعي
    """
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify(
                status='error',
                message='المستخدم غير موجود'
            ), 404
        
        # التحقق من أن المستخدم مدرس أو مسؤول
        if not (user.is_instructor() or user.is_admin()):
            return jsonify(
                status='error',
                message='يجب أن تكون مدرسًا أو مسؤولاً لاستخدام هذه الميزة'
            ), 403
        
        data = request.get_json()
        
        # التحقق من البيانات
        if not data or not data.get('task_description') or not data.get('submission_text'):
            return jsonify(
                status='error',
                message='وصف المهمة ونص التقديم مطلوبان'
            ), 400
        
        task_description = data.get('task_description')
        submission_text = data.get('submission_text')
        output_format = data.get('output_format', 'json')
        
        # إعداد الروبريك إذا تم توفيره
        rubric = None
        if 'rubric_id' in data and data.get('rubric_id'):
            rubric_id = data.get('rubric_id')
            rubric_template = RubricTemplate.query.get(rubric_id)
            
            if rubric_template:
                rubric = rubric_template.get_criteria()
        elif 'rubric' in data and data.get('rubric'):
            rubric = data.get('rubric')
        
        # استخدام مقيّم الذكاء الاصطناعي
        ai_evaluator = AIEvaluatorArabic()  # استخدام مقيّم اللغة العربية
        
        # إجراء التقييم
        evaluation_result = ai_evaluator.evaluate_task(
            task_description,
            submission_text,
            rubric=rubric,
            output_format=output_format
        )
        
        if evaluation_result.get('success', False):
            return jsonify(
                status='success',
                evaluation=evaluation_result
            ), 200
        else:
            return jsonify(
                status='error',
                message='فشل التقييم التلقائي',
                error=evaluation_result.get('error')
            ), 500
    
    except Exception as e:
        logger.error(f"خطأ في التقييم التلقائي: {str(e)}")
        return jsonify(
            status='error',
            message='حدث خطأ أثناء التقييم التلقائي',
            error=str(e)
        ), 500

# مسارات المساقات
@evaluation_bp.route('/courses', methods=['GET'])
@jwt_required()
def get_courses():
    """
    الحصول على قائمة المساقات
    """
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        # إعداد الاستعلام
        query = Course.query
        
        # تنفيذ الاستعلام مع التصفح
        courses = query.paginate(page=page, per_page=per_page)
        
        return jsonify(
            status='success',
            courses=[course.to_dict() for course in courses.items],
            total=courses.total,
            pages=courses.pages,
            page=page,
            per_page=per_page
        ), 200
    
    except Exception as e:
        logger.error(f"خطأ في الحصول على قائمة المساقات: {str(e)}")
        return jsonify(
            status='error',
            message='حدث خطأ أثناء الحصول على قائمة المساقات',
            error=str(e)
        ), 500

@evaluation_bp.route('/courses', methods=['POST'])
@jwt_required()
@instructor_required
def create_course():
    """
    إنشاء مساق جديد
    """
    try:
        user_id = get_jwt_identity()
        
        data = request.get_json()
        
        # التحقق من البيانات
        required_fields = ['code', 'name']
        for field in required_fields:
            if field not in data:
                return jsonify(
                    status='error',
                    message=f'الحقل {field} مطلوب'
                ), 400
        
        # التحقق من أن رمز المساق غير مستخدم
        if Course.query.filter_by(code=data.get('code')).first():
            return jsonify(
                status='error',
                message='رمز المساق مستخدم بالفعل'
            ), 400
        
        # إنشاء المساق
        course = Course()
        course.code = data.get('code')
        course.name = data.get('name')
        course.description = data.get('description')
        course.institution = data.get('institution')
        course.level = data.get('level')
        course.credits = data.get('credits')
        course.instructor_id = user_id
        
        # حفظ المساق
        db.session.add(course)
        db.session.commit()
        
        return jsonify(
            status='success',
            message='تم إنشاء المساق بنجاح',
            course=course.to_dict()
        ), 201
    
    except Exception as e:
        logger.error(f"خطأ في إنشاء المساق: {str(e)}")
        db.session.rollback()
        return jsonify(
            status='error',
            message='حدث خطأ أثناء إنشاء المساق',
            error=str(e)
        ), 500

# مسارات معايير التقييم
@evaluation_bp.route('/rubrics', methods=['GET'])
@jwt_required()
def get_rubrics():
    """
    الحصول على قائمة معايير التقييم
    """
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        # إعداد الاستعلام
        query = RubricTemplate.query
        
        # تنفيذ الاستعلام مع التصفح
        rubrics = query.paginate(page=page, per_page=per_page)
        
        return jsonify(
            status='success',
            rubrics=[rubric.to_dict() for rubric in rubrics.items],
            total=rubrics.total,
            pages=rubrics.pages,
            page=page,
            per_page=per_page
        ), 200
    
    except Exception as e:
        logger.error(f"خطأ في الحصول على قائمة معايير التقييم: {str(e)}")
        return jsonify(
            status='error',
            message='حدث خطأ أثناء الحصول على قائمة معايير التقييم',
            error=str(e)
        ), 500

@evaluation_bp.route('/rubrics', methods=['POST'])
@jwt_required()
@instructor_required
def create_rubric():
    """
    إنشاء معيار تقييم جديد
    """
    try:
        user_id = get_jwt_identity()
        
        data = request.get_json()
        
        # التحقق من البيانات
        required_fields = ['name', 'criteria']
        for field in required_fields:
            if field not in data:
                return jsonify(
                    status='error',
                    message=f'الحقل {field} مطلوب'
                ), 400
        
        # إنشاء معيار التقييم
        rubric = RubricTemplate()
        rubric.name = data.get('name')
        rubric.description = data.get('description')
        rubric.user_id = user_id
        
        # إعداد معايير التقييم
        criteria = data.get('criteria')
        rubric.set_criteria(criteria)
        
        # حفظ معيار التقييم
        db.session.add(rubric)
        db.session.commit()
        
        return jsonify(
            status='success',
            message='تم إنشاء معيار التقييم بنجاح',
            rubric=rubric.to_dict()
        ), 201
    
    except Exception as e:
        logger.error(f"خطأ في إنشاء معيار التقييم: {str(e)}")
        db.session.rollback()
        return jsonify(
            status='error',
            message='حدث خطأ أثناء إنشاء معيار التقييم',
            error=str(e)
        ), 500