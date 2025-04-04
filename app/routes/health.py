"""
مسارات صحة النظام
"""

from flask import Blueprint, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import User
import os
import psutil
import datetime

health = Blueprint('health', __name__)

@health.route('/check', methods=['GET'])
def health_check():
    """
    التحقق من الصحة العامة للنظام
    """
    # التحقق من الاتصال بقاعدة البيانات
    try:
        user_count = User.query.count()
        db_status = "متصل"
    except Exception as e:
        current_app.logger.error(f"خطأ في الاتصال بقاعدة البيانات: {str(e)}")
        db_status = "غير متصل"
    
    # جمع معلومات حول النظام
    system_info = {
        'memory_usage': psutil.virtual_memory().percent,
        'cpu_usage': psutil.cpu_percent(interval=0.1),
        'disk_usage': psutil.disk_usage('/').percent,
        'time': datetime.datetime.now().isoformat()
    }
    
    return jsonify(
        status="ok",
        message="نظام تقييم BTEC يعمل بشكل جيد",
        database_status=db_status,
        system_info=system_info,
        registered_users=user_count if db_status == "متصل" else "غير متاح"
    ), 200

@health.route('/detailed', methods=['GET'])
@jwt_required()
def detailed_health():
    """
    تحقق مفصل من صحة النظام - يتطلب صلاحيات الإدارة
    """
    # التحقق من صلاحيات المستخدم
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user or not user.is_admin():
        return jsonify(error="صلاحيات غير كافية", message="هذه العملية تتطلب صلاحيات المسؤول"), 403
    
    # التحقق من الاتصال بقاعدة البيانات
    try:
        user_count = User.query.count()
        db_status = {
            'status': "متصل",
            'user_count': user_count
        }
    except Exception as e:
        current_app.logger.error(f"خطأ في الاتصال بقاعدة البيانات: {str(e)}")
        db_status = {
            'status': "غير متصل",
            'error': str(e)
        }
    
    # التحقق من وجود المفاتيح اللازمة للخدمات الخارجية
    external_services = {
        'openai_api': bool(current_app.config.get('OPENAI_API_KEY')),
        'infura_url': bool(current_app.config.get('INFURA_URL')),
        'contract_address': bool(current_app.config.get('CONTRACT_ADDRESS')),
        'signer_private_key': bool(current_app.config.get('SIGNER_PRIVATE_KEY'))
    }
    
    # جمع معلومات مفصلة حول النظام
    system_info = {
        'memory': {
            'total': round(psutil.virtual_memory().total / (1024**3), 2),  # GB
            'available': round(psutil.virtual_memory().available / (1024**3), 2),  # GB
            'percent': psutil.virtual_memory().percent
        },
        'cpu': {
            'percent': psutil.cpu_percent(interval=0.5),
            'cores': psutil.cpu_count()
        },
        'disk': {
            'total': round(psutil.disk_usage('/').total / (1024**3), 2),  # GB
            'free': round(psutil.disk_usage('/').free / (1024**3), 2),  # GB
            'percent': psutil.disk_usage('/').percent
        },
        'process': {
            'pid': os.getpid(),
            'memory_percent': psutil.Process(os.getpid()).memory_percent(),
            'cpu_percent': psutil.Process(os.getpid()).cpu_percent(interval=0.5)
        },
        'uptime': datetime.datetime.now().isoformat()
    }
    
    return jsonify(
        status="ok",
        message="تفاصيل صحة النظام",
        database=db_status,
        external_services=external_services,
        system=system_info,
        application={
            'debug': current_app.debug,
            'environment': current_app.config.get('FLASK_ENV', 'غير محدد')
        }
    ), 200
