"""
مسارات واجهة برمجة التطبيقات (API) في نظام تقييم BTEC
"""

import os
import json
import logging
from datetime import datetime

from flask import Blueprint, jsonify, request, current_app, send_file
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename

from app.extensions import db, cache

api_bp = Blueprint('api', __name__, url_prefix='/api')

#
# نقاط نهاية المستخدمين
#

@api_bp.route('/users', methods=['GET'])
@jwt_required()
def get_users():
    """الحصول على قائمة المستخدمين - للمسؤولين فقط"""
    from app.models.user import User
    
    # التحقق من أن المستخدم الحالي هو مسؤول
    current_user_id = get_jwt_identity()
    current_user = User.query.get(current_user_id)
    
    if not current_user or not current_user.is_admin:
        return jsonify({'error': 'غير مصرح لك بالوصول إلى هذا المورد'}), 403
    
    # استرجاع جميع المستخدمين
    users = User.query.all()
    
    return jsonify({
        'users': [user.to_dict() for user in users]
    }), 200

@api_bp.route('/users/<int:user_id>', methods=['GET'])
@jwt_required()
def get_user(user_id):
    """الحصول على مستخدم معين"""
    from app.models.user import User
    
    # التحقق من أن المستخدم الحالي هو مسؤول أو المستخدم نفسه
    current_user_id = get_jwt_identity()
    current_user = User.query.get(current_user_id)
    
    if not current_user or (not current_user.is_admin and current_user.id != user_id):
        return jsonify({'error': 'غير مصرح لك بالوصول إلى هذا المورد'}), 403
    
    # استرجاع المستخدم
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({'error': 'لم يتم العثور على المستخدم'}), 404
    
    return jsonify({
        'user': user.to_dict()
    }), 200

@api_bp.route('/users/<int:user_id>', methods=['PUT'])
@jwt_required()
def update_user(user_id):
    """تحديث مستخدم معين"""
    from app.models.user import User
    
    # التحقق من أن المستخدم الحالي هو مسؤول أو المستخدم نفسه
    current_user_id = get_jwt_identity()
    current_user = User.query.get(current_user_id)
    
    if not current_user or (not current_user.is_admin and current_user.id != user_id):
        return jsonify({'error': 'غير مصرح لك بالوصول إلى هذا المورد'}), 403
    
    # استرجاع المستخدم
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({'error': 'لم يتم العثور على المستخدم'}), 404
    
    # تحديث بيانات المستخدم
    data = request.json
    
    if 'name' in data:
        user.name = data['name']
    
    # فقط المسؤولون يمكنهم تغيير الدور أو حالة التنشيط
    if current_user.is_admin:
        if 'role' in data:
            user.role = data['role']
        
        if 'is_active' in data:
            user.is_active = data['is_active']
    
    db.session.commit()
    
    return jsonify({
        'user': user.to_dict(),
        'message': 'تم تحديث المستخدم بنجاح'
    }), 200

#
# نقاط نهاية معايير التقييم
#

@api_bp.route('/rubrics', methods=['GET'])
@jwt_required()
def get_rubrics():
    """الحصول على قائمة معايير التقييم"""
    from app.models.rubric import Rubric
    
    # استرجاع جميع معايير التقييم النشطة
    rubrics = Rubric.query.filter_by(is_active=True).all()
    
    return jsonify({
        'rubrics': [rubric.to_dict() for rubric in rubrics]
    }), 200

@api_bp.route('/rubrics/<int:rubric_id>', methods=['GET'])
@jwt_required()
def get_rubric(rubric_id):
    """الحصول على معيار تقييم معين"""
    from app.models.rubric import Rubric
    
    # استرجاع معيار التقييم
    rubric = Rubric.query.get(rubric_id)
    
    if not rubric or not rubric.is_active:
        return jsonify({'error': 'لم يتم العثور على معيار التقييم'}), 404
    
    return jsonify({
        'rubric': rubric.to_dict()
    }), 200

@api_bp.route('/rubrics', methods=['POST'])
@jwt_required()
def create_rubric():
    """إنشاء معيار تقييم جديد"""
    from app.models.user import User
    from app.models.rubric import Rubric
    
    # التحقق من أن المستخدم الحالي هو مسؤول أو معلم
    current_user_id = get_jwt_identity()
    current_user = User.query.get(current_user_id)
    
    if not current_user or (not current_user.is_admin and not current_user.is_teacher):
        return jsonify({'error': 'غير مصرح لك بإنشاء معايير تقييم'}), 403
    
    # إنشاء معيار تقييم جديد
    data = request.json
    
    if not data or 'name' not in data:
        return jsonify({'error': 'البيانات غير كاملة. يرجى توفير اسم على الأقل.'}), 400
    
    new_rubric = Rubric(
        name=data['name'],
        description=data.get('description', ''),
        criteria=data.get('criteria', {}),
        max_score=data.get('max_score', 100),
        created_by=current_user.id
    )
    
    db.session.add(new_rubric)
    db.session.commit()
    
    return jsonify({
        'rubric': new_rubric.to_dict(),
        'message': 'تم إنشاء معيار التقييم بنجاح'
    }), 201

@api_bp.route('/rubrics/<int:rubric_id>', methods=['PUT'])
@jwt_required()
def update_rubric(rubric_id):
    """تحديث معيار تقييم معين"""
    from app.models.user import User
    from app.models.rubric import Rubric
    
    # التحقق من أن المستخدم الحالي هو مسؤول أو منشئ المعيار
    current_user_id = get_jwt_identity()
    current_user = User.query.get(current_user_id)
    
    # استرجاع معيار التقييم
    rubric = Rubric.query.get(rubric_id)
    
    if not rubric or not rubric.is_active:
        return jsonify({'error': 'لم يتم العثور على معيار التقييم'}), 404
    
    if not current_user or (not current_user.is_admin and rubric.created_by != current_user.id):
        return jsonify({'error': 'غير مصرح لك بتحديث هذا المعيار'}), 403
    
    # تحديث بيانات معيار التقييم
    data = request.json
    
    if 'name' in data:
        rubric.name = data['name']
    
    if 'description' in data:
        rubric.description = data['description']
    
    if 'criteria' in data:
        rubric.criteria = data['criteria']
    
    if 'max_score' in data:
        rubric.max_score = data['max_score']
    
    db.session.commit()
    
    return jsonify({
        'rubric': rubric.to_dict(),
        'message': 'تم تحديث معيار التقييم بنجاح'
    }), 200

@api_bp.route('/rubrics/<int:rubric_id>', methods=['DELETE'])
@jwt_required()
def delete_rubric(rubric_id):
    """حذف معيار تقييم (تعطيله)"""
    from app.models.user import User
    from app.models.rubric import Rubric
    
    # التحقق من أن المستخدم الحالي هو مسؤول أو منشئ المعيار
    current_user_id = get_jwt_identity()
    current_user = User.query.get(current_user_id)
    
    # استرجاع معيار التقييم
    rubric = Rubric.query.get(rubric_id)
    
    if not rubric:
        return jsonify({'error': 'لم يتم العثور على معيار التقييم'}), 404
    
    if not current_user or (not current_user.is_admin and rubric.created_by != current_user.id):
        return jsonify({'error': 'غير مصرح لك بحذف هذا المعيار'}), 403
    
    # بدلاً من الحذف الفعلي، نقوم بتعطيل المعيار
    rubric.is_active = False
    db.session.commit()
    
    return jsonify({
        'message': 'تم حذف معيار التقييم بنجاح'
    }), 200

#
# نقاط نهاية التقييمات
#

@api_bp.route('/evaluations', methods=['GET'])
@jwt_required()
def get_evaluations():
    """الحصول على قائمة التقييمات"""
    from app.models.user import User
    from app.models.evaluation import Evaluation
    
    # التحقق من المستخدم الحالي
    current_user_id = get_jwt_identity()
    current_user = User.query.get(current_user_id)
    
    if not current_user:
        return jsonify({'error': 'لم يتم العثور على المستخدم'}), 404
    
    # استرجاع التقييمات بناءً على دور المستخدم
    if current_user.is_admin:
        # المسؤولون يرون جميع التقييمات
        evaluations = Evaluation.query.all()
    elif current_user.is_teacher:
        # المعلمون يرون التقييمات التي قاموا بتقييمها
        evaluations = Evaluation.query.filter_by(evaluator_id=current_user.id).all()
    else:
        # الطلاب يرون تقييماتهم فقط
        evaluations = Evaluation.query.filter_by(student_id=current_user.id).all()
    
    return jsonify({
        'evaluations': [evaluation.to_dict() for evaluation in evaluations]
    }), 200

@api_bp.route('/evaluations/<int:evaluation_id>', methods=['GET'])
@jwt_required()
def get_evaluation(evaluation_id):
    """الحصول على تقييم معين"""
    from app.models.user import User
    from app.models.evaluation import Evaluation
    
    # التحقق من المستخدم الحالي
    current_user_id = get_jwt_identity()
    current_user = User.query.get(current_user_id)
    
    if not current_user:
        return jsonify({'error': 'لم يتم العثور على المستخدم'}), 404
    
    # استرجاع التقييم
    evaluation = Evaluation.query.get(evaluation_id)
    
    if not evaluation:
        return jsonify({'error': 'لم يتم العثور على التقييم'}), 404
    
    # التحقق من الصلاحيات
    if not current_user.is_admin and current_user.id != evaluation.student_id and current_user.id != evaluation.evaluator_id:
        return jsonify({'error': 'غير مصرح لك بالوصول إلى هذا التقييم'}), 403
    
    return jsonify({
        'evaluation': evaluation.to_dict()
    }), 200

@api_bp.route('/evaluations', methods=['POST'])
@jwt_required()
def create_evaluation():
    """إنشاء تقييم جديد"""
    from app.models.user import User
    from app.models.rubric import Rubric
    from app.models.evaluation import Evaluation
    
    # التحقق من المستخدم الحالي
    current_user_id = get_jwt_identity()
    current_user = User.query.get(current_user_id)
    
    if not current_user:
        return jsonify({'error': 'لم يتم العثور على المستخدم'}), 404
    
    # التحقق من البيانات
    data = request.json
    
    if not data or 'rubric_id' not in data or 'submission_text' not in data:
        return jsonify({'error': 'البيانات غير كاملة. يرجى توفير معرف معيار التقييم ونص المهمة.'}), 400
    
    # التحقق من وجود معيار التقييم
    rubric = Rubric.query.get(data['rubric_id'])
    
    if not rubric or not rubric.is_active:
        return jsonify({'error': 'لم يتم العثور على معيار التقييم'}), 404
    
    # إنشاء تقييم جديد
    new_evaluation = Evaluation(
        student_id=current_user.id,
        assignment_id=data.get('assignment_id', ''),
        rubric_id=data['rubric_id'],
        submission_text=data['submission_text'],
        status='pending'
    )
    
    # إذا كان هناك نتائج تقييم، قم بإضافتها
    if 'evaluation_result' in data:
        new_evaluation.evaluation_result = data['evaluation_result']
        
        # حساب الدرجة
        new_evaluation.score = new_evaluation.calculate_score()
        
        # إذا كان التقييم مكتملاً
        if data.get('status') == 'completed':
            new_evaluation.status = 'completed'
    
    db.session.add(new_evaluation)
    db.session.commit()
    
    return jsonify({
        'evaluation_id': new_evaluation.id,
        'message': 'تم إنشاء التقييم بنجاح'
    }), 201

@api_bp.route('/evaluations/<int:evaluation_id>', methods=['PUT'])
@jwt_required()
def update_evaluation(evaluation_id):
    """تحديث تقييم معين"""
    from app.models.user import User
    from app.models.evaluation import Evaluation
    
    # التحقق من المستخدم الحالي
    current_user_id = get_jwt_identity()
    current_user = User.query.get(current_user_id)
    
    if not current_user:
        return jsonify({'error': 'لم يتم العثور على المستخدم'}), 404
    
    # استرجاع التقييم
    evaluation = Evaluation.query.get(evaluation_id)
    
    if not evaluation:
        return jsonify({'error': 'لم يتم العثور على التقييم'}), 404
    
    # التحقق من الصلاحيات
    is_evaluator = current_user.is_admin or current_user.is_teacher
    is_owner = current_user.id == evaluation.student_id
    
    if not is_evaluator and not is_owner:
        return jsonify({'error': 'غير مصرح لك بتحديث هذا التقييم'}), 403
    
    # تحديث بيانات التقييم
    data = request.json
    
    # الطلاب يمكنهم تحديث نص المهمة فقط، والمقيمون يمكنهم تحديث نتائج التقييم
    if is_owner and 'submission_text' in data and evaluation.status == 'pending':
        evaluation.submission_text = data['submission_text']
    
    if is_evaluator:
        if 'evaluation_result' in data:
            evaluation.evaluation_result = data['evaluation_result']
            
            # حساب الدرجة
            evaluation.score = evaluation.calculate_score()
        
        if 'ai_score' in data:
            evaluation.ai_score = data['ai_score']
        
        if 'evaluator_comments' in data:
            evaluation.evaluator_comments = data['evaluator_comments']
        
        if 'status' in data:
            evaluation.status = data['status']
        
        # تعيين المقيم إذا لم يكن معينًا بالفعل
        if not evaluation.evaluator_id:
            evaluation.evaluator_id = current_user.id
    
    db.session.commit()
    
    return jsonify({
        'evaluation': evaluation.to_dict(),
        'message': 'تم تحديث التقييم بنجاح'
    }), 200

#
# نقاط نهاية الفصول الدراسية
#

@api_bp.route('/classrooms', methods=['GET'])
@jwt_required()
def get_classrooms():
    """الحصول على قائمة الفصول الدراسية"""
    from app.models.user import User
    from app.models.classroom import Classroom
    from app.models.participant import ClassroomParticipant
    
    # التحقق من المستخدم الحالي
    current_user_id = get_jwt_identity()
    current_user = User.query.get(current_user_id)
    
    if not current_user:
        return jsonify({'error': 'لم يتم العثور على المستخدم'}), 404
    
    # استرجاع الفصول الدراسية بناءً على دور المستخدم
    if current_user.is_admin:
        # المسؤولون يرون جميع الفصول الدراسية
        classrooms = Classroom.query.filter_by(is_active=True).all()
    elif current_user.is_teacher:
        # المعلمون يرون الفصول الدراسية التي أنشأوها
        classrooms = Classroom.query.filter_by(teacher_id=current_user.id, is_active=True).all()
    else:
        # الطلاب يرون الفصول الدراسية التي هم مشاركون فيها
        participations = ClassroomParticipant.query.filter_by(user_id=current_user.id, is_active=True).all()
        classroom_ids = [p.classroom_id for p in participations]
        classrooms = Classroom.query.filter(Classroom.id.in_(classroom_ids), Classroom.is_active == True).all()
    
    return jsonify({
        'classrooms': [classroom.to_dict() for classroom in classrooms]
    }), 200

@api_bp.route('/classrooms/<int:classroom_id>', methods=['GET'])
@jwt_required()
def get_classroom(classroom_id):
    """الحصول على فصل دراسي معين"""
    from app.models.user import User
    from app.models.classroom import Classroom
    from app.models.participant import ClassroomParticipant
    
    # التحقق من المستخدم الحالي
    current_user_id = get_jwt_identity()
    current_user = User.query.get(current_user_id)
    
    if not current_user:
        return jsonify({'error': 'لم يتم العثور على المستخدم'}), 404
    
    # استرجاع الفصل الدراسي
    classroom = Classroom.query.get(classroom_id)
    
    if not classroom or not classroom.is_active:
        return jsonify({'error': 'لم يتم العثور على الفصل الدراسي'}), 404
    
    # التحقق من الصلاحيات
    is_teacher = current_user.is_admin or current_user.id == classroom.teacher_id
    is_participant = ClassroomParticipant.query.filter_by(
        classroom_id=classroom.id, user_id=current_user.id, is_active=True
    ).first() is not None
    
    if not is_teacher and not is_participant:
        return jsonify({'error': 'غير مصرح لك بالوصول إلى هذا الفصل الدراسي'}), 403
    
    return jsonify({
        'classroom': classroom.to_dict()
    }), 200

#
# نقاط نهاية أخرى
#

@api_bp.route('/health', methods=['GET'])
def health_check():
    """فحص صحة API"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'version': current_app.config.get('VERSION', '1.0.0')
    }), 200