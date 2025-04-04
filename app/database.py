"""
قاعدة بيانات نظام تقييم BTEC
"""
import logging
import os
import time
from datetime import datetime
from sqlalchemy import create_engine, text

logger = logging.getLogger(__name__)

def get_db_url():
    """
    الحصول على رابط قاعدة البيانات من المتغيرات البيئية
    
    Returns:
        str: رابط قاعدة البيانات
    """
    db_url = os.environ.get('DATABASE_URL')
    if not db_url:
        logger.warning("DATABASE_URL غير موجود في المتغيرات البيئية. استخدام قاعدة بيانات SQLite المحلية.")
        return 'sqlite:///btec.db'
    return db_url

def check_database_connection():
    """
    التحقق من اتصال قاعدة البيانات
    
    Returns:
        tuple: (connected, error_message)
    """
    db_url = get_db_url()
    max_retries = 3
    retry_delay = 2  # ثوانٍ
    
    for attempt in range(max_retries):
        try:
            engine = create_engine(db_url)
            with engine.connect() as conn:
                conn.execute(text('SELECT 1'))
            return True, None
        except Exception as e:
            logger.error(f"خطأ في الاتصال بقاعدة البيانات (محاولة {attempt+1}/{max_retries}): {str(e)}")
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
    
    return False, f"فشل الاتصال بقاعدة البيانات بعد {max_retries} محاولات"

def get_metrics():
    """
    الحصول على مقاييس قاعدة البيانات
    
    Returns:
        dict: مقاييس قاعدة البيانات
    """
    try:
        from app import db
        
        metrics = {
            'timestamp': datetime.utcnow().isoformat(),
            'database_type': 'Unknown',
            'tables': {},
            'connections': {},
        }
        
        # نوع قاعدة البيانات
        db_url = get_db_url()
        if 'postgresql' in db_url:
            metrics['database_type'] = 'PostgreSQL'
        elif 'sqlite' in db_url:
            metrics['database_type'] = 'SQLite'
        
        # إحصائيات الجداول
        engine = db.engine
        with engine.connect() as conn:
            if metrics['database_type'] == 'PostgreSQL':
                # عدد الصفوف في كل جدول
                result = conn.execute(text("""
                    SELECT 
                        relname as table_name,
                        n_live_tup as row_count
                    FROM 
                        pg_stat_user_tables
                    ORDER BY 
                        n_live_tup DESC;
                """))
                
                for row in result:
                    metrics['tables'][row.table_name] = {
                        'row_count': row.row_count
                    }
                
                # معلومات الاتصال
                result = conn.execute(text("""
                    SELECT 
                        count(*) as total_connections
                    FROM 
                        pg_stat_activity;
                """))
                
                row = result.fetchone()
                if row:
                    metrics['connections']['total'] = row.total_connections
            
            elif metrics['database_type'] == 'SQLite':
                # قائمة الجداول
                result = conn.execute(text("SELECT name FROM sqlite_master WHERE type='table';"))
                tables = [row[0] for row in result]
                
                for table_name in tables:
                    try:
                        row_count = conn.execute(text(f"SELECT COUNT(*) FROM {table_name}")).scalar()
                        metrics['tables'][table_name] = {
                            'row_count': row_count
                        }
                    except Exception as e:
                        logger.warning(f"خطأ في الحصول على عدد الصفوف في الجدول {table_name}: {str(e)}")
        
        return metrics
    except Exception as e:
        logger.error(f"خطأ في الحصول على مقاييس قاعدة البيانات: {str(e)}")
        return {
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }