"""
وحدة قاعدة البيانات لنظام تقييم BTEC
"""
import logging
from datetime import datetime
import json

from flask import request
from sqlalchemy import text

from app import db
from app.models.audit import AuditLog
from app.models.system_metrics import SystemMetrics

def get_db_conn():
    """
    الحصول على اتصال قاعدة البيانات
    """
    return db.session

def init_db():
    """
    تهيئة قاعدة بيانات النظام
    """
    db.create_all()
    logging.info("تم تهيئة قاعدة البيانات بنجاح")

def log_audit(event_type: str, user: str = "System", details: str = ""):
    """
    تسجيل حدث في سجل التدقيق
    """
    try:
        # إذا كانت التفاصيل قاموسًا، قم بتحويلها إلى سلسلة JSON
        if isinstance(details, dict):
            details = json.dumps(details)
        
        # إنشاء سجل تدقيق جديد
        audit_log = AuditLog(
            event_type=event_type,
            user=user,
            details=details,
            ip_address=request.remote_addr if request else None,
            user_agent=request.user_agent.string if request and request.user_agent else None
        )
        
        # إضافة سجل التدقيق إلى قاعدة البيانات
        db.session.add(audit_log)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        logging.error(f"خطأ في تسجيل حدث التدقيق: {str(e)}")

def update_metrics(api_call=False, evaluation=False, blockchain=False, response_time=None, error=False, active_user=False):
    """
    تحديث مقاييس النظام
    """
    try:
        # الحصول على آخر مقاييس للنظام
        latest_metrics = SystemMetrics.query.order_by(SystemMetrics.created_at.desc()).first()
        
        # إذا لم تكن هناك مقاييس سابقة، قم بإنشاء واحدة جديدة
        if not latest_metrics:
            latest_metrics = SystemMetrics()
        
        # إنشاء مقاييس جديدة بناءً على الأحدث
        new_metrics = SystemMetrics(
            user_count=latest_metrics.user_count,
            evaluation_count=latest_metrics.evaluation_count,
            verification_count=latest_metrics.verification_count,
            api_calls_count=latest_metrics.api_calls_count,
            active_users_count=latest_metrics.active_users_count,
            average_response_time=latest_metrics.average_response_time,
            error_count=latest_metrics.error_count
        )
        
        # تحديث المقاييس بناءً على الحدث
        if api_call:
            new_metrics.api_calls_count += 1
        
        if evaluation:
            new_metrics.evaluation_count += 1
        
        if blockchain:
            new_metrics.verification_count += 1
        
        if error:
            new_metrics.error_count += 1
        
        if active_user:
            new_metrics.active_users_count += 1
        
        # تحديث الوقت المتوسط للاستجابة
        if response_time:
            current_total = latest_metrics.average_response_time * latest_metrics.api_calls_count
            new_total = current_total + response_time
            new_count = latest_metrics.api_calls_count + 1
            new_metrics.average_response_time = new_total / new_count
        
        # تحديث عدد المستخدمين (يتم احتسابه مباشرة من قاعدة البيانات)
        from app.models.user import User
        user_count = User.query.count()
        new_metrics.user_count = user_count
        
        # إضافة المقاييس الجديدة إلى قاعدة البيانات
        db.session.add(new_metrics)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        logging.error(f"خطأ في تحديث مقاييس النظام: {str(e)}")

def get_latest_metrics():
    """
    الحصول على أحدث مقاييس النظام
    """
    try:
        latest_metrics = SystemMetrics.query.order_by(SystemMetrics.created_at.desc()).first()
        return latest_metrics.to_dict() if latest_metrics else {}
    except Exception as e:
        logging.error(f"خطأ في الحصول على مقاييس النظام: {str(e)}")
        return {}
