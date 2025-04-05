"""
واجهة قاعدة البيانات لنظام تقييم BTEC
"""
import os
import logging
import json
import psycopg2
import psycopg2.extras
from contextlib import contextmanager
from datetime import datetime

from flask import current_app, g
from dotenv import load_dotenv

# تحميل المتغيرات البيئية
load_dotenv()

# تهيئة السجل
logger = logging.getLogger(__name__)

def get_db_url():
    """
    الحصول على عنوان اتصال قاعدة البيانات
    
    Returns:
        str: عنوان الاتصال
    """
    # محاولة الحصول على URL من متغير البيئة
    database_url = os.environ.get('DATABASE_URL')
    
    # إذا لم يكن متوفرًا، استخدم القيم المنفصلة
    if not database_url:
        host = os.environ.get('PGHOST', 'localhost')
        port = os.environ.get('PGPORT', '5432')
        user = os.environ.get('PGUSER', 'postgres')
        password = os.environ.get('PGPASSWORD', 'postgres')
        dbname = os.environ.get('PGDATABASE', 'btec_evaluation')
        
        database_url = f"postgresql://{user}:{password}@{host}:{port}/{dbname}"
    
    return database_url

def get_db_conn():
    """
    الحصول على اتصال قاعدة البيانات
    
    Returns:
        connection: كائن اتصال قاعدة البيانات
    """
    # تحقق مما إذا كان الاتصال موجودًا بالفعل في سياق Flask
    if 'db_conn' not in g:
        try:
            # الحصول على عنوان الاتصال
            database_url = get_db_url()
            
            # إنشاء اتصال جديد
            g.db_conn = psycopg2.connect(
                database_url,
                cursor_factory=psycopg2.extras.DictCursor
            )
            
            logger.debug("تم إنشاء اتصال قاعدة بيانات جديد")
        
        except Exception as e:
            logger.error(f"فشل الاتصال بقاعدة البيانات: {e}")
            return None
    
    return g.db_conn

@contextmanager
def get_db_cursor(commit=False):
    """
    الحصول على مؤشر قاعدة البيانات
    
    Args:
        commit (bool): ما إذا كان سيتم تأكيد التغييرات تلقائيًا
        
    Yields:
        cursor: مؤشر قاعدة البيانات
    """
    # الحصول على اتصال قاعدة البيانات
    conn = get_db_conn()
    
    if not conn:
        logger.error("لا يمكن الحصول على مؤشر بدون اتصال")
        raise Exception("فشل الاتصال بقاعدة البيانات")
    
    cursor = None
    try:
        # إنشاء مؤشر جديد
        cursor = conn.cursor()
        
        # تسليم المؤشر للاستخدام
        yield cursor
        
        # إذا طلب التأكيد، قم بتأكيد التغييرات
        if commit:
            conn.commit()
    
    except Exception as e:
        # في حالة حدوث خطأ، تراجع عن التغييرات
        conn.rollback()
        logger.error(f"خطأ في عملية قاعدة البيانات: {e}")
        raise
    
    finally:
        # إغلاق المؤشر دائمًا
        if cursor:
            cursor.close()

def init_db():
    """
    تهيئة قاعدة البيانات وإنشاء الجداول
    
    Returns:
        bool: حالة نجاح العملية
    """
    try:
        conn = get_db_conn()
        cursor = conn.cursor()
        
        # إنشاء جدول المستخدمين
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                email VARCHAR(120) UNIQUE NOT NULL,
                password_hash VARCHAR(256) NOT NULL,
                name VARCHAR(100),
                role VARCHAR(20) DEFAULT 'student',
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # إنشاء جدول معايير التقييم
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS rubrics (
                id SERIAL PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                description TEXT,
                criteria JSONB DEFAULT '{}',
                max_score FLOAT DEFAULT 100,
                created_by INTEGER REFERENCES users(id),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # إنشاء جدول التقييمات
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS evaluations (
                id SERIAL PRIMARY KEY,
                student_id INTEGER REFERENCES users(id),
                assignment_id VARCHAR(50),
                rubric_id INTEGER REFERENCES rubrics(id),
                submission_text TEXT,
                evaluation_result JSONB DEFAULT '{}',
                score FLOAT,
                ai_score FLOAT,
                evaluator_id INTEGER REFERENCES users(id),
                evaluator_comments TEXT,
                status VARCHAR(20) DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # إنشاء جدول التحقق من البلوكتشين
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS blockchain_verifications (
                id SERIAL PRIMARY KEY,
                evaluation_id INTEGER REFERENCES evaluations(id),
                hash_value VARCHAR(256) NOT NULL,
                transaction_id VARCHAR(256) NOT NULL,
                verified BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        conn.commit()
        logger.info("تم تهيئة قاعدة البيانات بنجاح")
        return True
    
    except Exception as e:
        if conn:
            conn.rollback()
        logger.error(f"فشل في تهيئة قاعدة البيانات: {e}")
        return False
    
    finally:
        if cursor:
            cursor.close()

def close_db(e=None):
    """
    إغلاق اتصال قاعدة البيانات
    
    Args:
        e: كائن الاستثناء (اختياري)
    """
    # الحصول على اتصال قاعدة البيانات من سياق Flask
    db_conn = g.pop('db_conn', None)
    
    # إذا كان الاتصال موجودًا، أغلقه
    if db_conn is not None:
        db_conn.close()
        logger.debug("تم إغلاق اتصال قاعدة البيانات")

def check_database_connection():
    """
    التحقق من اتصال قاعدة البيانات
    
    Returns:
        bool: حالة الاتصال
    """
    try:
        conn = get_db_conn()
        
        if not conn:
            return False
        
        cursor = conn.cursor()
        
        # التحقق من الاتصال عن طريق استعلام بسيط
        cursor.execute("SELECT 1")
        result = cursor.fetchone()
        
        cursor.close()
        
        return result[0] == 1
    
    except Exception as e:
        logger.error(f"فشل التحقق من اتصال قاعدة البيانات: {e}")
        return False