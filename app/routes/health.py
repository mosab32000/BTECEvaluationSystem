"""
مسار فحص الصحة لنظام تقييم BTEC
"""
from flask import Blueprint, jsonify

# تعريف البلوبرنت
health_bp = Blueprint('health', __name__, url_prefix='/api/health')

@health_bp.route('/')
def health_check():
    """نقطة نهاية للتحقق من صحة النظام"""
    return jsonify({
        "status": "ok",
        "service": "BTEC Evaluation System",
        "version": "1.0.0"
    })

@health_bp.route('/stats', methods=['GET'])
def system_stats():
    """
    إحصائيات النظام العامة
    """
    try:
        # إحصائيات المستخدمين والتقييمات
        with db.engine.connect() as connection:
            result = connection.execute("SELECT COUNT(*) FROM users").fetchone()
            if result:
                user_count = result[0]
            
            result = connection.execute("SELECT COUNT(*) FROM evaluations").fetchone()
            if result:
                evaluation_count = result[0]
        
        # إرجاع الإحصائيات
        return jsonify({
            'status': 'success',
            'stats': {
                'users': user_count,
                'evaluations': evaluation_count,
                'up_time': get_uptime()
            }
        }), 200
    except Exception as e:
        logging.error(f"خطأ في الحصول على إحصائيات النظام: {str(e)}")
        
        return jsonify({
            'status': 'error',
            'message': 'حدث خطأ أثناء الحصول على إحصائيات النظام'
        }), 500

@health_bp.route('/metrics', methods=['GET'])
@jwt_required()
@token_required(allowed_roles=['admin'])
def detailed_metrics():
    """
    مقاييس النظام المفصلة
    """
    try:
        # الحصول على آخر مقاييس للنظام
        latest_metrics = get_latest_metrics()
        
        # الحصول على مقاييس النظام للأسبوع الماضي
        date_limit = datetime.utcnow() - timedelta(days=7)
        weekly_metrics = SystemMetrics.query.filter(SystemMetrics.created_at >= date_limit) \
            .order_by(SystemMetrics.created_at) \
            .all()
        
        # إحصائيات المستخدمين والتقييمات
        user_stats = {
            'total': User.query.count(),
            'active': User.query.filter_by(is_active=True).count(),
            'new_last_week': User.query.filter(User.created_at >= date_limit).count()
        }
        
        evaluation_stats = {
            'total': Evaluation.query.count(),
            'verified': Evaluation.query.filter_by(is_verified=True).count(),
            'new_last_week': Evaluation.query.filter(Evaluation.created_at >= date_limit).count()
        }
        
        # معلومات النظام الحالية
        current_system_info = {
            'cpu_percent': psutil.cpu_percent(),
            'memory_percent': psutil.virtual_memory().percent,
            'disk_percent': psutil.disk_usage('/').percent,
            'up_time': get_uptime()
        }
        
        # إرجاع المقاييس المفصلة
        return jsonify({
            'status': 'success',
            'current': {
                'system': current_system_info,
                'metrics': latest_metrics,
                'users': user_stats,
                'evaluations': evaluation_stats
            },
            'history': {
                'weekly_metrics': [metric.to_dict() for metric in weekly_metrics]
            }
        }), 200
    except Exception as e:
        logging.error(f"خطأ في الحصول على مقاييس النظام المفصلة: {str(e)}")
        
        return jsonify({
            'status': 'error',
            'message': 'حدث خطأ أثناء الحصول على مقاييس النظام المفصلة'
        }), 500

def get_uptime():
    """
    الحصول على مدة تشغيل النظام
    """
    try:
        # الحصول على وقت بدء تشغيل النظام
        boot_time = datetime.fromtimestamp(psutil.boot_time())
        uptime = datetime.now() - boot_time
        
        # تنسيق مدة التشغيل
        days = uptime.days
        hours, remainder = divmod(uptime.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        
        return f"{days}d {hours}h {minutes}m {seconds}s"
    except Exception as e:
        logging.error(f"خطأ في الحصول على مدة تشغيل النظام: {str(e)}")
        return "غير معروف"

import os
import sys
import psutil
import logging
from datetime import datetime, timedelta

from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required

from app import db
from app.models.user import User
from app.models.evaluation import Evaluation
from app.models.system_metrics import SystemMetrics
from app.core.security import token_required
from app.database import get_latest_metrics