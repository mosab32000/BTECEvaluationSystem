"""
واجهات API في نظام تقييم BTEC
"""

import logging
import json
from flask import request, jsonify, abort, session

from app.routes import api_bp
from app.models.user import User
from app.models.evaluation import Evaluation
from app.models.rubric import Rubric

logger = logging.getLogger(__name__)

@api_bp.route('/health')
def health():
    """
    نقطة نهاية للتحقق من صحة واجهة API
    """
    from datetime import datetime
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "api_version": "1.0.0"
    })

@api_bp.route('/login', methods=['POST'])
def login():
    """
    واجهة API لتسجيل الدخول
    """
    data = request.get_json()
    if not data:
        return jsonify({'error': 'البيانات المطلوبة غير موجودة'}), 400
    
    email = data.get('email')
    password = data.get('password')
    
    if not email or not password:
        return jsonify({'error': 'البريد الإلكتروني وكلمة المرور مطلوبين'}), 400
    
    user = User.get_by_email(email)
    if not user or not user.check_password(password):
        return jsonify({'error': 'البريد الإلكتروني أو كلمة المرور غير صحيحة'}), 401
    
    if not user.is_active:
        return jsonify({'error': 'حسابك غير نشط'}), 403
    
    # إنشاء رمز جلسة أو JWT هنا إذا لزم الأمر
    
    return jsonify({
        'success': True,
        'message': 'تم تسجيل الدخول بنجاح',
        'user': user.to_dict(exclude=['password_hash'])
    })

@api_bp.route('/register', methods=['POST'])
def register():
    """
    واجهة API لتسجيل حساب جديد
    """
    data = request.get_json()
    if not data:
        return jsonify({'error': 'البيانات المطلوبة غير موجودة'}), 400
    
    email = data.get('email')
    password = data.get('password')
    name = data.get('name')
    
    if not email or not password or not name:
        return jsonify({'error': 'جميع الحقول مطلوبة'}), 400
    
    # التحقق مما إذا كان البريد الإلكتروني مستخدمًا بالفعل
    existing_user = User.get_by_email(email)
    if existing_user:
        return jsonify({'error': 'البريد الإلكتروني مستخدم بالفعل'}), 400
    
    # إنشاء مستخدم جديد
    user = User(email=email, name=name, role='student')
    user.set_password(password)
    if user.save():
        return jsonify({
            'success': True,
            'message': 'تم التسجيل بنجاح',
            'user': user.to_dict(exclude=['password_hash'])
        })
    else:
        return jsonify({'error': 'حدث خطأ أثناء التسجيل'}), 500

@api_bp.route('/users', methods=['GET'])
def get_users():
    """
    واجهة API للحصول على قائمة المستخدمين
    """
    # التحقق من تسجيل الدخول ودور المستخدم
    if 'user_id' not in session or session.get('user_role') != 'admin':
        return jsonify({'error': 'ليس لديك صلاحية الوصول إلى هذه البيانات'}), 403
    
    users = User.get_all()
    return jsonify({
        'success': True,
        'users': [user.to_dict(exclude=['password_hash']) for user in users]
    })

@api_bp.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    """
    واجهة API للحصول على بيانات مستخدم معين
    """
    # التحقق من تسجيل الدخول
    if 'user_id' not in session:
        return jsonify({'error': 'يجب تسجيل الدخول للوصول إلى هذه البيانات'}), 401
    
    # التحقق من صلاحية الوصول (المستخدم نفسه أو المسؤول)
    if session['user_id'] != user_id and session.get('user_role') != 'admin':
        return jsonify({'error': 'ليس لديك صلاحية الوصول إلى هذه البيانات'}), 403
    
    user = User.get_by_id(user_id)
    if not user:
        return jsonify({'error': 'المستخدم غير موجود'}), 404
    
    return jsonify({
        'success': True,
        'user': user.to_dict(exclude=['password_hash'])
    })

@api_bp.route('/rubrics', methods=['GET'])
def get_rubrics():
    """
    واجهة API للحصول على قائمة معايير التقييم
    """
    # التحقق من تسجيل الدخول
    if 'user_id' not in session:
        return jsonify({'error': 'يجب تسجيل الدخول للوصول إلى هذه البيانات'}), 401
    
    rubrics = Rubric.get_all()
    return jsonify({
        'success': True,
        'rubrics': [rubric.to_dict() for rubric in rubrics]
    })

@api_bp.route('/rubrics/<int:rubric_id>', methods=['GET'])
def get_rubric(rubric_id):
    """
    واجهة API للحصول على معيار تقييم معين
    """
    # التحقق من تسجيل الدخول
    if 'user_id' not in session:
        return jsonify({'error': 'يجب تسجيل الدخول للوصول إلى هذه البيانات'}), 401
    
    rubric = Rubric.get_by_id(rubric_id)
    if not rubric:
        return jsonify({'error': 'معيار التقييم غير موجود'}), 404
    
    return jsonify({
        'success': True,
        'rubric': rubric.to_dict()
    })

@api_bp.route('/evaluations', methods=['GET'])
def get_evaluations():
    """
    واجهة API للحصول على قائمة التقييمات
    """
    # التحقق من تسجيل الدخول
    if 'user_id' not in session:
        return jsonify({'error': 'يجب تسجيل الدخول للوصول إلى هذه البيانات'}), 401
    
    # الحصول على التقييمات حسب دور المستخدم
    user = User.get_by_id(session['user_id'])
    if not user:
        return jsonify({'error': 'حدث خطأ في جلستك'}), 401
    
    if user.role == 'admin':
        # المسؤول يرى جميع التقييمات
        evaluations = Evaluation.get_all()
    elif user.role == 'teacher':
        # المدرس يرى التقييمات التي قام بتقييمها وغير المقيمة
        evaluations = Evaluation.get_by_evaluator(user.id) + Evaluation.get_pending()
    else:
        # الطالب يرى التقييمات الخاصة به فقط
        evaluations = Evaluation.get_by_student(user.id)
    
    return jsonify({
        'success': True,
        'evaluations': [evaluation.to_dict() for evaluation in evaluations]
    })

@api_bp.route('/evaluations/<int:evaluation_id>', methods=['GET'])
def get_evaluation(evaluation_id):
    """
    واجهة API للحصول على تقييم معين
    """
    # التحقق من تسجيل الدخول
    if 'user_id' not in session:
        return jsonify({'error': 'يجب تسجيل الدخول للوصول إلى هذه البيانات'}), 401
    
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
    
    return jsonify({
        'success': True,
        'evaluation': evaluation.to_dict(),
        'student': User.get_by_id(evaluation.student_id).to_dict() if evaluation.student_id else None,
        'rubric': Rubric.get_by_id(evaluation.rubric_id).to_dict() if evaluation.rubric_id else None,
        'evaluator': User.get_by_id(evaluation.evaluator_id).to_dict() if evaluation.evaluator_id else None
    })

@api_bp.route('/evaluations', methods=['POST'])
def create_evaluation():
    """
    واجهة API لإنشاء تقييم جديد
    """
    # التحقق من تسجيل الدخول
    if 'user_id' not in session:
        return jsonify({'error': 'يجب تسجيل الدخول للوصول إلى هذه الوظيفة'}), 401
    
    data = request.get_json()
    if not data:
        return jsonify({'error': 'البيانات المطلوبة غير موجودة'}), 400
    
    # الحصول على البيانات من الطلب
    student_id = session['user_id']  # الطالب هو المستخدم الحالي
    assignment_id = data.get('assignment_id')
    rubric_id = data.get('rubric_id')
    submission_text = data.get('submission_text')
    
    # التحقق من صحة البيانات
    if not assignment_id or not rubric_id or not submission_text:
        return jsonify({'error': 'جميع الحقول مطلوبة'}), 400
    
    # التحقق من وجود معيار التقييم
    rubric = Rubric.get_by_id(rubric_id)
    if not rubric:
        return jsonify({'error': 'معيار التقييم غير موجود'}), 400
    
    # إنشاء تقييم جديد
    evaluation = Evaluation(
        student_id=student_id,
        assignment_id=assignment_id,
        rubric_id=rubric_id,
        submission_text=submission_text,
        status='pending'
    )
    
    if evaluation.save():
        return jsonify({
            'success': True,
            'message': 'تم إنشاء التقييم بنجاح',
            'evaluation': evaluation.to_dict()
        })
    else:
        return jsonify({'error': 'حدث خطأ أثناء إنشاء التقييم'}), 500

@api_bp.route('/evaluations/<int:evaluation_id>/evaluate', methods=['POST'])
def evaluate_submission(evaluation_id):
    """
    واجهة API لتقييم مهمة
    """
    # التحقق من تسجيل الدخول ودور المستخدم
    if 'user_id' not in session:
        return jsonify({'error': 'يجب تسجيل الدخول للوصول إلى هذه الوظيفة'}), 401
    
    user = User.get_by_id(session['user_id'])
    if not user or user.role not in ['admin', 'teacher']:
        return jsonify({'error': 'ليس لديك صلاحية الوصول إلى هذه الوظيفة'}), 403
    
    # الحصول على التقييم
    evaluation = Evaluation.get_by_id(evaluation_id)
    if not evaluation:
        return jsonify({'error': 'التقييم غير موجود'}), 404
    
    # التحقق من حالة التقييم
    if evaluation.status != 'pending':
        return jsonify({'error': 'لا يمكن تقييم مهمة تم تقييمها مسبقًا'}), 400
    
    data = request.get_json()
    if not data:
        return jsonify({'error': 'البيانات المطلوبة غير موجودة'}), 400
    
    # الحصول على البيانات من الطلب
    score = data.get('score')
    evaluator_comments = data.get('evaluator_comments')
    evaluation_result = data.get('evaluation_result')
    
    # التحقق من صحة البيانات
    if not score or not evaluator_comments:
        return jsonify({'error': 'الدرجة والتعليقات مطلوبة'}), 400
    
    # تحديث التقييم
    evaluation.evaluator_id = user.id
    evaluation.score = float(score)
    evaluation.evaluator_comments = evaluator_comments
    if evaluation_result:
        evaluation.evaluation_result = evaluation_result
    evaluation.status = 'completed'
    
    if evaluation.save():
        return jsonify({
            'success': True,
            'message': 'تم تقييم المهمة بنجاح',
            'evaluation': evaluation.to_dict()
        })
    else:
        return jsonify({'error': 'حدث خطأ أثناء تقييم المهمة'}), 500