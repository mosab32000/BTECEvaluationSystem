
"""
مسارات API للمهام والتحليل في نظام BTEC
"""
from flask import Blueprint, request, jsonify, current_app, url_for
import os
import uuid
from werkzeug.utils import secure_filename
from backend.app.database import db
from app.models.task import Task

# تعريف البلوبرنت
tasks_bp = Blueprint('tasks', __name__, url_prefix='/api/tasks')

# المسارات الجذرية
@tasks_bp.route('/', methods=['GET'])
def get_tasks():
    """الحصول على قائمة المهام"""
    tasks = Task.query.order_by(Task.created_at.desc()).all()
    result = []
    
    for task in tasks:
        task_data = {
            'id': task.id,
            'title': task.title,
            'description': task.description,
            'filename': task.filename,
            'created_at': task.created_at.isoformat(),
            'analysis_result': task.analysis_result,
            'evaluation_result': task.evaluation_result
        }
        
        if task.uploaded_file:
            file_url = url_for('static', filename=f'uploads/{task.filename}', _external=True)
            task_data['uploaded_file_url'] = file_url
        
        result.append(task_data)
    
    return jsonify(result)

@tasks_bp.route('/', methods=['POST'])
def create_task():
    """إنشاء مهمة جديدة"""
    if 'uploaded_file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['uploaded_file']
    if file.filename == '':
        return jsonify({'error': 'Empty filename'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'error': 'File type not allowed'}), 400
    
    # تأمين اسم الملف وإضافة معرّف فريد
    filename = secure_filename(file.filename)
    unique_filename = f"{uuid.uuid4().hex}_{filename}"
    
    # إنشاء مجلد التحميل إذا لم يكن موجودًا
    upload_folder = os.path.join(current_app.static_folder, 'uploads')
    os.makedirs(upload_folder, exist_ok=True)
    
    # حفظ الملف
    file_path = os.path.join(upload_folder, unique_filename)
    file.save(file_path)
    
    # إنشاء سجل المهمة
    task = Task(
        title=request.form.get('title', 'Untitled Task'),
        description=request.form.get('description'),
        uploaded_file=f'uploads/{unique_filename}'
    )
    
    db.session.add(task)
    db.session.commit()
    
    # إعداد الاستجابة
    response = {
        'id': task.id,
        'title': task.title,
        'description': task.description,
        'uploaded_file_url': url_for('static', filename=f'uploads/{unique_filename}', _external=True),
        'filename': filename,
        'created_at': task.created_at.isoformat(),
        'analysis_result': None,
        'evaluation_result': None
    }
    
    return jsonify(response), 201

@tasks_bp.route('/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    """حذف مهمة"""
    task = Task.query.get_or_404(task_id)
    
    # حذف الملف المرفق إذا كان موجودًا
    if task.uploaded_file:
        file_path = os.path.join(current_app.static_folder, task.uploaded_file)
        if os.path.exists(file_path):
            os.remove(file_path)
    
    db.session.delete(task)
    db.session.commit()
    
    return jsonify({'message': f'Task {task_id} deleted successfully'}), 200

@tasks_bp.route('/<int:task_id>/analyze', methods=['POST'])
def analyze_task(task_id):
    """تحليل نص المهمة"""
    task = Task.query.get_or_404(task_id)
    
    # في هذا المثال، نحلل بشكل بسيط
    # يمكن تنفيذ تحليل أكثر تعقيدًا بالاعتماد على مكتبات NLP
    
    # مثال لنتيجة تحليل (يمكن توسيعها)
    analysis_result = {
        'word_count': 150,  # هنا سيكون العدد الفعلي للكلمات
        'sentence_count': 12,  # عدد الجمل
        'entities': [
            {'text': 'BTEC', 'label': 'ORG', 'start': 10, 'end': 14}
        ],
        'potential_spelling_errors': []
    }
    
    # تحديث سجل المهمة بنتائج التحليل
    task.analysis_result = analysis_result
    db.session.commit()
    
    return jsonify(analysis_result)

@tasks_bp.route('/<int:task_id>/evaluate', methods=['POST'])
def evaluate_task(task_id):
    """تقييم جودة المهمة"""
    task = Task.query.get_or_404(task_id)
    
    # مثال لنتيجة تقييم بسيطة (يمكن توسيعها باستخدام نماذج ML)
    evaluation_result = {
        'score': 0.85,  # درجة التقييم (0-1)
        'label': 'Good'  # تصنيف الجودة
    }
    
    # تحديث سجل المهمة بنتائج التقييم
    task.evaluation_result = evaluation_result
    db.session.commit()
    
    return jsonify(evaluation_result)

# وظائف مساعدة
def allowed_file(filename):
    """التحقق من أن نوع الملف مسموح به"""
    ALLOWED_EXTENSIONS = {'txt', 'pdf', 'docx', 'jpg', 'jpeg', 'png'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
