"""
مسارات التقييم في نظام تقييم BTEC
"""
import json
import logging
from datetime import datetime
from flask import Blueprint, request, jsonify, render_template, redirect, url_for, flash, abort
from flask_login import login_required, current_user
from flask_jwt_extended import jwt_required, get_jwt_identity

from app import db
from app.models.user import User
from app.models.evaluation import Evaluation
from app.models.rubric import Rubric
from app.core.ai_evaluator import AIEvaluator
from app.core.blockchain_verifier import BlockchainVerifier

# إنشاء مخطط مسارات التقييم
bp = Blueprint('evaluation', __name__, url_prefix='/evaluation')

# إعداد التسجيل
logger = logging.getLogger(__name__)

@bp.route('/')
@login_required
def index():
    """عرض قائمة التقييمات"""
    # الحصول على كل التقييمات للمستخدم الحالي أو كل التقييمات للمسؤول
    if current_user.is_admin:
        evaluations = Evaluation.query.order_by(Evaluation.created_at.desc()).all()
    else:
        evaluations = Evaluation.query.filter_by(user_id=current_user.id).order_by(Evaluation.created_at.desc()).all()
    
    return render_template('evaluation/index.html', evaluations=evaluations)

@bp.route('/new', methods=['GET', 'POST'])
@login_required
def new_evaluation():
    """إنشاء تقييم جديد"""
    # إذا كان الطلب POST (إرسال النموذج)
    if request.method == 'POST':
        title = request.form.get('title')
        task_description = request.form.get('task_description')
        submission_text = request.form.get('submission_text')
        use_ai = 'use_ai' in request.form
        rubric_id = request.form.get('rubric_id') if use_ai else None
        
        # التحقق من البيانات
        if not task_description or not submission_text:
            flash('وصف المهمة ونص الإجابة مطلوبان.', 'danger')
            rubrics = Rubric.query.all()
            return render_template('evaluation/new.html', rubrics=rubrics)
        
        # إنشاء تقييم جديد
        evaluation = Evaluation(
            title=title or 'تقييم جديد',
            task_description=task_description,
            submission_text=submission_text,
            user_id=current_user.id,
            rubric_id=rubric_id,
            created_at=datetime.utcnow(),
            is_ai_evaluated=use_ai
        )
        
        # حفظ التقييم في قاعدة البيانات
        try:
            evaluation.update_status()
            db.session.add(evaluation)
            db.session.commit()
            
            # إذا تم اختيار استخدام الذكاء الاصطناعي، انتقل إلى صفحة التقييم التلقائي
            if use_ai:
                return redirect(url_for('evaluation.ai_evaluate', id=evaluation.id))
            
            flash('تم إنشاء التقييم بنجاح.', 'success')
            return redirect(url_for('evaluation.view', id=evaluation.id))
        except Exception as e:
            db.session.rollback()
            logger.error(f"خطأ في إنشاء التقييم: {str(e)}")
            flash('حدث خطأ أثناء إنشاء التقييم. يرجى المحاولة مرة أخرى.', 'danger')
    
    # عرض صفحة التقييم الجديد
    rubrics = Rubric.query.all()
    return render_template('evaluation/new.html', rubrics=rubrics)

@bp.route('/<int:id>')
@login_required
def view(id):
    """عرض تفاصيل التقييم"""
    # الحصول على التقييم من قاعدة البيانات
    evaluation = Evaluation.query.get_or_404(id)
    
    # التحقق من صلاحية الوصول (المستخدم هو صاحب التقييم أو مسؤول)
    if evaluation.user_id != current_user.id and not current_user.is_admin:
        flash('ليس لديك صلاحية لعرض هذا التقييم.', 'danger')
        return redirect(url_for('evaluation.index'))
    
    return render_template('evaluation/view.html', evaluation=evaluation)

@bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit(id):
    """تعديل التقييم"""
    # الحصول على التقييم من قاعدة البيانات
    evaluation = Evaluation.query.get_or_404(id)
    
    # التحقق من صلاحية الوصول (المستخدم هو صاحب التقييم أو مسؤول)
    if evaluation.user_id != current_user.id and not current_user.is_admin:
        flash('ليس لديك صلاحية لتعديل هذا التقييم.', 'danger')
        return redirect(url_for('evaluation.index'))
    
    # التحقق من حالة التقييم (يمكن تعديل التقييمات المعلقة أو قيد التقدم فقط)
    if evaluation.status not in ['pending', 'in_progress']:
        flash('لا يمكن تعديل التقييم المكتمل أو المتحقق منه.', 'warning')
        return redirect(url_for('evaluation.view', id=evaluation.id))
    
    # إذا كان الطلب POST (إرسال النموذج)
    if request.method == 'POST':
        title = request.form.get('title')
        task_description = request.form.get('task_description')
        submission_text = request.form.get('submission_text')
        
        # التحقق من البيانات
        if not task_description or not submission_text:
            flash('وصف المهمة ونص الإجابة مطلوبان.', 'danger')
            return render_template('evaluation/edit.html', evaluation=evaluation)
        
        # تحديث التقييم
        evaluation.title = title or evaluation.title
        evaluation.task_description = task_description
        evaluation.submission_text = submission_text
        evaluation.updated_at = datetime.utcnow()
        
        # حفظ التغييرات في قاعدة البيانات
        try:
            db.session.commit()
            flash('تم تحديث التقييم بنجاح.', 'success')
            return redirect(url_for('evaluation.view', id=evaluation.id))
        except Exception as e:
            db.session.rollback()
            logger.error(f"خطأ في تحديث التقييم: {str(e)}")
            flash('حدث خطأ أثناء تحديث التقييم. يرجى المحاولة مرة أخرى.', 'danger')
    
    # عرض صفحة تعديل التقييم
    return render_template('evaluation/edit.html', evaluation=evaluation)

@bp.route('/<int:id>/manual-grade', methods=['GET', 'POST'])
@login_required
def manual_grade(id):
    """تقييم يدوي"""
    # الحصول على التقييم من قاعدة البيانات
    evaluation = Evaluation.query.get_or_404(id)
    
    # التحقق من صلاحية الوصول (المستخدم هو صاحب التقييم أو مسؤول)
    if evaluation.user_id != current_user.id and not current_user.is_admin:
        flash('ليس لديك صلاحية لتقييم هذا التقييم.', 'danger')
        return redirect(url_for('evaluation.index'))
    
    # إذا كان الطلب POST (إرسال النموذج)
    if request.method == 'POST':
        grade = request.form.get('grade')
        feedback = request.form.get('feedback')
        strengths = request.form.get('strengths')
        weaknesses = request.form.get('weaknesses')
        
        # التحقق من البيانات
        if not grade or not feedback:
            flash('الدرجة والتغذية الراجعة مطلوبان.', 'danger')
            return render_template('evaluation/manual_grade.html', evaluation=evaluation)
        
        # تحويل الدرجة إلى رقم عشري
        try:
            grade = float(grade)
            if grade < 0 or grade > 100:
                flash('يجب أن تكون الدرجة بين 0 و 100.', 'danger')
                return render_template('evaluation/manual_grade.html', evaluation=evaluation)
        except ValueError:
            flash('يجب أن تكون الدرجة رقمًا صحيحًا أو عشريًا.', 'danger')
            return render_template('evaluation/manual_grade.html', evaluation=evaluation)
        
        # تحديث التقييم
        evaluation.grade = grade
        evaluation.feedback = feedback
        evaluation.strengths = strengths if strengths else evaluation.strengths
        evaluation.weaknesses = weaknesses if weaknesses else evaluation.weaknesses
        evaluation.is_ai_evaluated = False
        evaluation.evaluated_at = datetime.utcnow()
        evaluation.status = 'completed'
        
        # حفظ التغييرات في قاعدة البيانات
        try:
            db.session.commit()
            flash('تم تقييم المهمة بنجاح.', 'success')
            return redirect(url_for('evaluation.view', id=evaluation.id))
        except Exception as e:
            db.session.rollback()
            logger.error(f"خطأ في تقييم المهمة: {str(e)}")
            flash('حدث خطأ أثناء تقييم المهمة. يرجى المحاولة مرة أخرى.', 'danger')
    
    # عرض صفحة التقييم اليدوي
    return render_template('evaluation/manual_grade.html', evaluation=evaluation)

@bp.route('/<int:id>/ai-evaluate')
@login_required
def ai_evaluate(id):
    """تقييم باستخدام الذكاء الاصطناعي"""
    # الحصول على التقييم من قاعدة البيانات
    evaluation = Evaluation.query.get_or_404(id)
    
    # التحقق من صلاحية الوصول (المستخدم هو صاحب التقييم أو مسؤول)
    if evaluation.user_id != current_user.id and not current_user.is_admin:
        flash('ليس لديك صلاحية لتقييم هذا التقييم.', 'danger')
        return redirect(url_for('evaluation.index'))
    
    # التحقق من تمكين الذكاء الاصطناعي في الإعدادات
    from flask import current_app
    if not current_app.config.get('AI_ENABLED'):
        flash('تقييم الذكاء الاصطناعي غير ممكّن حاليًا.', 'warning')
        return redirect(url_for('evaluation.view', id=evaluation.id))
    
    # التحقق من وجود مفتاح API للذكاء الاصطناعي
    if not current_app.config.get('OPENAI_API_KEY'):
        flash('مفتاح API للذكاء الاصطناعي غير متوفر.', 'danger')
        return redirect(url_for('evaluation.view', id=evaluation.id))
    
    # عرض صفحة التقييم بالذكاء الاصطناعي
    rubric = None
    if evaluation.rubric_id:
        rubric = Rubric.query.get(evaluation.rubric_id)
    
    return render_template('evaluation/ai_evaluate.html', evaluation=evaluation, rubric=rubric)

@bp.route('/<int:id>/process-ai-evaluation', methods=['POST'])
@login_required
def process_ai_evaluation(id):
    """معالجة تقييم الذكاء الاصطناعي"""
    # الحصول على التقييم من قاعدة البيانات
    evaluation = Evaluation.query.get_or_404(id)
    
    # التحقق من صلاحية الوصول (المستخدم هو صاحب التقييم أو مسؤول)
    if evaluation.user_id != current_user.id and not current_user.is_admin:
        return jsonify({'success': False, 'message': 'ليس لديك صلاحية لتقييم هذا التقييم.'}), 403
    
    # التحقق من تمكين الذكاء الاصطناعي في الإعدادات
    from flask import current_app
    if not current_app.config.get('AI_ENABLED'):
        return jsonify({'success': False, 'message': 'تقييم الذكاء الاصطناعي غير ممكّن حاليًا.'}), 403
    
    # إنشاء مقيم الذكاء الاصطناعي
    ai_evaluator = AIEvaluator()
    
    try:
        # الحصول على معايير التقييم إذا كانت موجودة
        rubric = None
        if evaluation.rubric_id:
            rubric = Rubric.query.get(evaluation.rubric_id)
            rubric_dict = rubric.get_criteria_dict() if rubric else None
        else:
            rubric_dict = None
        
        # إجراء التقييم باستخدام الذكاء الاصطناعي
        result = ai_evaluator.evaluate_submission(
            task_description=evaluation.task_description,
            submission_text=evaluation.submission_text,
            rubric=rubric_dict,
            language=evaluation.language
        )
        
        # تحديث التقييم بنتائج الذكاء الاصطناعي
        evaluation.grade = result.get('grade')
        evaluation.feedback = result.get('feedback')
        evaluation.strengths = result.get('strengths')
        evaluation.weaknesses = result.get('weaknesses')
        evaluation.criteria_scores = json.dumps(result.get('criteria_scores', {}))
        evaluation.is_ai_evaluated = True
        evaluation.evaluated_at = datetime.utcnow()
        evaluation.status = 'completed'
        
        # حفظ التغييرات في قاعدة البيانات
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'تم التقييم بنجاح',
            'result': result,
            'redirect_url': url_for('evaluation.view', id=evaluation.id)
        }), 200
    except Exception as e:
        db.session.rollback()
        logger.error(f"خطأ في تقييم الذكاء الاصطناعي: {str(e)}")
        return jsonify({'success': False, 'message': f'حدث خطأ أثناء التقييم: {str(e)}'}), 500

@bp.route('/<int:id>/verify')
@login_required
def verify(id):
    """التحقق من التقييم باستخدام البلوكتشين"""
    # الحصول على التقييم من قاعدة البيانات
    evaluation = Evaluation.query.get_or_404(id)
    
    # التحقق من صلاحية الوصول (المستخدم هو صاحب التقييم أو مسؤول)
    if evaluation.user_id != current_user.id and not current_user.is_admin:
        flash('ليس لديك صلاحية للتحقق من هذا التقييم.', 'danger')
        return redirect(url_for('evaluation.index'))
    
    # التحقق من أن التقييم مكتمل
    if evaluation.status != 'completed':
        flash('يمكن التحقق فقط من التقييمات المكتملة.', 'warning')
        return redirect(url_for('evaluation.view', id=evaluation.id))
    
    # التحقق من تمكين البلوكتشين في الإعدادات
    from flask import current_app
    if not current_app.config.get('BLOCKCHAIN_ENABLED'):
        flash('التحقق من البلوكتشين غير ممكّن حاليًا.', 'warning')
        return redirect(url_for('evaluation.view', id=evaluation.id))
    
    # عرض صفحة التحقق من البلوكتشين
    return render_template('evaluation/verify.html', evaluation=evaluation)

@bp.route('/<int:id>/process-verification', methods=['POST'])
@login_required
def process_verification(id):
    """معالجة التحقق من البلوكتشين"""
    # الحصول على التقييم من قاعدة البيانات
    evaluation = Evaluation.query.get_or_404(id)
    
    # التحقق من صلاحية الوصول (المستخدم هو صاحب التقييم أو مسؤول)
    if evaluation.user_id != current_user.id and not current_user.is_admin:
        return jsonify({'success': False, 'message': 'ليس لديك صلاحية للتحقق من هذا التقييم.'}), 403
    
    # التحقق من أن التقييم مكتمل
    if evaluation.status != 'completed':
        return jsonify({'success': False, 'message': 'يمكن التحقق فقط من التقييمات المكتملة.'}), 400
    
    # التحقق من تمكين البلوكتشين في الإعدادات
    from flask import current_app
    if not current_app.config.get('BLOCKCHAIN_ENABLED'):
        return jsonify({'success': False, 'message': 'التحقق من البلوكتشين غير ممكّن حاليًا.'}), 403
    
    # إنشاء مدقق البلوكتشين
    blockchain_verifier = BlockchainVerifier()
    
    try:
        # إجراء التحقق باستخدام البلوكتشين
        result = blockchain_verifier.verify_evaluation(evaluation)
        
        # تحديث التقييم بنتائج التحقق
        evaluation.verified = True
        evaluation.verification_hash = result.get('hash')
        evaluation.transaction_id = result.get('transaction_id')
        evaluation.verified_at = datetime.utcnow()
        evaluation.status = 'verified'
        
        # حفظ التغييرات في قاعدة البيانات
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'تم التحقق بنجاح',
            'result': result,
            'redirect_url': url_for('evaluation.view', id=evaluation.id)
        }), 200
    except Exception as e:
        db.session.rollback()
        logger.error(f"خطأ في التحقق من البلوكتشين: {str(e)}")
        return jsonify({'success': False, 'message': f'حدث خطأ أثناء التحقق: {str(e)}'}), 500

@bp.route('/<int:id>/delete', methods=['POST'])
@login_required
def delete(id):
    """حذف التقييم"""
    # الحصول على التقييم من قاعدة البيانات
    evaluation = Evaluation.query.get_or_404(id)
    
    # التحقق من صلاحية الوصول (المستخدم هو صاحب التقييم أو مسؤول)
    if evaluation.user_id != current_user.id and not current_user.is_admin:
        flash('ليس لديك صلاحية لحذف هذا التقييم.', 'danger')
        return redirect(url_for('evaluation.index'))
    
    # التحقق من حالة التقييم (لا يمكن حذف التقييمات المتحقق منها)
    if evaluation.status == 'verified':
        flash('لا يمكن حذف التقييمات المتحقق منها.', 'warning')
        return redirect(url_for('evaluation.view', id=evaluation.id))
    
    try:
        # حذف التقييم من قاعدة البيانات
        db.session.delete(evaluation)
        db.session.commit()
        flash('تم حذف التقييم بنجاح.', 'success')
    except Exception as e:
        db.session.rollback()
        logger.error(f"خطأ في حذف التقييم: {str(e)}")
        flash('حدث خطأ أثناء حذف التقييم. يرجى المحاولة مرة أخرى.', 'danger')
    
    return redirect(url_for('evaluation.index'))

# واجهة برمجة التطبيقات (API) للتقييمات
@bp.route('/api/evaluations', methods=['GET'])
@jwt_required()
def api_get_evaluations():
    """الحصول على قائمة التقييمات"""
    # الحصول على المستخدم الحالي من JWT
    user_uuid = get_jwt_identity()
    user = User.query.filter_by(uuid=user_uuid).first()
    
    if not user:
        return jsonify({'success': False, 'message': 'المستخدم غير موجود.'}), 401
    
    # الحصول على كل التقييمات للمستخدم الحالي أو كل التقييمات للمسؤول
    if user.is_admin:
        evaluations = Evaluation.query.order_by(Evaluation.created_at.desc()).all()
    else:
        evaluations = Evaluation.query.filter_by(user_id=user.id).order_by(Evaluation.created_at.desc()).all()
    
    return jsonify({
        'success': True,
        'evaluations': [evaluation.to_dict() for evaluation in evaluations]
    }), 200

@bp.route('/api/evaluations/<int:id>', methods=['GET'])
@jwt_required()
def api_get_evaluation(id):
    """الحصول على تفاصيل التقييم"""
    # الحصول على المستخدم الحالي من JWT
    user_uuid = get_jwt_identity()
    user = User.query.filter_by(uuid=user_uuid).first()
    
    if not user:
        return jsonify({'success': False, 'message': 'المستخدم غير موجود.'}), 401
    
    # الحصول على التقييم من قاعدة البيانات
    evaluation = Evaluation.query.get_or_404(id)
    
    # التحقق من صلاحية الوصول (المستخدم هو صاحب التقييم أو مسؤول)
    if evaluation.user_id != user.id and not user.is_admin:
        return jsonify({'success': False, 'message': 'ليس لديك صلاحية لعرض هذا التقييم.'}), 403
    
    return jsonify({
        'success': True,
        'evaluation': evaluation.to_dict()
    }), 200

@bp.route('/api/evaluations', methods=['POST'])
@jwt_required()
def api_create_evaluation():
    """إنشاء تقييم جديد"""
    # الحصول على المستخدم الحالي من JWT
    user_uuid = get_jwt_identity()
    user = User.query.filter_by(uuid=user_uuid).first()
    
    if not user:
        return jsonify({'success': False, 'message': 'المستخدم غير موجود.'}), 401
    
    # الحصول على بيانات التقييم من الطلب
    data = request.get_json()
    
    if not data or not data.get('task_description') or not data.get('submission_text'):
        return jsonify({'success': False, 'message': 'وصف المهمة ونص الإجابة مطلوبان.'}), 400
    
    # إنشاء تقييم جديد
    evaluation = Evaluation(
        title=data.get('title') or 'تقييم جديد',
        task_description=data.get('task_description'),
        submission_text=data.get('submission_text'),
        user_id=user.id,
        rubric_id=data.get('rubric_id'),
        created_at=datetime.utcnow(),
        is_ai_evaluated=data.get('use_ai', False)
    )
    
    # حفظ التقييم في قاعدة البيانات
    try:
        evaluation.update_status()
        db.session.add(evaluation)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'تم إنشاء التقييم بنجاح.',
            'evaluation': evaluation.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        logger.error(f"خطأ في إنشاء التقييم: {str(e)}")
        return jsonify({'success': False, 'message': 'حدث خطأ أثناء إنشاء التقييم.'}), 500