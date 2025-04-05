"""
وحدة قاعدة البيانات لنظام تقييم BTEC
"""

import os
import logging
from flask import current_app, g
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

logger = logging.getLogger(__name__)

def get_db():
    """
    الحصول على اتصال قاعدة البيانات
    
    Returns:
        Connection: اتصال قاعدة البيانات
    """
    if "db" not in g:
        g.db = current_app.config["SQLALCHEMY_DATABASE_URI"]
    return g.db

def close_db(e=None):
    """
    إغلاق اتصال قاعدة البيانات
    
    Args:
        e: الخطأ (إن وجد)
    """
    db = g.pop("db", None)
    if db is not None:
        logger.debug("تم إغلاق اتصال قاعدة البيانات")

def init_db():
    """
    تهيئة قاعدة البيانات
    """
    logger.info("جاري تهيئة قاعدة البيانات...")
    
def init_app(app):
    """
    تهيئة التطبيق بإعدادات قاعدة البيانات
    
    Args:
        app: تطبيق Flask
    """
    app.teardown_appcontext(close_db)
    logger.info("تم تهيئة قاعدة البيانات بنجاح")

