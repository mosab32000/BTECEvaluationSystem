#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
سكريبت بسيط للتحقق من اتصال قاعدة البيانات وعرض جداول نظام تقييم BTEC
"""

import os
import sys
import logging
import psycopg2
from dotenv import load_dotenv

# تهيئة السجلات
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('database_check')

# تحميل متغيرات البيئة
load_dotenv()

def test_db_connection():
    """اختبار الاتصال بقاعدة البيانات"""
    logger.info("جاري التحقق من اتصال قاعدة البيانات...")
    
    db_url = os.environ.get('DATABASE_URL')
    if not db_url:
        logger.error("خطأ: متغير البيئة DATABASE_URL غير موجود")
        return False
    
    try:
        # محاولة اتصال بقاعدة البيانات
        conn = psycopg2.connect(db_url)
        conn.close()
        logger.info("تم الاتصال بقاعدة البيانات بنجاح!")
        return True
    except Exception as e:
        logger.error(f"فشل الاتصال بقاعدة البيانات: {str(e)}")
        return False

def list_tables():
    """عرض قائمة بجداول قاعدة البيانات"""
    db_url = os.environ.get('DATABASE_URL')
    if not db_url:
        logger.error("خطأ: متغير البيئة DATABASE_URL غير موجود")
        return []
    
    try:
        conn = psycopg2.connect(db_url)
        cursor = conn.cursor()
        
        # استعلام لعرض جميع الجداول في قاعدة البيانات
        cursor.execute("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public'
            ORDER BY table_name
        """)
        
        tables = [table[0] for table in cursor.fetchall()]
        
        cursor.close()
        conn.close()
        
        return tables
    except Exception as e:
        logger.error(f"فشل في استرجاع قائمة الجداول: {str(e)}")
        return []

def main():
    """الدالة الرئيسية"""
    logger.info("بدء فحص قاعدة بيانات نظام تقييم BTEC...")
    
    # التحقق من اتصال قاعدة البيانات
    if not test_db_connection():
        logger.error("فشل التحقق من قاعدة البيانات. يرجى التأكد من إعدادات الاتصال.")
        sys.exit(1)
    
    # عرض جداول قاعدة البيانات
    tables = list_tables()
    if not tables:
        logger.warning("لم يتم العثور على أي جداول في قاعدة البيانات.")
        logger.info("قد تحتاج إلى تشغيل 'python init_db.py' لإنشاء الجداول.")
    else:
        logger.info(f"تم العثور على {len(tables)} جدول:")
        for table in tables:
            logger.info(f"  - {table}")
    
    logger.info("اكتمل فحص قاعدة البيانات.")
    return 0

if __name__ == "__main__":
    sys.exit(main())