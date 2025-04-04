"""
وحدة التفاعل مع قاعدة البيانات
"""
import datetime
import json
import logging
import os
import time
from functools import wraps
from typing import Any, Dict, List, Optional, Tuple, Union

from flask import current_app, g
from sqlalchemy import text

from app import db

logger = logging.getLogger(__name__)

# التحديثات الإحصائية والمقاييس
_metrics = {
    'active_users': 0,
    'evaluations': 0,
    'blockchain_verifications': 0,
    'avg_response_time': 0,
    'errors': 0,
    'last_updated': None
}

# جدول تدقيق الأحداث (بديل مؤقت لجدول قاعدة البيانات)
_audit_log = []


def log_audit(event_type: str, user: str = "system", details: Any = None):
    """
    تسجيل حدث في سجل التدقيق
    
    Args:
        event_type: نوع الحدث (مثل login, evaluation, error)
        user: المستخدم المرتبط بالحدث (اختياري)
        details: تفاصيل إضافية عن الحدث (اختياري)
    """
    timestamp = datetime.datetime.utcnow().isoformat()
    
    # تحويل التفاصيل إلى سلسلة JSON إذا لم تكن سلسلة بالفعل
    details_str = details
    if details and not isinstance(details, str):
        try:
            details_str = json.dumps(details)
        except Exception as e:
            details_str = str(details)
    
    # إنشاء سجل الحدث
    audit_entry = {
        'timestamp': timestamp,
        'event_type': event_type,
        'user': user,
        'details': details_str
    }
    
    try:
        # في المستقبل، سنضيف هذا إلى جدول قاعدة البيانات
        # حاليًا، نضيفه إلى القائمة المؤقتة
        _audit_log.append(audit_entry)
        
        # تحديد حجم السجل المؤقت (حد أقصى 1000 حدث)
        if len(_audit_log) > 1000:
            _audit_log.pop(0)  # إزالة أقدم حدث
        
        logger.debug(f"Audit log: {event_type} - {user}")
    except Exception as e:
        logger.error(f"Error logging audit event: {e}")


def update_metrics(active_user: bool = False, evaluation: bool = False, 
                 blockchain: bool = False, response_time: float = None, 
                 error: bool = False):
    """
    تحديث المقاييس الإحصائية للنظام
    
    Args:
        active_user: ما إذا كان يجب زيادة عدد المستخدمين النشطين
        evaluation: ما إذا كان يجب زيادة عدد التقييمات
        blockchain: ما إذا كان يجب زيادة عدد عمليات التحقق من البلوكتشين
        response_time: وقت الاستجابة بالثواني (لحساب المتوسط)
        error: ما إذا كان يجب زيادة عدد الأخطاء
    """
    global _metrics
    
    try:
        if active_user:
            _metrics['active_users'] += 1
        
        if evaluation:
            _metrics['evaluations'] += 1
        
        if blockchain:
            _metrics['blockchain_verifications'] += 1
        
        if response_time:
            # حساب المتوسط المتحرك
            current_avg = _metrics['avg_response_time']
            count = _metrics['evaluations']
            
            if count > 0:
                _metrics['avg_response_time'] = (current_avg * (count - 1) + response_time) / count
            else:
                _metrics['avg_response_time'] = response_time
        
        if error:
            _metrics['errors'] += 1
        
        _metrics['last_updated'] = datetime.datetime.utcnow().isoformat()
    except Exception as e:
        logger.error(f"Error updating metrics: {e}")


def get_metrics() -> Dict:
    """
    الحصول على المقاييس الحالية
    
    Returns:
        dict: المقاييس الحالية
    """
    return _metrics


def get_recent_audit_logs(limit: int = 100, event_type: str = None, user: str = None) -> List[Dict]:
    """
    الحصول على سجلات التدقيق الأخيرة
    
    Args:
        limit: الحد الأقصى لعدد السجلات المراد إرجاعها
        event_type: تصفية حسب نوع الحدث (اختياري)
        user: تصفية حسب المستخدم (اختياري)
        
    Returns:
        list: قائمة سجلات التدقيق
    """
    filtered_logs = _audit_log
    
    if event_type:
        filtered_logs = [log for log in filtered_logs if log['event_type'] == event_type]
    
    if user:
        filtered_logs = [log for log in filtered_logs if log['user'] == user]
    
    # ترتيب السجلات حسب الوقت (الأحدث أولاً)
    sorted_logs = sorted(filtered_logs, key=lambda x: x['timestamp'], reverse=True)
    
    return sorted_logs[:limit]


def db_transaction(func):
    """
    مزخرف لضمان تنفيذ العمليات داخل معاملة قاعدة بيانات
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            result = func(*args, **kwargs)
            db.session.commit()
            return result
        except Exception as e:
            db.session.rollback()
            logger.error(f"Database transaction error: {e}")
            raise
    return wrapper


def execute_raw_sql(query: str, params: Dict = None) -> List:
    """
    تنفيذ استعلام SQL خام
    
    Args:
        query: استعلام SQL
        params: المعلمات للاستعلام (اختياري)
        
    Returns:
        list: نتائج الاستعلام
    """
    try:
        result = db.session.execute(text(query), params or {})
        return [dict(row) for row in result]
    except Exception as e:
        logger.error(f"Error executing raw SQL: {e}")
        db.session.rollback()
        raise