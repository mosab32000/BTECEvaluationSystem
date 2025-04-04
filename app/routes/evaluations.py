"""
مسارات التقييمات
"""

from flask import Blueprint, jsonify, request, current_app, send_file
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import User, Evaluation, RubricTemplate
from app.core.security import SecureVault
from app import db
from app.core.ai_evaluator import AIEvaluator  # سنفترض وجود هذا الملف للتعامل مع التقييم
from app.core.blockchain_verifier import BlockchainVerifier  # سنفترض وجود هذا الملف للتحقق من البلوكتشين
import json
import datetime
import io
import csv

evaluations = Blueprint('evaluations', __name__)

@evaluations.route('/', methods=['GET'])
@jwt_required()
def get_evaluations():
    """
    الحصول على قائمة التقييمات للمستخدم الحالي
    """
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user:
        return jsonify(error="مستخدم غير موجود", message="المستخدم غير موجود"), 404
    
    # معلمات البحث والترتيب والصفحات
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', current_app.config['ITEMS_PER_PAGE'], type=int)
    search = request.args.get('q', '')
    status = request.args.get('status', '')
    from_date = request.args.get('from', '')
    to_date = request.args.get('to', '')
    
    # بناء الاستعلام
    query = Evaluation.query.filter_by(user_id=user.id)
    
    # إضافة البحث إذا تم توفيره
    if search:
        # نحتاج إلى فك تشفير المهمة للبحث فيها - هذه عملية معقدة
        # في الواقع، يمكننا تنفيذ البحث على مستوى التطبيق بدلاً من قاعدة البيانات
        pass
    
    # تصفية حسب حالة التحقق
    if status == 'verified':
        query = query.filter_by(verification_status=True)
    elif status == 'unverified':
        query = query.filter_by(verification_status=False)
    
    # تصفية حسب التاريخ
    if from_date:
        try:
            from_date_obj = datetime.datetime.strptime(from_date, '%Y-%m-%d')
            query = query.filter(Evaluation.submitted_at >= from_date_obj)
        except ValueError:
            pass
    
    if to_date:
        try:
            to_date_obj = datetime.datetime.strptime(to_date, '%Y-%m-%d')
            to_date_obj = to_date_obj + datetime.timedelta(days=1)  # لتضمين اليوم المحدد
            query = query.filter(Evaluation.submitted_at <= to_date_obj)
        except ValueError:
            pass
    
    # تنفيذ الاستعلام مع الصفحات
    pagination = query.order_by(Evaluation.submitted_at.desc()).paginate(page=page, per_page=per_page, error_out=False)
    
    # إنشاء الرد
    vault = SecureVault()  # للتعامل مع فك تشفير البيانات
    
    return jsonify(
        data=[evaluation.to_dict(include_task=True, vault=vault) for evaluation in pagination.items],
        pagination={
            'total': pagination.total,
            'pages': pagination.pages,
            'current_page': pagination.page,
            'per_page': pagination.per_page,
            'has_next': pagination.has_next,
            'has_prev': pagination.has_prev
        }
    ), 200

@evaluations.route('/<int:evaluation_id>', methods=['GET'])
@jwt_required()
def get_evaluation(evaluation_id):
    """
    الحصول على تفاصيل تقييم محدد
    """
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user:
        return jsonify(error="مستخدم غير موجود", message="المستخدم غير موجود"), 404
    
    evaluation = Evaluation.query.get(evaluation_id)
    
    if not evaluation:
        return jsonify(error="تقييم غير موجود", message="التقييم المطلوب غير موجود"), 404
    
    # التأكد من أن المستخدم هو صاحب التقييم أو مسؤول
    if evaluation.user_id != current_user_id and not user.is_admin():
        return jsonify(error="صلاحيات غير كافية", message="ليس لديك صلاحية للوصول إلى هذا التقييم"), 403
    
    # فك تشفير المهمة
    vault = SecureVault()
    
    return jsonify(evaluation.to_dict(include_task=True, vault=vault)), 200

@evaluations.route('/evaluate', methods=['POST'])
@jwt_required()
def evaluate_task():
    """
    تقييم مهمة جديدة
    """
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user:
        return jsonify(error="مستخدم غير موجود", message="المستخدم غير موجود"), 404
    
    data = request.get_json()
    
    if not data:
        return jsonify(error="بيانات غير صالحة", message="لم يتم توفير البيانات المطلوبة"), 400
    
    # تحقق من وجود المهمة
    if 'task' not in data or not data['task']:
        return jsonify(error="بيانات ناقصة", message="يرجى توفير محتوى المهمة"), 400
    
    # تشفير المهمة
    vault = SecureVault()
    encrypted_task = vault.encrypt(data['task'])
    
    # تحديد معايير التقييم
    rubric_data = None
    
    if 'rubric_id' in data and data['rubric_id']:
        # استخدام قالب معايير موجود
        rubric_template = RubricTemplate.query.get(data['rubric_id'])
        if rubric_template:
            rubric_data = rubric_template.rubric_data()
    elif 'custom_rubric' in data and data['custom_rubric']:
        # استخدام معايير مخصصة
        try:
            if isinstance(data['custom_rubric'], str):
                rubric_data = json.loads(data['custom_rubric'])
            else:
                rubric_data = data['custom_rubric']
        except json.JSONDecodeError:
            return jsonify(error="معايير غير صالحة", message="تنسيق معايير التقييم المخصصة غير صالح"), 400
    
    # إنشاء مثيل التقييم
    new_evaluation = Evaluation(
        task_encrypted=encrypted_task,
        user_id=current_user_id,
        submitted_at=datetime.datetime.utcnow()
    )
    
    # حفظ التقييم في قاعدة البيانات
    db.session.add(new_evaluation)
    db.session.commit()
    
    try:
        # استدعاء خدمة التقييم بالذكاء الاصطناعي
        evaluator = AIEvaluator()
        evaluation_result = evaluator.evaluate_task(data['task'], rubric_data)
        
        # تحديث التقييم بالنتائج
        new_evaluation.grade = evaluation_result.get('grade')
        new_evaluation.feedback = evaluation_result.get('feedback')
        new_evaluation.grade_numerical = evaluation_result.get('grade_numerical')
        
        if 'rubric_results' in evaluation_result:
            new_evaluation.set_rubric_data(evaluation_result['rubric_results'])
        
        new_evaluation.evaluated_at = datetime.datetime.utcnow()
        
        # حفظ التحديثات
        db.session.commit()
        
        return jsonify(new_evaluation.to_dict(include_task=True, vault=vault)), 200
    
    except Exception as e:
        current_app.logger.error(f"خطأ في عملية التقييم: {str(e)}")
        return jsonify(error="خطأ في التقييم", message=f"حدث خطأ أثناء عملية التقييم: {str(e)}"), 500

@evaluations.route('/<int:evaluation_id>/verify', methods=['POST'])
@jwt_required()
def verify_evaluation(evaluation_id):
    """
    التحقق من صحة تقييم باستخدام البلوكتشين
    """
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user:
        return jsonify(error="مستخدم غير موجود", message="المستخدم غير موجود"), 404
    
    evaluation = Evaluation.query.get(evaluation_id)
    
    if not evaluation:
        return jsonify(error="تقييم غير موجود", message="التقييم المطلوب غير موجود"), 404
    
    # التأكد من أن المستخدم هو صاحب التقييم أو مسؤول
    if evaluation.user_id != current_user_id and not user.is_admin():
        return jsonify(error="صلاحيات غير كافية", message="ليس لديك صلاحية للتحقق من هذا التقييم"), 403
    
    # التحقق من أن التقييم تم تقييمه بالفعل
    if not evaluation.evaluated_at:
        return jsonify(error="تقييم غير مكتمل", message="يجب تقييم المهمة أولاً قبل التحقق منها"), 400
    
    # التحقق من أنه لم يتم التحقق منه بالفعل
    if evaluation.verification_status:
        return jsonify(success=True, message="تم التحقق من هذا التقييم بالفعل", audit_hash=evaluation.audit_hash), 200
    
    try:
        # استدعاء خدمة التحقق بالبلوكتشين
        verifier = BlockchainVerifier()
        verification_result = verifier.verify_evaluation(evaluation)
        
        # تحديث التقييم بنتائج التحقق
        evaluation.audit_hash = verification_result.get('hash')
        evaluation.verification_status = True
        evaluation.verification_timestamp = datetime.datetime.utcnow()
        
        # حفظ التحديثات
        db.session.commit()
        
        return jsonify(
            success=True,
            message="تم التحقق من التقييم بنجاح",
            audit_hash=evaluation.audit_hash
        ), 200
    
    except Exception as e:
        current_app.logger.error(f"خطأ في عملية التحقق: {str(e)}")
        return jsonify(error="خطأ في التحقق", message=f"حدث خطأ أثناء عملية التحقق: {str(e)}"), 500

@evaluations.route('/<int:evaluation_id>/export', methods=['GET'])
@jwt_required()
def export_evaluation(evaluation_id):
    """
    تصدير تقييم محدد
    """
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user:
        return jsonify(error="مستخدم غير موجود", message="المستخدم غير موجود"), 404
    
    evaluation = Evaluation.query.get(evaluation_id)
    
    if not evaluation:
        return jsonify(error="تقييم غير موجود", message="التقييم المطلوب غير موجود"), 404
    
    # التأكد من أن المستخدم هو صاحب التقييم أو مسؤول
    if evaluation.user_id != current_user_id and not user.is_admin():
        return jsonify(error="صلاحيات غير كافية", message="ليس لديك صلاحية لتصدير هذا التقييم"), 403
    
    # تحديد تنسيق التصدير (CSV أو JSON)
    export_format = request.args.get('format', 'csv')
    
    # فك تشفير المهمة
    vault = SecureVault()
    task = vault.decrypt(evaluation.task_encrypted)
    
    if export_format == 'json':
        # تصدير بتنسيق JSON
        export_data = evaluation.to_dict(include_task=True, vault=vault)
        
        return jsonify(export_data), 200
    else:
        # تصدير بتنسيق CSV
        csv_data = io.StringIO()
        csv_writer = csv.writer(csv_data)
        
        # كتابة الرأس
        csv_writer.writerow(['معرف التقييم', 'المهمة', 'التقييم', 'الدرجة', 'ملاحظات',
                             'حالة التحقق', 'رمز التحقق', 'تاريخ التقييم'])
        
        # كتابة البيانات
        csv_writer.writerow([
            evaluation.id,
            task,
            evaluation.grade,
            evaluation.grade_numerical,
            evaluation.feedback,
            'تم التحقق' if evaluation.verification_status else 'لم يتم التحقق',
            evaluation.audit_hash or 'غير متوفر',
            evaluation.evaluated_at.strftime('%Y-%m-%d %H:%M:%S') if evaluation.evaluated_at else 'غير متوفر'
        ])
        
        # إرجاع الملف
        csv_data.seek(0)
        return send_file(
            io.BytesIO(csv_data.getvalue().encode('utf-8')),
            mimetype='text/csv',
            as_attachment=True,
            download_name=f'تقييم-{evaluation.id}.csv'
        )
