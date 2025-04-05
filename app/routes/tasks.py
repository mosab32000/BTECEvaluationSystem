"""
مسارات المهام في نظام تقييم BTEC
توفر هذه الوحدة واجهة RESTful API للتعامل مع المهام
"""

from flask import request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
import logging

from ..extensions import db
from ..models import Task, User
from . import tasks_bp

logger = logging.getLogger(__name__)

# --- المسارات ---

@tasks_bp.route('/', methods=['POST'])
@jwt_required()
def create_task():
    """إنشاء مهمة جديدة (مع تشفير المحتوى والمعايير)"""
    current_user_email = get_jwt_identity()
    # user = User.query.filter_by(email=current_user_email).first() # اختياري: للتحقق من الدور إذا لزم الأمر

    data = request.get_json()
    if not data:
        return jsonify({"error": "No JSON data provided"}), 400
        
    task_content = data.get('task_content')
    criteria = data.get('criteria')
    deadline_str = data.get('deadline')
    # يمكنك إضافة حقول أخرى هنا مثل submitter_email إذا كان المعلم ينشئ لطالب

    if not task_content or not criteria:
        return jsonify({"error": "Task content and criteria are required"}), 400

    deadline = None
    if deadline_str:
        try:
            # تحويل النص إلى كائن datetime
            deadline = datetime.fromisoformat(deadline_str.replace('Z', '+00:00'))
        except ValueError:
            return jsonify({"error": "Invalid deadline format. Use ISO 8601 format."}), 400

    try:
        # إنشاء المهمة
        new_task = Task(
            submitter_email=current_user_email,
            deadline=deadline,
            status='pending'
        )
        # استخدام خصائص التشفير
        new_task.task_content = task_content
        new_task.criteria = criteria
        
        # حفظ المهمة في قاعدة البيانات
        db.session.add(new_task)
        db.session.commit()
        logger.info(f"Task {new_task.id} created by {current_user_email}")

        # إرجاع بيانات المهمة المنشأة (سيتم فك تشفيرها بواسطة getters)
        return jsonify({
            "message": "Task created successfully",
            "task": {
                "id": new_task.id,
                "submitter_email": new_task.submitter_email,
                "task_content": new_task.task_content,  # Getter
                "criteria": new_task.criteria,         # Getter
                "deadline": new_task.deadline.isoformat() if new_task.deadline else None,
                "submitted_at": new_task.submitted_at.isoformat(),
                "status": new_task.status
            }
        }), 201
    except ValueError as ve:  # خطأ من setter التشفير
        logger.error(f"Task creation failed due to configuration/encryption error: {ve}")
        return jsonify({"error": f"Task creation failed: {ve}"}), 500
    except Exception as e:
        db.session.rollback()
        logger.error(f"Task creation failed for user {current_user_email}: {e}", exc_info=True)
        return jsonify({"error": "Task creation failed due to an internal error"}), 500


@tasks_bp.route('/', methods=['GET'])
@jwt_required()
def get_tasks():
    """الحصول على قائمة المهام (مع فك تشفير المحتوى)"""
    current_user_email = get_jwt_identity()
    user = User.query.filter_by(email=current_user_email).first()
    
    if not user:
        return jsonify({"error": "User not found"}), 404

    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)

    # الفلترة حسب الدور
    task_query = Task.query
    if user.role == 'student':
        # الطلاب يرون مهامهم فقط
        task_query = task_query.filter_by(submitter_email=current_user_email)
    
    # الترتيب حسب تاريخ الإنشاء (الأحدث أولاً)
    paginated_tasks = task_query.order_by(Task.submitted_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    tasks = paginated_tasks.items
    
    output = []
    try:
        for task in tasks:
            # استخدام الخصائص لفك التشفير تلقائيًا
            task_data = {
                'id': task.id,
                'submitter_email': task.submitter_email,
                'task_content': task.task_content,  # Getter
                'criteria': task.criteria,         # Getter
                'feedback': task.feedback,         # Getter
                'approved': task.approved,
                'plagiarism_score': task.plagiarism_score,
                'sentiment': task.sentiment,
                'ai_score': task.ai_score,
                'teacher_score': task.teacher_score,
                'status': task.status,
                'deadline': task.deadline.isoformat() if task.deadline else None,
                'submitted_at': task.submitted_at.isoformat(),
                'evaluated_at': task.evaluated_at.isoformat() if task.evaluated_at else None
            }
            output.append(task_data)
        
        return jsonify({
            'tasks': output,
            'page': page,
            'per_page': per_page,
            'total': paginated_tasks.total,
            'pages': paginated_tasks.pages
        })
    except Exception as e:
        logger.error(f"Error retrieving tasks: {e}", exc_info=True)
        return jsonify({"error": "Failed to retrieve tasks"}), 500


@tasks_bp.route('/<int:task_id>', methods=['GET'])
@jwt_required()
def get_task(task_id):
    """الحصول على مهمة محددة بواسطة المعرف"""
    current_user_email = get_jwt_identity()
    user = User.query.filter_by(email=current_user_email).first()
    
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    task = Task.query.get(task_id)
    if not task:
        return jsonify({"error": "Task not found"}), 404
    
    # التحقق من الصلاحيات
    if user.role == 'student' and task.submitter_email != current_user_email:
        return jsonify({"error": "You don't have permission to view this task"}), 403
    
    try:
        # استخدام الخصائص لفك التشفير
        task_data = {
            'id': task.id,
            'submitter_email': task.submitter_email,
            'task_content': task.task_content,  # Getter
            'criteria': task.criteria,         # Getter
            'feedback': task.feedback,         # Getter
            'approved': task.approved,
            'plagiarism_score': task.plagiarism_score,
            'sentiment': task.sentiment,
            'ai_score': task.ai_score,
            'teacher_score': task.teacher_score,
            'status': task.status,
            'deadline': task.deadline.isoformat() if task.deadline else None,
            'submitted_at': task.submitted_at.isoformat(),
            'evaluated_at': task.evaluated_at.isoformat() if task.evaluated_at else None
        }
        
        return jsonify(task_data)
    except Exception as e:
        logger.error(f"Error retrieving task {task_id}: {e}", exc_info=True)
        return jsonify({"error": "Failed to retrieve task details"}), 500


@tasks_bp.route('/<int:task_id>', methods=['PUT'])
@jwt_required()
def update_task(task_id):
    """تحديث مهمة محددة"""
    current_user_email = get_jwt_identity()
    user = User.query.filter_by(email=current_user_email).first()
    
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    task = Task.query.get(task_id)
    if not task:
        return jsonify({"error": "Task not found"}), 404
    
    # التحقق من الصلاحيات
    if user.role == 'student' and task.submitter_email != current_user_email:
        return jsonify({"error": "You don't have permission to update this task"}), 403
    
    # لا تسمح بالتحديث بعد الموافقة عليها
    if task.approved and user.role == 'student':
        return jsonify({"error": "Cannot update an approved task"}), 403
    
    data = request.get_json()
    if not data:
        return jsonify({"error": "No JSON data provided"}), 400
    
    try:
        # تحديث البيانات
        if 'task_content' in data and (user.role != 'student' or not task.approved):
            task.task_content = data['task_content']
        
        if 'criteria' in data and user.role != 'student':
            task.criteria = data['criteria']
        
        if 'feedback' in data and user.role != 'student':
            task.feedback = data['feedback']
        
        # حقول أخرى (غير مشفرة)
        if 'status' in data and user.role != 'student':
            task.status = data['status']
        
        if 'deadline' in data and user.role != 'student':
            deadline_str = data.get('deadline')
            if deadline_str:
                try:
                    # تحويل النص إلى كائن datetime
                    task.deadline = datetime.fromisoformat(deadline_str.replace('Z', '+00:00'))
                except ValueError:
                    return jsonify({"error": "Invalid deadline format. Use ISO 8601 format."}), 400
        
        # حقول التقييم (للمعلمين فقط)
        if user.role != 'student':
            if 'ai_score' in data:
                task.ai_score = data['ai_score']
            
            if 'teacher_score' in data:
                task.teacher_score = data['teacher_score']
                
            if 'approved' in data:
                task.approved = data['approved']
                if data['approved']:
                    task.evaluated_at = datetime.utcnow()
        
        # حفظ التغييرات
        db.session.commit()
        logger.info(f"Task {task_id} updated by {current_user_email}")
        
        return jsonify({
            "message": "Task updated successfully",
            "task": {
                "id": task.id,
                "submitter_email": task.submitter_email,
                "task_content": task.task_content,  # Getter
                "criteria": task.criteria,         # Getter
                "feedback": task.feedback,         # Getter
                "status": task.status,
                "approved": task.approved
            }
        })
    except ValueError as ve:  # خطأ من setter التشفير
        logger.error(f"Task update failed due to configuration/encryption error: {ve}")
        return jsonify({"error": f"Task update failed: {ve}"}), 500
    except Exception as e:
        db.session.rollback()
        logger.error(f"Task update failed: {e}", exc_info=True)
        return jsonify({"error": "Task update failed due to an internal error"}), 500


@tasks_bp.route('/<int:task_id>', methods=['DELETE'])
@jwt_required()
def delete_task(task_id):
    """حذف مهمة محددة"""
    current_user_email = get_jwt_identity()
    user = User.query.filter_by(email=current_user_email).first()
    
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    task = Task.query.get(task_id)
    if not task:
        return jsonify({"error": "Task not found"}), 404
    
    # التحقق من الصلاحيات: فقط الأساتذة والمسؤولون يمكنهم حذف المهام، أو الطالب يمكنه حذف مهامه الخاصة فقط
    if user.role == 'student' and task.submitter_email != current_user_email:
        return jsonify({"error": "You don't have permission to delete this task"}), 403
    
    # لا تسمح بالحذف بعد الموافقة عليها (إلا للمسؤولين)
    if task.approved and user.role not in ['admin', 'teacher']:
        return jsonify({"error": "Cannot delete an approved task"}), 403
    
    try:
        db.session.delete(task)
        db.session.commit()
        logger.info(f"Task {task_id} deleted by {current_user_email}")
        
        return jsonify({"message": "Task deleted successfully"})
    except Exception as e:
        db.session.rollback()
        logger.error(f"Task deletion failed: {e}", exc_info=True)
        return jsonify({"error": "Task deletion failed due to an internal error"}), 500


@tasks_bp.route('/<int:task_id>/evaluate', methods=['POST'])
@jwt_required()
def evaluate_task(task_id):
    """تقييم مهمة محددة باستخدام الذكاء الاصطناعي"""
    current_user_email = get_jwt_identity()
    user = User.query.filter_by(email=current_user_email).first()
    
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    # فقط المعلمون والمسؤولون يمكنهم تقييم المهام
    if user.role not in ['teacher', 'admin']:
        return jsonify({"error": "Only teachers and admins can evaluate tasks"}), 403
    
    task = Task.query.get(task_id)
    if not task:
        return jsonify({"error": "Task not found"}), 404
    
    # التحقق من حالة المهمة
    if task.status not in ['pending', 'submitted']:
        return jsonify({"error": f"Task cannot be evaluated in {task.status} status"}), 400
    
    # الحصول على بيانات التقييم من الطلب
    data = request.get_json()
    if not data:
        return jsonify({"error": "No JSON data provided"}), 400
    
    try:
        # عملية التقييم - في الإنتاج هذا قد يستدعي خدمة AI
        # قم بتعديل هذا الجزء لاستدعاء خدمة الذكاء الاصطناعي الخاصة بك
        
        # نسخة مبسطة للعرض التوضيحي
        ai_score = data.get('ai_score', 0)
        teacher_score = data.get('teacher_score', 0)
        feedback = data.get('feedback')
        
        # تحديث المهمة
        task.ai_score = ai_score
        task.teacher_score = teacher_score
        task.feedback = feedback  # سيتم تشفيره تلقائيًا
        task.status = 'evaluated'
        task.evaluated_at = datetime.utcnow()
        
        # حفظ التغييرات
        db.session.commit()
        logger.info(f"Task {task_id} evaluated by {current_user_email}")
        
        return jsonify({
            "message": "Task evaluated successfully",
            "task": {
                "id": task.id,
                "ai_score": task.ai_score,
                "teacher_score": task.teacher_score,
                "feedback": task.feedback,  # Getter
                "status": task.status,
                "evaluated_at": task.evaluated_at.isoformat()
            }
        })
    except Exception as e:
        db.session.rollback()
        logger.error(f"Task evaluation failed: {e}", exc_info=True)
        return jsonify({"error": "Task evaluation failed due to an internal error"}), 500