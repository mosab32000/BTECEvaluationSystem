"""
مسارات التقييم في نظام تقييم BTEC
"""
import logging
import json
from datetime import datetime
import os

from flask import Blueprint, request, jsonify, render_template, redirect
from flask import url_for, session, flash, current_app
from flask_login import login_required, current_user
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.models.user import User
from app.models.evaluation import Evaluation
from app.models.rubric import Rubric

# تهيئة السجل
logger = logging.getLogger(__name__)

# إنشاء blueprint للتقييم
bp = Blueprint('evaluation', __name__, url_prefix='/evaluation')

@bp.route('/')
@login_required
def index():
    """صفحة قائمة التقييمات"""
    # الحصول على التقييمات حسب دور المستخدم
    if current_user.role == 'admin':
        # المسؤول يمكنه رؤية جميع التقييمات
        evaluations = Evaluation.get_all(limit=50)
    elif current_user.role == 'evaluator':
        # المقيم يمكنه رؤية التقييمات المخصصة له أو التي قام بتقييمها
        evaluations = Evaluation.get_by_evaluator_id(current_user.id, limit=50)
    else:
        # الطالب يمكنه رؤية تقييماته فقط
        evaluations = Evaluation.get_by_student_id(current_user.id, limit=50)
    
    return render_template('evaluation/index.html', evaluations=evaluations)

@bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    """صفحة إنشاء تقييم جديد"""
    # التحقق من صلاحية الوصول
    if current_user.role not in ['admin', 'evaluator']:
        flash('ليس لديك صلاحية للوصول إلى هذه الصفحة', 'error')
        return redirect(url_for('evaluation.index'))
    
    if request.method == 'POST':
        # الحصول على بيانات النموذج
        student_id = request.form.get('student_id')
        assignment_id = request.form.get('assignment_id')
        rubric_id = request.form.get('rubric_id')
        submission_text = request.form.get('submission_text')
        
        # التحقق من البيانات
        error = None
        if not student_id:
            error = 'يجب تحديد الطالب'
        elif not assignment_id:
            error = 'يجب تحديد المهمة'
        elif not submission_text:
            error = 'نص المهمة مطلوب'
        
        if error is None:
            # إنشاء تقييم جديد
            evaluation = Evaluation()
            evaluation.student_id = int(student_id)
            evaluation.assignment_id = assignment_id
            evaluation.rubric_id = int(rubric_id) if rubric_id else None
            evaluation.submission_text = submission_text
            evaluation.evaluator_id = current_user.id
            evaluation.status = 'pending'
            
            # حفظ التقييم
            if evaluation.save():
                flash('تم إنشاء التقييم بنجاح', 'success')
                return redirect(url_for('evaluation.view', evaluation_id=evaluation.id))
            else:
                error = 'حدث خطأ أثناء إنشاء التقييم'
        
        if error:
            flash(error, 'error')
    
    # الحصول على قائمة الطلاب ومعايير التقييم
    students = User.get_by_role('student')
    rubrics = Rubric.get_all()
    
    return render_template('evaluation/create.html', students=students, rubrics=rubrics)

@bp.route('/<int:evaluation_id>')
@login_required
def view(evaluation_id):
    """صفحة عرض تقييم"""
    # الحصول على التقييم
    evaluation = Evaluation.get_by_id(evaluation_id)
    
    if not evaluation:
        flash('التقييم غير موجود', 'error')
        return redirect(url_for('evaluation.index'))
    
    # التحقق من صلاحية الوصول
    if current_user.role not in ['admin', 'evaluator'] and evaluation.student_id != current_user.id:
        flash('ليس لديك صلاحية للوصول إلى هذا التقييم', 'error')
        return redirect(url_for('evaluation.index'))
    
    return render_template('evaluation/view.html', evaluation=evaluation)

@bp.route('/<int:evaluation_id>/evaluate', methods=['GET', 'POST'])
@login_required
def evaluate(evaluation_id):
    """صفحة تقييم مهمة"""
    # التحقق من صلاحية الوصول
    if current_user.role not in ['admin', 'evaluator']:
        flash('ليس لديك صلاحية للوصول إلى هذه الصفحة', 'error')
        return redirect(url_for('evaluation.index'))
    
    # الحصول على التقييم
    evaluation = Evaluation.get_by_id(evaluation_id)
    
    if not evaluation:
        flash('التقييم غير موجود', 'error')
        return redirect(url_for('evaluation.index'))
    
    if request.method == 'POST':
        # الحصول على بيانات النموذج
        score = request.form.get('score')
        evaluator_comments = request.form.get('evaluator_comments')
        
        # تحديث التقييم
        evaluation.score = float(score) if score else None
        evaluation.evaluator_comments = evaluator_comments
        evaluation.evaluator_id = current_user.id
        evaluation.status = 'completed'
        
        # حفظ التقييم
        if evaluation.save():
            flash('تم تقييم المهمة بنجاح', 'success')
            return redirect(url_for('evaluation.view', evaluation_id=evaluation.id))
        else:
            flash('حدث خطأ أثناء حفظ التقييم', 'error')
    
    # الحصول على معيار التقييم إذا كان موجودًا
    rubric = None
    if evaluation.rubric_id:
        rubric = Rubric.get_by_id(evaluation.rubric_id)
    
    return render_template('evaluation/evaluate.html', evaluation=evaluation, rubric=rubric)

@bp.route('/<int:evaluation_id>/ai-evaluate', methods=['POST'])
@login_required
def ai_evaluate(evaluation_id):
    """طلب تقييم بواسطة الذكاء الاصطناعي"""
    # التحقق من صلاحية الوصول
    if current_user.role not in ['admin', 'evaluator']:
        return jsonify({'error': 'ليس لديك صلاحية للوصول إلى هذه الوظيفة'}), 403
    
    # التحقق من تمكين الذكاء الاصطناعي
    if not current_app.config.get('AI_ENABLED', False):
        return jsonify({'error': 'ميزة الذكاء الاصطناعي غير مفعلة'}), 400
    
    # الحصول على التقييم
    evaluation = Evaluation.get_by_id(evaluation_id)
    
    if not evaluation:
        return jsonify({'error': 'التقييم غير موجود'}), 404
    
    try:
        # TODO: تنفيذ التقييم بالذكاء الاصطناعي
        # في هذه المرحلة، نستخدم استدعاء وهمي للتقييم الآلي
        
        # تحديث التقييم
        evaluation.ai_score = 0  # سيتم تعيينه من نتيجة الذكاء الاصطناعي
        evaluation.evaluation_result = {}  # سيتم تعيينه من نتيجة الذكاء الاصطناعي
        evaluation.save()
        
        return jsonify({'message': 'تم بدء التقييم بواسطة الذكاء الاصطناعي'}), 200
    
    except Exception as e:
        logger.error(f"خطأ في التقييم بالذكاء الاصطناعي: {e}")
        return jsonify({'error': 'حدث خطأ أثناء التقييم'}), 500

@bp.route('/api/evaluations', methods=['GET'])
@jwt_required()
def api_evaluations():
    """واجهة API للحصول على قائمة التقييمات"""
    user_id = get_jwt_identity()
    user = User.get_by_id(user_id)
    
    if not user:
        return jsonify({'error': 'المستخدم غير موجود'}), 404
    
    # الحصول على التقييمات حسب دور المستخدم
    if user.role == 'admin':
        # المسؤول يمكنه رؤية جميع التقييمات
        evaluations = Evaluation.get_all(limit=50)
    elif user.role == 'evaluator':
        # المقيم يمكنه رؤية التقييمات المخصصة له أو التي قام بتقييمها
        evaluations = Evaluation.get_by_evaluator_id(user.id, limit=50)
    else:
        # الطالب يمكنه رؤية تقييماته فقط
        evaluations = Evaluation.get_by_student_id(user.id, limit=50)
    
    # تحويل التقييمات إلى قاموس
    results = []
    for evaluation in evaluations:
        results.append(evaluation.to_dict())
    
    return jsonify(results), 200

@bp.route('/api/evaluations/<int:evaluation_id>', methods=['GET'])
@jwt_required()
def api_get_evaluation(evaluation_id):
    """واجهة API للحصول على تقييم محدد"""
    user_id = get_jwt_identity()
    user = User.get_by_id(user_id)
    
    if not user:
        return jsonify({'error': 'المستخدم غير موجود'}), 404
    
    # الحصول على التقييم
    evaluation = Evaluation.get_by_id(evaluation_id)
    
    if not evaluation:
        return jsonify({'error': 'التقييم غير موجود'}), 404
    
    # التحقق من صلاحية الوصول
    if user.role not in ['admin', 'evaluator'] and evaluation.student_id != user.id:
        return jsonify({'error': 'ليس لديك صلاحية للوصول إلى هذا التقييم'}), 403
    
    return jsonify(evaluation.to_dict()), 200

@bp.route('/api/evaluations', methods=['POST'])
@jwt_required()
def api_create_evaluation():
    """واجهة API لإنشاء تقييم جديد"""
    user_id = get_jwt_identity()
    user = User.get_by_id(user_id)
    
    if not user:
        return jsonify({'error': 'المستخدم غير موجود'}), 404
    
    # التحقق من صلاحية الوصول
    if user.role not in ['admin', 'evaluator']:
        return jsonify({'error': 'ليس لديك صلاحية لإنشاء تقييم'}), 403
    
    data = request.get_json() or {}
    
    # التحقق من البيانات المطلوبة
    if not data.get('student_id'):
        return jsonify({'error': 'معرف الطالب مطلوب'}), 400
    elif not data.get('assignment_id'):
        return jsonify({'error': 'معرف المهمة مطلوب'}), 400
    elif not data.get('submission_text'):
        return jsonify({'error': 'نص المهمة مطلوب'}), 400
    
    # إنشاء تقييم جديد
    evaluation = Evaluation()
    evaluation.student_id = int(data['student_id'])
    evaluation.assignment_id = data['assignment_id']
    evaluation.rubric_id = int(data['rubric_id']) if data.get('rubric_id') else None
    evaluation.submission_text = data['submission_text']
    evaluation.evaluator_id = user.id
    evaluation.status = 'pending'
    
    # حفظ التقييم
    if not evaluation.save():
        return jsonify({'error': 'حدث خطأ أثناء إنشاء التقييم'}), 500
    
    return jsonify(evaluation.to_dict()), 201

@bp.route('/api/evaluations/<int:evaluation_id>/evaluate', methods=['POST'])
@jwt_required()
def api_evaluate(evaluation_id):
    """واجهة API لتقييم مهمة"""
    user_id = get_jwt_identity()
    user = User.get_by_id(user_id)
    
    if not user:
        return jsonify({'error': 'المستخدم غير موجود'}), 404
    
    # التحقق من صلاحية الوصول
    if user.role not in ['admin', 'evaluator']:
        return jsonify({'error': 'ليس لديك صلاحية لتقييم المهمة'}), 403
    
    # الحصول على التقييم
    evaluation = Evaluation.get_by_id(evaluation_id)
    
    if not evaluation:
        return jsonify({'error': 'التقييم غير موجود'}), 404
    
    data = request.get_json() or {}
    
    # تحديث التقييم
    if 'score' in data:
        evaluation.score = float(data['score'])
    
    if 'evaluator_comments' in data:
        evaluation.evaluator_comments = data['evaluator_comments']
    
    evaluation.evaluator_id = user.id
    evaluation.status = 'completed'
    
    # حفظ التقييم
    if not evaluation.save():
        return jsonify({'error': 'حدث خطأ أثناء حفظ التقييم'}), 500
    
    return jsonify(evaluation.to_dict()), 200