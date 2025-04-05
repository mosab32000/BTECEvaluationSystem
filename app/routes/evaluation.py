"""
مسارات التقييم في نظام تقييم BTEC
"""

import logging
from flask import render_template, redirect, url_for, request, flash, session, jsonify, abort

from app.routes import evaluation_bp
from app.models.evaluation import Evaluation
from app.models.rubric import Rubric
from app.models.user import User

logger = logging.getLogger(__name__)

@evaluation_bp.route('/')
def index():
    """صفحة عرض التقييمات"""
    # التحقق من تسجيل الدخول
    if 'user_id' not in session:
        flash('يجب تسجيل الدخول للوصول إلى هذه الصفحة', 'error')
        return redirect(url_for('auth.login'))
    
    # الحصول على التقييمات حسب دور المستخدم
    user = User.get_by_id(session['user_id'])
    if not user:
        session.clear()
        flash('حدث خطأ في جلستك. يرجى تسجيل الدخول مرة أخرى.', 'error')
        return redirect(url_for('auth.login'))
    
    if user.role == 'admin':
        # المسؤول يرى جميع التقييمات
        evaluations = Evaluation.get_all()
    elif user.role == 'teacher':
        # المدرس يرى التقييمات التي قام بتقييمها وغير المقيمة
        evaluations = Evaluation.get_by_evaluator(user.id) + Evaluation.get_pending()
    else:
        # الطالب يرى التقييمات الخاصة به فقط
        evaluations = Evaluation.get_by_student(user.id)
    
    return render_template('evaluation/index.html', evaluations=evaluations, user=user)

@evaluation_bp.route('/create', methods=['GET', 'POST'])
def create():
    """صفحة إنشاء تقييم جديد"""
    # التحقق من تسجيل الدخول
    if 'user_id' not in session:
        flash('يجب تسجيل الدخول للوصول إلى هذه الصفحة', 'error')
        return redirect(url_for('auth.login'))
    
    # الحصول على معايير التقييم المتاحة
    rubrics = Rubric.get_all()
    if not rubrics:
        flash('لا توجد معايير تقييم متاحة. يرجى إنشاء معايير أولاً.', 'error')
        return redirect(url_for('evaluation.index'))
    
    if request.method == 'POST':
        # الحصول على البيانات من النموذج
        student_id = session['user_id']  # الطالب هو المستخدم الحالي
        assignment_id = request.form.get('assignment_id')
        rubric_id = request.form.get('rubric_id')
        submission_text = request.form.get('submission_text')
        
        # التحقق من صحة البيانات
        if not assignment_id or not rubric_id or not submission_text:
            flash('جميع الحقول مطلوبة', 'error')
            return render_template('evaluation/create.html', rubrics=rubrics)
        
        # إنشاء تقييم جديد
        evaluation = Evaluation(
            student_id=student_id,
            assignment_id=assignment_id,
            rubric_id=rubric_id,
            submission_text=submission_text,
            status='pending'
        )
        
        if evaluation.save():
            flash('تم إنشاء التقييم بنجاح. سيتم تقييمه قريبًا.', 'success')
            return redirect(url_for('evaluation.view', evaluation_id=evaluation.id))
        else:
            flash('حدث خطأ أثناء إنشاء التقييم. يرجى المحاولة مرة أخرى.', 'error')
    
    return render_template('evaluation/create.html', rubrics=rubrics)

@evaluation_bp.route('/view/<int:evaluation_id>')
def view(evaluation_id):
    """صفحة عرض تفاصيل التقييم"""
    # التحقق من تسجيل الدخول
    if 'user_id' not in session:
        flash('يجب تسجيل الدخول للوصول إلى هذه الصفحة', 'error')
        return redirect(url_for('auth.login'))
    
    # الحصول على التقييم
    evaluation = Evaluation.get_by_id(evaluation_id)
    if not evaluation:
        flash('التقييم غير موجود', 'error')
        return redirect(url_for('evaluation.index'))
    
    # التحقق من صلاحية الوصول
    user = User.get_by_id(session['user_id'])
    if not user:
        session.clear()
        flash('حدث خطأ في جلستك. يرجى تسجيل الدخول مرة أخرى.', 'error')
        return redirect(url_for('auth.login'))
    
    # السماح بالوصول فقط للمسؤول أو المدرس أو الطالب صاحب التقييم
    if user.role not in ['admin', 'teacher'] and evaluation.student_id != user.id:
        flash('ليس لديك صلاحية الوصول إلى هذا التقييم', 'error')
        return redirect(url_for('evaluation.index'))
    
    # الحصول على معلومات إضافية
    student = User.get_by_id(evaluation.student_id)
    rubric = Rubric.get_by_id(evaluation.rubric_id)
    evaluator = User.get_by_id(evaluation.evaluator_id) if evaluation.evaluator_id else None
    
    return render_template('evaluation/view.html', evaluation=evaluation, student=student, rubric=rubric, evaluator=evaluator, user=user)

@evaluation_bp.route('/evaluate/<int:evaluation_id>', methods=['GET', 'POST'])
def evaluate(evaluation_id):
    """صفحة تقييم المهمة"""
    # التحقق من تسجيل الدخول
    if 'user_id' not in session:
        flash('يجب تسجيل الدخول للوصول إلى هذه الصفحة', 'error')
        return redirect(url_for('auth.login'))
    
    # التحقق من صلاحية المستخدم (المدرس أو المسؤول فقط)
    user = User.get_by_id(session['user_id'])
    if not user or user.role not in ['admin', 'teacher']:
        flash('ليس لديك صلاحية الوصول إلى هذه الصفحة', 'error')
        return redirect(url_for('evaluation.index'))
    
    # الحصول على التقييم
    evaluation = Evaluation.get_by_id(evaluation_id)
    if not evaluation:
        flash('التقييم غير موجود', 'error')
        return redirect(url_for('evaluation.index'))
    
    # التحقق من حالة التقييم
    if evaluation.status != 'pending':
        flash('لا يمكن تقييم مهمة تم تقييمها مسبقًا', 'error')
        return redirect(url_for('evaluation.view', evaluation_id=evaluation.id))
    
    # الحصول على معايير التقييم
    rubric = Rubric.get_by_id(evaluation.rubric_id)
    if not rubric:
        flash('معايير التقييم غير موجودة', 'error')
        return redirect(url_for('evaluation.index'))
    
    if request.method == 'POST':
        # الحصول على البيانات من النموذج
        score = request.form.get('score')
        evaluator_comments = request.form.get('evaluator_comments')
        
        # التحقق من صحة البيانات
        if not score or not evaluator_comments:
            flash('جميع الحقول مطلوبة', 'error')
            return render_template('evaluation/evaluate.html', evaluation=evaluation, rubric=rubric)
        
        # تحديث التقييم
        evaluation.evaluator_id = user.id
        evaluation.score = float(score)
        evaluation.evaluator_comments = evaluator_comments
        evaluation.status = 'completed'
        
        if evaluation.save():
            flash('تم تقييم المهمة بنجاح', 'success')
            return redirect(url_for('evaluation.view', evaluation_id=evaluation.id))
        else:
            flash('حدث خطأ أثناء تقييم المهمة. يرجى المحاولة مرة أخرى.', 'error')
    
    return render_template('evaluation/evaluate.html', evaluation=evaluation, rubric=rubric)

@evaluation_bp.route('/api/get_evaluation/<int:evaluation_id>')
def api_get_evaluation(evaluation_id):
    """واجهة API للحصول على تفاصيل التقييم"""
    # التحقق من تسجيل الدخول
    if 'user_id' not in session:
        return jsonify({'error': 'يجب تسجيل الدخول للوصول إلى هذه الصفحة'}), 401
    
    # الحصول على التقييم
    evaluation = Evaluation.get_by_id(evaluation_id)
    if not evaluation:
        return jsonify({'error': 'التقييم غير موجود'}), 404
    
    # التحقق من صلاحية الوصول
    user = User.get_by_id(session['user_id'])
    if not user:
        return jsonify({'error': 'حدث خطأ في جلستك'}), 401
    
    # السماح بالوصول فقط للمسؤول أو المدرس أو الطالب صاحب التقييم
    if user.role not in ['admin', 'teacher'] and evaluation.student_id != user.id:
        return jsonify({'error': 'ليس لديك صلاحية الوصول إلى هذا التقييم'}), 403
    
    # إرجاع بيانات التقييم
    return jsonify({
        'evaluation': evaluation.to_dict(),
        'student': User.get_by_id(evaluation.student_id).to_dict() if evaluation.student_id else None,
        'rubric': Rubric.get_by_id(evaluation.rubric_id).to_dict() if evaluation.rubric_id else None,
        'evaluator': User.get_by_id(evaluation.evaluator_id).to_dict() if evaluation.evaluator_id else None
    })