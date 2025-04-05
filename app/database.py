"""
واجهة قاعدة البيانات لنظام تقييم BTEC
"""
import os
import logging
import psycopg2
import psycopg2.extras
from contextlib import contextmanager
from urllib.parse import urlparse

from flask import current_app, g
from dotenv import load_dotenv

# تحميل متغيرات البيئة
load_dotenv()

# تهيئة السجل
logger = logging.getLogger(__name__)

def get_db_url():
    """
    الحصول على عنوان اتصال قاعدة البيانات
    
    Returns:
        str: عنوان الاتصال
    """
    # أولاً، نحاول الحصول على عنوان الاتصال من متغيرات البيئة
    db_url = os.environ.get('DATABASE_URL')
    
    if not db_url:
        # إنشاء عنوان اتصال من مكونات قاعدة البيانات
        db_user = os.environ.get('PGUSER')
        db_password = os.environ.get('PGPASSWORD')
        db_host = os.environ.get('PGHOST', 'localhost')
        db_port = os.environ.get('PGPORT', '5432')
        db_name = os.environ.get('PGDATABASE')
        
        if all([db_user, db_password, db_host, db_port, db_name]):
            db_url = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
        else:
            # استخدام اتصال افتراضي لبيئة التطوير
            logger.warning("تعذر العثور على متغيرات بيئة قاعدة البيانات، استخدام اتصال افتراضي")
            db_url = "postgresql://postgres:postgres@localhost:5432/btec_evaluation"
    
    # التأكد من أن عنوان الاتصال يبدأ بـ 'postgresql://'
    if db_url.startswith('postgres://'):
        db_url = db_url.replace('postgres://', 'postgresql://', 1)
    
    logger.debug(f"عنوان اتصال قاعدة البيانات: {db_url.split('@')[0].split('://')[0]}://*****@{db_url.split('@')[1]}")
    return db_url

def get_db_conn():
    """
    الحصول على اتصال قاعدة البيانات
    
    Returns:
        connection: كائن اتصال قاعدة البيانات
    """
    # إذا كنا في سياق طلب Flask وتم إنشاء اتصال مسبقًا، نستخدمه
    if hasattr(g, 'db_conn') and g.db_conn:
        return g.db_conn
    
    try:
        db_url = get_db_url()
        conn = psycopg2.connect(
            db_url,
            cursor_factory=psycopg2.extras.DictCursor
        )
        
        # إذا كنا في سياق طلب Flask، نحفظ الاتصال
        if hasattr(g, 'db_conn'):
            g.db_conn = conn
        
        return conn
    except psycopg2.Error as e:
        logger.error(f"خطأ في الاتصال بقاعدة البيانات: {e}")
        raise

@contextmanager
def get_db_cursor(commit=False):
    """
    الحصول على مؤشر قاعدة البيانات
    
    Args:
        commit (bool): ما إذا كان سيتم تأكيد التغييرات تلقائيًا
        
    Yields:
        cursor: مؤشر قاعدة البيانات
    """
    conn = get_db_conn()
    try:
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        yield cursor
        if commit:
            conn.commit()
    except Exception as e:
        conn.rollback()
        logger.error(f"خطأ في عملية قاعدة البيانات: {e}")
        raise
    finally:
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
                role VARCHAR(20) DEFAULT 'user',
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # إنشاء جدول معايير التقييم
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS rubrics (
                id SERIAL PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                description TEXT,
                criteria JSONB,
                max_score FLOAT DEFAULT 100,
                created_by INTEGER REFERENCES users(id),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # إنشاء جدول التقييمات
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS evaluations (
                id SERIAL PRIMARY KEY,
                student_id INTEGER REFERENCES users(id),
                assignment_id VARCHAR(100),
                rubric_id INTEGER REFERENCES rubrics(id),
                submission_text TEXT,
                evaluation_result JSONB,
                score FLOAT,
                ai_score FLOAT,
                evaluator_id INTEGER REFERENCES users(id),
                evaluator_comments TEXT,
                status VARCHAR(20) DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # إنشاء جدول التحقق من صحة التقييمات باستخدام البلوكتشين
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS blockchain_verifications (
                id SERIAL PRIMARY KEY,
                evaluation_id INTEGER REFERENCES evaluations(id),
                hash_value VARCHAR(256) NOT NULL,
                transaction_id VARCHAR(256),
                verified BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # إنشاء فهارس لتحسين الأداء
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_users_role ON users(role)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_evaluations_student_id ON evaluations(student_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_evaluations_evaluator_id ON evaluations(evaluator_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_evaluations_status ON evaluations(status)")
        
        conn.commit()
        logger.info("تم تهيئة قاعدة البيانات بنجاح")
        return True
    
    except Exception as e:
        conn.rollback()
        logger.error(f"خطأ في تهيئة قاعدة البيانات: {e}")
        return False
    
    finally:
        cursor.close()

def close_db(e=None):
    """
    إغلاق اتصال قاعدة البيانات
    
    Args:
        e: كائن الاستثناء (اختياري)
    """
    db_conn = g.pop('db_conn', None)
    
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
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        result = cursor.fetchone()
        cursor.close()
        
        return result[0] == 1
    
    except Exception as e:
        logger.error(f"فشل في الاتصال بقاعدة البيانات: {e}")
        return False