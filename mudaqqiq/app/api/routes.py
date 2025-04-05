from flask import jsonify, request, current_app, abort, url_for
from flask_login import current_user, login_required
from app import db
from app.api import api
from app.models import User, Project, AuditResult, AuditCriteria
from app.utils import log_activity
from functools import wraps
import jwt
from datetime import datetime, timedelta

# وظيفة للتحقق من رمز API
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        # التحقق من وجود التوكن في الهيدر
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            parts = auth_header.split()
            
            if len(parts) == 2 and parts[0].lower() == 'bearer':
                token = parts[1]
        
        if not token:
            return jsonify({'message': 'لم يتم توفير رمز الوصول!'}), 401
        
        try:
            data = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
            current_user = User.query.filter_by(id=data['user_id']).first()
        except:
            return jsonify({'message': 'رمز وصول غير صالح!'}), 401
        
        if not current_user:
            return jsonify({'message': 'المستخدم غير موجود!'}), 401
        
        if not current_user.is_active:
            return jsonify({'message': 'الحساب معطل!'}), 403
        
        return f(current_user, *args, **kwargs)
    
    return decorated

# نقطة نهاية للحصول على رمز وصول
@api.route('/token', methods=['POST'])
def get_token():
    auth = request.authorization
    
    if not auth or not auth.username or not auth.password:
        return jsonify({'message': 'بيانات المصادقة مفقودة!'}), 401
    
    user = User.query.filter_by(email=auth.username).first()
    
    if not user or not user.verify_password(auth.password):
        return jsonify({'message': 'البريد الإلكتروني أو كلمة المرور غير صحيحة!'}), 401
    
    if not user.is_active:
        return jsonify({'message': 'الحساب معطل!'}), 403
    
    # إنشاء رمز JWT صالح لمدة ساعة
    token = jwt.encode(
        {
            'user_id': user.id,
            'exp': datetime.utcnow() + timedelta(hours=1)
        },
        current_app.config['SECRET_KEY'],
        algorithm='HS256'
    )
    
    log_activity(user, 'إنشاء رمز API', ip_address=request.remote_addr)
    
    return jsonify({
        'token': token,
        'user_id': user.id,
        'username': user.username,
        'expiration': (datetime.utcnow() + timedelta(hours=1)).isoformat()
    })

# نقطة نهاية لاختبار صلاحية الرمز
@api.route('/check_token', methods=['GET'])
@token_required
def check_token(current_user):
    return jsonify({
        'status': 'success',
        'message': 'الرمز صالح',
        'user': {
            'id': current_user.id,
            'username': current_user.username,
            'email': current_user.email,
            'is_admin': current_user.is_admin()
        }
    })

# نقطة نهاية للحصول على مشاريع المستخدم
@api.route('/projects', methods=['GET'])
@token_required
def get_projects(current_user):
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 10, type=int), 50)
    
    if current_user.is_admin() and request.args.get('all') == 'true':
        # المدراء يمكنهم الوصول إلى جميع المشاريع
        query = Project.query
    else:
        # المستخدم العادي يمكنه الوصول إلى مشاريعه فقط
        query = Project.query.filter_by(user_id=current_user.id)
    
    projects_page = query.order_by(Project.submission_date.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    projects_list = []
    for project in projects_page.items:
        projects_list.append({
            'id': project.id,
            'title': project.title,
            'description': project.description,
            'project_type': project.project_type,
            'status': project.status,
            'submission_date': project.submission_date.isoformat(),
            'completion_date': project.completion_date.isoformat() if project.completion_date else None,
            'user_id': project.user_id,
            'has_file': bool(project.file_path),
            'file_url': url_for('projects.download_file', id=project.id, _external=True) if project.file_path else None
        })
    
    return jsonify({
        'projects': projects_list,
        'pagination': {
            'page': projects_page.page,
            'per_page': projects_page.per_page,
            'total_pages': projects_page.pages,
            'total_items': projects_page.total
        }
    })

# نقطة نهاية للحصول على تفاصيل مشروع محدد
@api.route('/projects/<int:id>', methods=['GET'])
@token_required
def get_project(current_user, id):
    project = Project.query.get_or_404(id)
    
    # التحقق من الصلاحيات
    if project.user_id != current_user.id and not current_user.is_admin():
        return jsonify({'message': 'غير مصرح لك بالوصول إلى هذا المشروع!'}), 403
    
    # الحصول على نتائج التدقيق
    audit_results = []
    for result in AuditResult.query.filter_by(project_id=project.id).order_by(AuditResult.audit_date.desc()).all():
        auditor = User.query.get(result.auditor_id)
        audit_results.append({
            'id': result.id,
            'audit_date': result.audit_date.isoformat(),
            'status': result.status,
            'score': result.score,
            'feedback': result.feedback,
            'result_details': result.result_details,
            'auditor': {
                'id': auditor.id,
                'username': auditor.username,
                'full_name': auditor.full_name
            } if auditor else None
        })
    
    return jsonify({
        'id': project.id,
        'title': project.title,
        'description': project.description,
        'project_type': project.project_type,
        'status': project.status,
        'submission_date': project.submission_date.isoformat(),
        'completion_date': project.completion_date.isoformat() if project.completion_date else None,
        'user_id': project.user_id,
        'has_file': bool(project.file_path),
        'file_url': url_for('projects.download_file', id=project.id, _external=True) if project.file_path else None,
        'audit_results': audit_results
    })

# نقطة نهاية للحصول على معايير التدقيق
@api.route('/audit_criteria', methods=['GET'])
@token_required
def get_audit_criteria(current_user):
    criteria = AuditCriteria.query.all()
    criteria_list = []
    
    for c in criteria:
        criteria_list.append({
            'id': c.id,
            'name': c.name,
            'description': c.description,
            'category': c.category,
            'weight': c.weight
        })
    
    return jsonify({
        'audit_criteria': criteria_list
    })

# نقطة نهاية للحصول على ملخص الإحصائيات
@api.route('/stats', methods=['GET'])
@token_required
def get_stats(current_user):
    if current_user.is_admin():
        # إحصائيات المدراء
        total_users = User.query.count()
        total_projects = Project.query.count()
        pending_projects = Project.query.filter_by(status='قيد الانتظار').count()
        completed_projects = Project.query.filter_by(status='مكتمل').count()
        avg_score = db.session.query(db.func.avg(AuditResult.score)).scalar() or 0
        
        # عدد المشاريع حسب النوع
        projects_by_type = db.session.query(
            Project.project_type, 
            db.func.count(Project.id)
        ).group_by(Project.project_type).all()
        
        projects_by_type_dict = {pt: count for pt, count in projects_by_type}
        
        return jsonify({
            'total_users': total_users,
            'total_projects': total_projects,
            'pending_projects': pending_projects,
            'completed_projects': completed_projects,
            'avg_score': round(avg_score, 2),
            'projects_by_type': projects_by_type_dict
        })
    else:
        # إحصائيات المستخدم العادي
        user_projects = Project.query.filter_by(user_id=current_user.id).count()
        pending_projects = Project.query.filter_by(user_id=current_user.id, status='قيد الانتظار').count()
        completed_projects = Project.query.filter_by(user_id=current_user.id, status='مكتمل').count()
        
        # متوسط درجات مشاريع المستخدم
        user_projects_ids = [p.id for p in Project.query.filter_by(user_id=current_user.id).all()]
        avg_score = 0
        if user_projects_ids:
            avg_score = db.session.query(db.func.avg(AuditResult.score)).filter(
                AuditResult.project_id.in_(user_projects_ids)
            ).scalar() or 0
        
        return jsonify({
            'user_projects': user_projects,
            'pending_projects': pending_projects,
            'completed_projects': completed_projects,
            'avg_score': round(avg_score, 2)
        })
