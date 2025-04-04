"""
مسارات المسؤول للتحكم في النظام
"""
import logging
from datetime import datetime, timedelta

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import func, desc

from app import db
from app.models.user import User
from app.models.evaluation import Evaluation
from app.models.rubric import Rubric
from app.models.audit import AuditLog
from app.models.system_metrics import SystemMetrics
from app.core.security import token_required
from app.database import log_audit, get_latest_metrics

# إنشاء Blueprint للمسؤول
admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.route('/dashboard', methods=['GET'])
@jwt_required()
@token_required(allowed_roles=['admin'])
def admin_dashboard():
    """
    الحصول على بيانات لوحة تحكم المسؤول
    """
    # إحصائيات المستخدمين
    total_users = User.query.count()
    active_users = User.query.filter_by(is_active=True).count()
    admin_users = User.query.filter_by(role='admin').count()
    
    # إحصائيات التقييمات
    total_evaluations = Evaluation.query.count()
    verified_evaluations = Evaluation.query.filter_by(is_verified=True).count()
    
    # التقييمات الأخيرة
    recent_evaluations = Evaluation.query.order_by(Evaluation.created_at.desc()).limit(5).all()
    
    # المستخدمين الجدد
    new_users = User.query.order_by(User.created_at.desc()).limit(5).all()
    
    # آخر مقاييس النظام
    system_metrics = get_latest_metrics()
    
    # إرجاع البيانات
    return jsonify({
        'status': 'success',
        'stats': {
            'users': {
                'total': total_users,
                'active': active_users,
                'admin': admin_users
            },
            'evaluations': {
                'total': total_evaluations,
                'verified': verified_evaluations,
                'verification_rate': (verified_evaluations / total_evaluations) * 100 if total_evaluations > 0 else 0
            },
            'system': system_metrics
        },
        'recent_evaluations': [evaluation.to_dict() for evaluation in recent_evaluations],
        'new_users': [user.to_dict() for user in new_users]
    }), 200

@admin_bp.route('/users', methods=['GET'])
@jwt_required()
@token_required(allowed_roles=['admin'])
def get_users():
    """
    الحصول على قائمة المستخدمين
    """
    current_user_id = get_jwt_identity()
    
    # الحصول على معلمات الاستعلام
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    search = request.args.get('search', '')
    
    # البحث عن المستخدمين
    query = User.query
    
    # تطبيق البحث إذا كان متوفرًا
    if search:
        query = query.filter(
            (User.name.like(f'%{search}%')) |
            (User.email.like(f'%{search}%'))
        )
    
    # ترتيب المستخدمين حسب تاريخ الإنشاء
    users = query.order_by(User.created_at.desc()).paginate(page=page, per_page=per_page)
    
    # تسجيل الحدث
    log_audit('admin_list_users', f"Admin ID: {current_user_id}")
    
    # إرجاع المستخدمين
    return jsonify({
        'status': 'success',
        'users': [user.to_dict() for user in users.items],
        'pagination': {
            'total': users.total,
            'pages': users.pages,
            'page': page,
            'per_page': per_page,
            'prev_page': users.prev_num,
            'next_page': users.next_num,
            'has_prev': users.has_prev,
            'has_next': users.has_next
        }
    }), 200

@admin_bp.route('/user/<int:user_id>', methods=['PUT'])
@jwt_required()
@token_required(allowed_roles=['admin'])
def update_user(user_id):
    """
    تحديث معلومات مستخدم (بواسطة المسؤول)
    """
    current_user_id = get_jwt_identity()
    data = request.json
    
    # البحث عن المستخدم
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({
            'status': 'error',
            'message': 'المستخدم غير موجود'
        }), 404
    
    try:
        # تحديث معلومات المستخدم
        if 'name' in data:
            user.name = data['name']
        
        if 'email' in data and data['email'] != user.email:
            # التحقق من عدم وجود مستخدم آخر بنفس البريد الإلكتروني
            existing_user = User.query.filter_by(email=data['email']).first()
            if existing_user and existing_user.id != user_id:
                return jsonify({
                    'status': 'error',
                    'message': 'البريد الإلكتروني مستخدم بالفعل'
                }), 400
            
            user.email = data['email']
        
        if 'role' in data:
            # التحقق من أن المستخدم الحالي ليس المسؤول الوحيد
            if user.role == 'admin' and data['role'] != 'admin':
                admin_count = User.query.filter_by(role='admin', is_active=True).count()
                if admin_count <= 1:
                    return jsonify({
                        'status': 'error',
                        'message': 'لا يمكن تغيير دور المسؤول الوحيد'
                    }), 400
            
            user.role = data['role']
        
        if 'is_active' in data:
            # التحقق من أن المستخدم الحالي ليس المسؤول الوحيد
            if user.role == 'admin' and not data['is_active']:
                admin_count = User.query.filter_by(role='admin', is_active=True).count()
                if admin_count <= 1:
                    return jsonify({
                        'status': 'error',
                        'message': 'لا يمكن تعطيل المسؤول الوحيد'
                    }), 400
            
            user.is_active = data['is_active']
        
        # تحديث تاريخ التحديث
        user.updated_at = datetime.utcnow()
        
        # حفظ التغييرات
        db.session.commit()
        
        # تسجيل الحدث
        log_audit('admin_update_user', f"Admin ID: {current_user_id}", {
            'user_id': user.id,
            'updates': data
        })
        
        # إرجاع النجاح
        return jsonify({
            'status': 'success',
            'message': 'تم تحديث معلومات المستخدم بنجاح',
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        logging.error(f"خطأ في تحديث معلومات المستخدم: {str(e)}")
        
        # تسجيل الخطأ
        log_audit('admin_update_user_error', f"Admin ID: {current_user_id}", str(e))
        
        return jsonify({
            'status': 'error',
            'message': f'حدث خطأ أثناء تحديث معلومات المستخدم: {str(e)}'
        }), 500

@admin_bp.route('/user', methods=['POST'])
@jwt_required()
@token_required(allowed_roles=['admin'])
def create_user():
    """
    إنشاء مستخدم جديد (بواسطة المسؤول)
    """
    current_user_id = get_jwt_identity()
    data = request.json
    
    # التحقق من وجود البيانات المطلوبة
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({
            'status': 'error',
            'message': 'البريد الإلكتروني وكلمة المرور مطلوبان'
        }), 400
    
    # التحقق مما إذا كان المستخدم موجودًا بالفعل
    existing_user = User.query.filter_by(email=data['email']).first()
    if existing_user:
        return jsonify({
            'status': 'error',
            'message': 'البريد الإلكتروني مسجل بالفعل'
        }), 400
    
    try:
        # إنشاء المستخدم الجديد
        from werkzeug.security import generate_password_hash
        
        user = User(
            name=data.get('name', ''),
            email=data['email'],
            password_hash=generate_password_hash(data['password']),
            role=data.get('role', 'user'),
            is_active=data.get('is_active', True),
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        # حفظ المستخدم في قاعدة البيانات
        db.session.add(user)
        db.session.commit()
        
        # تسجيل الحدث
        log_audit('admin_create_user', f"Admin ID: {current_user_id}", {
            'user_id': user.id,
            'email': user.email,
            'role': user.role
        })
        
        # إرجاع النجاح
        return jsonify({
            'status': 'success',
            'message': 'تم إنشاء المستخدم بنجاح',
            'user': user.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        logging.error(f"خطأ في إنشاء المستخدم: {str(e)}")
        
        # تسجيل الخطأ
        log_audit('admin_create_user_error', f"Admin ID: {current_user_id}", str(e))
        
        return jsonify({
            'status': 'error',
            'message': f'حدث خطأ أثناء إنشاء المستخدم: {str(e)}'
        }), 500

@admin_bp.route('/audit-log', methods=['GET'])
@jwt_required()
@token_required(allowed_roles=['admin'])
def get_audit_log():
    """
    الحصول على سجل التدقيق
    """
    current_user_id = get_jwt_identity()
    
    # الحصول على معلمات الاستعلام
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    event_type = request.args.get('event_type', '')
    user = request.args.get('user', '')
    days = request.args.get('days', 0, type=int)
    
    # البحث عن سجلات التدقيق
    query = AuditLog.query
    
    # تطبيق الفلاتر
    if event_type:
        query = query.filter(AuditLog.event_type == event_type)
    
    if user:
        query = query.filter(AuditLog.user.like(f'%{user}%'))
    
    if days > 0:
        date_limit = datetime.utcnow() - timedelta(days=days)
        query = query.filter(AuditLog.created_at >= date_limit)
    
    # ترتيب سجلات التدقيق حسب تاريخ الإنشاء (الأحدث أولاً)
    audit_logs = query.order_by(AuditLog.created_at.desc()).paginate(page=page, per_page=per_page)
    
    # إرجاع سجلات التدقيق
    return jsonify({
        'status': 'success',
        'audit_logs': [log.to_dict() for log in audit_logs.items],
        'pagination': {
            'total': audit_logs.total,
            'pages': audit_logs.pages,
            'page': page,
            'per_page': per_page,
            'prev_page': audit_logs.prev_num,
            'next_page': audit_logs.next_num,
            'has_prev': audit_logs.has_prev,
            'has_next': audit_logs.has_next
        }
    }), 200

@admin_bp.route('/metrics', methods=['GET'])
@jwt_required()
@token_required(allowed_roles=['admin'])
def get_system_metrics():
    """
    الحصول على مقاييس النظام
    """
    days = request.args.get('days', 7, type=int)
    
    # تحديد فترة البيانات
    date_limit = datetime.utcnow() - timedelta(days=days)
    
    # الحصول على مقاييس النظام للفترة المحددة
    metrics = SystemMetrics.query.filter(SystemMetrics.created_at >= date_limit) \
        .order_by(SystemMetrics.created_at) \
        .all()
    
    # إرجاع المقاييس
    return jsonify({
        'status': 'success',
        'metrics': [metric.to_dict() for metric in metrics]
    }), 200
