"""
مسارات التقييم في نظام تقييم BTEC
"""
import logging
import json
from datetime import datetime
import os

from flask import Blueprint, request, jsonify, render_template, redirect, url_for, flash, current_app, abort
from flask_login import login_required, current_user
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.models.user import User
from app.models.rubric import Rubric
from app.models.evaluation import Evaluation

# تهيئة السجل
logger = logging.getLogger(__name__)

# إنشاء Blueprint
bp = Blueprint('evaluation', __name__, url_prefix='/evaluation')

@bp.route('/')
@login_required
def evaluation_dashboard():
    """
    لوحة تحكم التقييمات
    
    Returns:
        Response: استجابة HTTP
    """
    # تحميل التقييمات بناءً على دور المستخدم
    evaluations = []
    
    if current_user.role == 'admin':
        # المسؤول يرى جميع التقييمات
        evaluations = Evaluation.get_all(limit=50)
    elif current_user.role == 'evaluator':
        # المقيم يرى التقييمات المخصصة له
        evaluations = Evaluation.get_by_user(current_user.id, limit=50)
    elif current_user.role == 'student':
        # الطالب يرى تقييماته فقط
        evaluations = Evaluation.get_by_student(current_user.id, limit=50)
    
    # تحميل الروبريكات (معايير التقييم)
    rubrics = Rubric.get_all()
    
    # تحميل المستخدمين (للمسؤول والمقيم)
    students = []
    if current_user.role in ['admin', 'evaluator']:
        students = User.get_by_role('student')
    
    return render_template(
        'evaluation/dashboard.html',
        evaluations=evaluations,
        rubrics=rubrics,
        students=students
    )

@bp.route('/view/<int:evaluation_id>')
@login_required
def view_evaluation(evaluation_id):
    """
    عرض تقييم محدد
    
    Args:
        evaluation_id (int): معرف التقييم
        
    Returns:
        Response: استجابة HTTP
    """
    evaluation = Evaluation.get_by_id(evaluation_id)
    
    if not evaluation:
        flash("التقييم غير موجود", "error")
        return redirect(url_for('evaluation.evaluation_dashboard'))
    
    # التحقق من الصلاحيات (الطالب يمكنه فقط مشاهدة تقييماته)
    if current_user.role == 'student' and evaluation.student_id != current_user.id:
        flash("ليس لديك صلاحية لعرض هذا التقييم", "error")
        return redirect(url_for('evaluation.evaluation_dashboard'))
    
    # الحصول على الروبريك المستخدم والمستخدمين المرتبطين
    rubric = Rubric.get_by_id(evaluation.rubric_id)
    student = User.get_by_id(evaluation.student_id)
    evaluator = User.get_by_id(evaluation.evaluator_id) if evaluation.evaluator_id else None
    
    # الحصول على بيانات التحقق من صحة التقييم
    verification = evaluation.get_verification()
    
    return render_template(
        'evaluation/view.html',
        evaluation=evaluation,
        rubric=rubric,
        student=student,
        evaluator=evaluator,
        verification=verification
    )

@bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_evaluation():
    """
    إنشاء تقييم جديد
    
    Returns:
        Response: استجابة HTTP
    """
    # التحقق من الصلاحيات (فقط المسؤول والمقيم يمكنهم إنشاء تقييمات)
    if current_user.role not in ['admin', 'evaluator']:
        flash("ليس لديك صلاحية لإنشاء تقييمات", "error")
        return redirect(url_for('evaluation.evaluation_dashboard'))
    
    # للطلب GET، عرض نموذج إنشاء تقييم
    if request.method == 'GET':
        students = User.get_by_role('student')
        rubrics = Rubric.get_all()
        
        return render_template(
            'evaluation/create.html',
            students=students,
            rubrics=rubrics
        )
    
    # للطلب POST، إنشاء تقييم جديد
    # الحصول على بيانات النموذج
    if request.is_json:
        data = request.get_json()
    else:
        data = request.form
    
    student_id = data.get('student_id')
    rubric_id = data.get('rubric_id')
    assignment_id = data.get('assignment_id')
    submission_text = data.get('submission_text')
    
    # التحقق من البيانات المطلوبة
    if not student_id or not rubric_id:
        if request.is_json:
            return jsonify({"error": "يرجى تحديد الطالب ومعيار التقييم"}), 400
        flash("يرجى تحديد الطالب ومعيار التقييم", "error")
        return redirect(url_for('evaluation.create_evaluation'))
    
    # إنشاء تقييم جديد
    evaluation = Evaluation(
        student_id=student_id,
        rubric_id=rubric_id,
        assignment_id=assignment_id,
        submission_text=submission_text,
        evaluator_id=current_user.id,
        status='pending'
    )
    
    # حفظ التقييم
    if evaluation.save():
        logger.info(f"تم إنشاء تقييم جديد: ID={evaluation.id}")
        
        if request.is_json:
            return jsonify({
                "message": "تم إنشاء التقييم بنجاح",
                "evaluation": evaluation.to_dict()
            }), 201
        
        flash("تم إنشاء التقييم بنجاح", "success")
        return redirect(url_for('evaluation.view_evaluation', evaluation_id=evaluation.id))
    else:
        logger.error("فشل في إنشاء تقييم جديد")
        
        if request.is_json:
            return jsonify({"error": "فشل في إنشاء التقييم"}), 500
        
        flash("فشل في إنشاء التقييم، يرجى المحاولة مرة أخرى", "error")
        return redirect(url_for('evaluation.create_evaluation'))

@bp.route('/edit/<int:evaluation_id>', methods=['GET', 'POST'])
@login_required
def edit_evaluation(evaluation_id):
    """
    تعديل تقييم موجود
    
    Args:
        evaluation_id (int): معرف التقييم
        
    Returns:
        Response: استجابة HTTP
    """
    evaluation = Evaluation.get_by_id(evaluation_id)
    
    if not evaluation:
        if request.is_json:
            return jsonify({"error": "التقييم غير موجود"}), 404
        flash("التقييم غير موجود", "error")
        return redirect(url_for('evaluation.evaluation_dashboard'))
    
    # التحقق من الصلاحيات (فقط المسؤول والمقيم يمكنهم تعديل التقييمات)
    # المقيم يمكنه فقط تعديل تقييماته
    if current_user.role == 'evaluator' and evaluation.evaluator_id != current_user.id:
        if request.is_json:
            return jsonify({"error": "ليس لديك صلاحية لتعديل هذا التقييم"}), 403
        flash("ليس لديك صلاحية لتعديل هذا التقييم", "error")
        return redirect(url_for('evaluation.evaluation_dashboard'))
    elif current_user.role == 'student':
        if request.is_json:
            return jsonify({"error": "ليس لديك صلاحية لتعديل التقييمات"}), 403
        flash("ليس لديك صلاحية لتعديل التقييمات", "error")
        return redirect(url_for('evaluation.evaluation_dashboard'))
    
    # الحصول على معيار التقييم والطالب
    rubric = Rubric.get_by_id(evaluation.rubric_id)
    student = User.get_by_id(evaluation.student_id)
    
    # للطلب GET، عرض نموذج تعديل التقييم
    if request.method == 'GET':
        students = User.get_by_role('student')
        rubrics = Rubric.get_all()
        
        return render_template(
            'evaluation/edit.html',
            evaluation=evaluation,
            rubric=rubric,
            student=student,
            students=students,
            rubrics=rubrics
        )
    
    # للطلب POST، تحديث التقييم
    # الحصول على بيانات النموذج
    if request.is_json:
        data = request.get_json()
    else:
        data = request.form
    
    # تحديث بيانات التقييم
    if current_user.role == 'admin':
        # المسؤول يمكنه تحديث جميع الحقول
        student_id = data.get('student_id')
        rubric_id = data.get('rubric_id')
        if student_id:
            evaluation.student_id = student_id
        if rubric_id:
            evaluation.rubric_id = rubric_id
    
    assignment_id = data.get('assignment_id')
    submission_text = data.get('submission_text')
    score = data.get('score')
    evaluator_comments = data.get('evaluator_comments')
    status = data.get('status')
    evaluation_result = data.get('evaluation_result')
    
    if assignment_id:
        evaluation.assignment_id = assignment_id
    
    if submission_text:
        evaluation.submission_text = submission_text
    
    if score:
        try:
            evaluation.score = float(score)
        except ValueError:
            if request.is_json:
                return jsonify({"error": "قيمة الدرجة غير صالحة"}), 400
            flash("قيمة الدرجة غير صالحة", "error")
            return redirect(url_for('evaluation.edit_evaluation', evaluation_id=evaluation_id))
    
    if evaluator_comments:
        evaluation.evaluator_comments = evaluator_comments
    
    if status:
        evaluation.status = status
    
    if evaluation_result:
        if isinstance(evaluation_result, str):
            try:
                evaluation.evaluation_result = json.loads(evaluation_result)
            except json.JSONDecodeError:
                if request.is_json:
                    return jsonify({"error": "تنسيق نتيجة التقييم غير صالح"}), 400
                flash("تنسيق نتيجة التقييم غير صالح", "error")
                return redirect(url_for('evaluation.edit_evaluation', evaluation_id=evaluation_id))
        else:
            evaluation.evaluation_result = evaluation_result
    
    # حفظ التقييم
    if evaluation.save():
        logger.info(f"تم تحديث التقييم: ID={evaluation.id}")
        
        if request.is_json:
            return jsonify({
                "message": "تم تحديث التقييم بنجاح",
                "evaluation": evaluation.to_dict()
            }), 200
        
        flash("تم تحديث التقييم بنجاح", "success")
        return redirect(url_for('evaluation.view_evaluation', evaluation_id=evaluation.id))
    else:
        logger.error(f"فشل في تحديث التقييم: ID={evaluation.id}")
        
        if request.is_json:
            return jsonify({"error": "فشل في تحديث التقييم"}), 500
        
        flash("فشل في تحديث التقييم، يرجى المحاولة مرة أخرى", "error")
        return redirect(url_for('evaluation.edit_evaluation', evaluation_id=evaluation_id))

@bp.route('/delete/<int:evaluation_id>', methods=['POST'])
@login_required
def delete_evaluation(evaluation_id):
    """
    حذف تقييم
    
    Args:
        evaluation_id (int): معرف التقييم
        
    Returns:
        Response: استجابة HTTP
    """
    evaluation = Evaluation.get_by_id(evaluation_id)
    
    if not evaluation:
        if request.is_json:
            return jsonify({"error": "التقييم غير موجود"}), 404
        flash("التقييم غير موجود", "error")
        return redirect(url_for('evaluation.evaluation_dashboard'))
    
    # التحقق من الصلاحيات (فقط المسؤول يمكنه حذف التقييمات)
    if current_user.role != 'admin':
        if request.is_json:
            return jsonify({"error": "ليس لديك صلاحية لحذف التقييمات"}), 403
        flash("ليس لديك صلاحية لحذف التقييمات", "error")
        return redirect(url_for('evaluation.evaluation_dashboard'))
    
    # حذف التقييم
    if evaluation.delete():
        logger.info(f"تم حذف التقييم: ID={evaluation_id}")
        
        if request.is_json:
            return jsonify({"message": "تم حذف التقييم بنجاح"}), 200
        
        flash("تم حذف التقييم بنجاح", "success")
    else:
        logger.error(f"فشل في حذف التقييم: ID={evaluation_id}")
        
        if request.is_json:
            return jsonify({"error": "فشل في حذف التقييم"}), 500
        
        flash("فشل في حذف التقييم، يرجى المحاولة مرة أخرى", "error")
    
    return redirect(url_for('evaluation.evaluation_dashboard'))

@bp.route('/submit/<int:evaluation_id>', methods=['POST'])
@login_required
def submit_evaluation(evaluation_id):
    """
    تقديم تقييم (تغيير الحالة إلى 'submitted')
    
    Args:
        evaluation_id (int): معرف التقييم
        
    Returns:
        Response: استجابة HTTP
    """
    evaluation = Evaluation.get_by_id(evaluation_id)
    
    if not evaluation:
        if request.is_json:
            return jsonify({"error": "التقييم غير موجود"}), 404
        flash("التقييم غير موجود", "error")
        return redirect(url_for('evaluation.evaluation_dashboard'))
    
    # التحقق من الصلاحيات (فقط المقيم الذي أنشأ التقييم أو المسؤول)
    if current_user.role == 'evaluator' and evaluation.evaluator_id != current_user.id:
        if request.is_json:
            return jsonify({"error": "ليس لديك صلاحية لتقديم هذا التقييم"}), 403
        flash("ليس لديك صلاحية لتقديم هذا التقييم", "error")
        return redirect(url_for('evaluation.evaluation_dashboard'))
    elif current_user.role == 'student':
        if request.is_json:
            return jsonify({"error": "ليس لديك صلاحية لتقديم التقييمات"}), 403
        flash("ليس لديك صلاحية لتقديم التقييمات", "error")
        return redirect(url_for('evaluation.evaluation_dashboard'))
    
    # تحديث حالة التقييم
    evaluation.status = 'submitted'
    
    # حفظ التقييم
    if evaluation.save():
        logger.info(f"تم تقديم التقييم: ID={evaluation.id}")
        
        if request.is_json:
            return jsonify({
                "message": "تم تقديم التقييم بنجاح",
                "evaluation": evaluation.to_dict()
            }), 200
        
        flash("تم تقديم التقييم بنجاح", "success")
    else:
        logger.error(f"فشل في تقديم التقييم: ID={evaluation.id}")
        
        if request.is_json:
            return jsonify({"error": "فشل في تقديم التقييم"}), 500
        
        flash("فشل في تقديم التقييم، يرجى المحاولة مرة أخرى", "error")
    
    return redirect(url_for('evaluation.view_evaluation', evaluation_id=evaluation.id))

@bp.route('/verify/<int:evaluation_id>', methods=['POST'])
@login_required
def verify_evaluation(evaluation_id):
    """
    التحقق من صحة التقييم باستخدام البلوكتشين
    
    Args:
        evaluation_id (int): معرف التقييم
        
    Returns:
        Response: استجابة HTTP
    """
    # التحقق من الصلاحيات (فقط المسؤول يمكنه التحقق من صحة التقييمات)
    if current_user.role != 'admin':
        if request.is_json:
            return jsonify({"error": "ليس لديك صلاحية للتحقق من صحة التقييمات"}), 403
        flash("ليس لديك صلاحية للتحقق من صحة التقييمات", "error")
        return redirect(url_for('evaluation.evaluation_dashboard'))
    
    evaluation = Evaluation.get_by_id(evaluation_id)
    
    if not evaluation:
        if request.is_json:
            return jsonify({"error": "التقييم غير موجود"}), 404
        flash("التقييم غير موجود", "error")
        return redirect(url_for('evaluation.evaluation_dashboard'))
    
    # التحقق من أن التقييم تم تقديمه
    if evaluation.status != 'submitted':
        if request.is_json:
            return jsonify({"error": "يجب تقديم التقييم قبل التحقق من صحته"}), 400
        flash("يجب تقديم التقييم قبل التحقق من صحته", "error")
        return redirect(url_for('evaluation.view_evaluation', evaluation_id=evaluation.id))
    
    # إنشاء قيمة تجزئة للتقييم (بسيطة في هذا المثال)
    # في الواقع، يجب استخدام خوارزميات تجزئة آمنة مثل SHA-256
    import hashlib
    evaluation_data = json.dumps(evaluation.to_dict(), sort_keys=True)
    hash_value = hashlib.sha256(evaluation_data.encode('utf-8')).hexdigest()
    
    # يجب هنا إجراء عملية التحقق باستخدام البلوكتشين
    # هذا مثال بسيط فقط
    transaction_id = f"tx_{hash_value[:16]}"
    
    # إضافة سجل تحقق جديد
    if evaluation.add_verification(hash_value, transaction_id, True):
        # تحديث حالة التقييم
        evaluation.status = 'verified'
        evaluation.save()
        
        logger.info(f"تم التحقق من صحة التقييم: ID={evaluation.id}")
        
        if request.is_json:
            return jsonify({
                "message": "تم التحقق من صحة التقييم بنجاح",
                "hash": hash_value,
                "transaction_id": transaction_id
            }), 200
        
        flash("تم التحقق من صحة التقييم بنجاح", "success")
    else:
        logger.error(f"فشل في التحقق من صحة التقييم: ID={evaluation.id}")
        
        if request.is_json:
            return jsonify({"error": "فشل في التحقق من صحة التقييم"}), 500
        
        flash("فشل في التحقق من صحة التقييم، يرجى المحاولة مرة أخرى", "error")
    
    return redirect(url_for('evaluation.view_evaluation', evaluation_id=evaluation.id))

# مسارات API للتقييمات
@bp.route('/api/evaluations', methods=['GET'])
@jwt_required()
def api_get_evaluations():
    """
    الحصول على قائمة التقييمات عبر API
    
    Returns:
        Response: استجابة HTTP
    """
    current_user_id = get_jwt_identity()
    user = User.get_by_id(current_user_id)
    
    if not user:
        return jsonify({"error": "المستخدم غير موجود"}), 404
    
    limit = request.args.get('limit', 100, type=int)
    offset = request.args.get('offset', 0, type=int)
    
    # تحميل التقييمات بناءً على دور المستخدم
    evaluations = []
    
    if user.role == 'admin':
        # المسؤول يرى جميع التقييمات
        evaluations = Evaluation.get_all(limit=limit, offset=offset)
    elif user.role == 'evaluator':
        # المقيم يرى التقييمات المخصصة له
        evaluations = Evaluation.get_by_user(user.id, limit=limit, offset=offset)
    elif user.role == 'student':
        # الطالب يرى تقييماته فقط
        evaluations = Evaluation.get_by_student(user.id, limit=limit, offset=offset)
    
    # تحويل التقييمات إلى قواميس
    evaluations_data = [evaluation.to_dict() for evaluation in evaluations]
    
    return jsonify({
        "evaluations": evaluations_data,
        "count": len(evaluations_data),
        "limit": limit,
        "offset": offset
    }), 200

@bp.route('/api/evaluations/<int:evaluation_id>', methods=['GET'])
@jwt_required()
def api_get_evaluation(evaluation_id):
    """
    الحصول على تفاصيل تقييم عبر API
    
    Args:
        evaluation_id (int): معرف التقييم
        
    Returns:
        Response: استجابة HTTP
    """
    current_user_id = get_jwt_identity()
    user = User.get_by_id(current_user_id)
    
    if not user:
        return jsonify({"error": "المستخدم غير موجود"}), 404
    
    evaluation = Evaluation.get_by_id(evaluation_id)
    
    if not evaluation:
        return jsonify({"error": "التقييم غير موجود"}), 404
    
    # التحقق من الصلاحيات (الطالب يمكنه فقط مشاهدة تقييماته)
    if user.role == 'student' and evaluation.student_id != user.id:
        return jsonify({"error": "ليس لديك صلاحية لعرض هذا التقييم"}), 403
    
    # الحصول على البيانات المرتبطة
    rubric = Rubric.get_by_id(evaluation.rubric_id)
    student = User.get_by_id(evaluation.student_id)
    evaluator = User.get_by_id(evaluation.evaluator_id) if evaluation.evaluator_id else None
    verification = evaluation.get_verification()
    
    response_data = {
        "evaluation": evaluation.to_dict(),
        "rubric": rubric.to_dict() if rubric else None,
        "student": student.to_dict() if student else None,
        "evaluator": evaluator.to_dict() if evaluator else None,
        "verification": verification
    }
    
    return jsonify(response_data), 200

@bp.route('/api/evaluations', methods=['POST'])
@jwt_required()
def api_create_evaluation():
    """
    إنشاء تقييم جديد عبر API
    
    Returns:
        Response: استجابة HTTP
    """
    current_user_id = get_jwt_identity()
    user = User.get_by_id(current_user_id)
    
    if not user:
        return jsonify({"error": "المستخدم غير موجود"}), 404
    
    # التحقق من الصلاحيات (فقط المسؤول والمقيم يمكنهم إنشاء تقييمات)
    if user.role not in ['admin', 'evaluator']:
        return jsonify({"error": "ليس لديك صلاحية لإنشاء تقييمات"}), 403
    
    data = request.get_json()
    
    if not data:
        return jsonify({"error": "بيانات JSON غير صالحة"}), 400
    
    student_id = data.get('student_id')
    rubric_id = data.get('rubric_id')
    assignment_id = data.get('assignment_id')
    submission_text = data.get('submission_text')
    
    # التحقق من البيانات المطلوبة
    if not student_id or not rubric_id:
        return jsonify({"error": "يرجى تحديد الطالب ومعيار التقييم"}), 400
    
    # إنشاء تقييم جديد
    evaluation = Evaluation(
        student_id=student_id,
        rubric_id=rubric_id,
        assignment_id=assignment_id,
        submission_text=submission_text,
        evaluator_id=user.id,
        status='pending'
    )
    
    # حفظ التقييم
    if evaluation.save():
        logger.info(f"تم إنشاء تقييم جديد عبر API: ID={evaluation.id}")
        
        return jsonify({
            "message": "تم إنشاء التقييم بنجاح",
            "evaluation": evaluation.to_dict()
        }), 201
    else:
        logger.error("فشل في إنشاء تقييم جديد عبر API")
        
        return jsonify({"error": "فشل في إنشاء التقييم"}), 500