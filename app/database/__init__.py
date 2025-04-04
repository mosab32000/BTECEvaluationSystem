"""
وحدة قاعدة البيانات لنظام تقييم BTEC
"""

import os
import sqlite3
import logging
import json
from datetime import datetime
from flask import request, g

logger = logging.getLogger(__name__)

def get_db_conn():
    """
    الحصول على اتصال قاعدة البيانات
    """
    data_dir = 'data'
    os.makedirs(data_dir, exist_ok=True)
    
    conn = sqlite3.connect(os.path.join(data_dir, 'btec_eval.db'))
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """
    تهيئة قاعدة بيانات النظام
    """
    logger.info("Initializing database...")
    conn = None
    try:
        conn = get_db_conn()
        logger.info("Database connection established")
        
        # هنا يمكن إضافة أي عمليات إضافية لإعداد قاعدة البيانات
        conn.commit()
        logger.info("Database initialization completed successfully")
    except sqlite3.Error as e:
        logger.error(f"Database initialization error: {e}", exc_info=True)
        if conn:
            conn.rollback()
    finally:
        if conn:
            conn.close()

def log_audit(event_type: str, user: str = "System", details: str = ""):
    """
    تسجيل حدث في سجل التدقيق
    """
    conn = None
    try:
        conn = get_db_conn()
        c = conn.cursor()
        
        ip_address = request.remote_addr if hasattr(request, 'remote_addr') else "N/A"
        
        c.execute(
            "INSERT INTO audit_log (event_type, user, details, ip_address) VALUES (?, ?, ?, ?)",
            (event_type, user, details, ip_address)
        )
        
        conn.commit()
        logger.debug(f"Audit log: {event_type} by {user}")
    except sqlite3.Error as e:
        logger.error(f"Error logging audit event: {e}", exc_info=True)
        if conn:
            conn.rollback()
    finally:
        if conn:
            conn.close()

def update_metrics(api_call=False, evaluation=False, blockchain=False, response_time=None, error=False, active_user=False):
    """
    تحديث مقاييس النظام
    """
    conn = None
    try:
        conn = get_db_conn()
        c = conn.cursor()
        
        # التحقق من وجود سجل لليوم الحالي
        today = datetime.now().strftime('%Y-%m-%d')
        c.execute("SELECT id FROM system_metrics WHERE date(timestamp) = ?", (today,))
        metric = c.fetchone()
        
        if metric:
            # تحديث السجل الموجود
            updates = []
            params = []
            
            if api_call:
                updates.append("api_calls = api_calls + 1")
            if evaluation:
                updates.append("evaluations_completed = evaluations_completed + 1")
            if blockchain:
                updates.append("blockchain_verifications = blockchain_verifications + 1")
            if response_time is not None:
                updates.append("average_response_time = (average_response_time * (api_calls - 1) + ?) / api_calls")
                params.append(response_time)
            if error:
                updates.append("error_count = error_count + 1")
            if active_user:
                updates.append("active_users = active_users + 1")
            
            if updates:
                query = f"UPDATE system_metrics SET {', '.join(updates)} WHERE id = ?"
                params.append(metric['id'])
                c.execute(query, params)
        else:
            # إنشاء سجل جديد
            fields = ["timestamp"]
            values = ["CURRENT_TIMESTAMP"]
            params = []
            
            if api_call:
                fields.append("api_calls")
                values.append("1")
            if evaluation:
                fields.append("evaluations_completed")
                values.append("1")
            if blockchain:
                fields.append("blockchain_verifications")
                values.append("1")
            if response_time is not None:
                fields.append("average_response_time")
                values.append("?")
                params.append(response_time)
            if error:
                fields.append("error_count")
                values.append("1")
            if active_user:
                fields.append("active_users")
                values.append("1")
            
            query = f"INSERT INTO system_metrics ({', '.join(fields)}) VALUES ({', '.join(values)})"
            c.execute(query, params)
        
        conn.commit()
    except sqlite3.Error as e:
        logger.error(f"Error updating metrics: {e}", exc_info=True)
        if conn:
            conn.rollback()
    finally:
        if conn:
            conn.close()

def get_latest_metrics():
    """
    الحصول على أحدث مقاييس النظام
    """
    conn = None
    try:
        conn = get_db_conn()
        c = conn.cursor()
        
        c.execute("SELECT * FROM system_metrics ORDER BY timestamp DESC LIMIT 1")
        metric = c.fetchone()
        
        if metric:
            return dict(metric)
        return None
    except sqlite3.Error as e:
        logger.error(f"Error fetching metrics: {e}", exc_info=True)
        return None
    finally:
        if conn:
            conn.close()