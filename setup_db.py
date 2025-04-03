"""
هذا البرنامج يقوم بإنشاء قواعد البيانات المطلوبة لنظام تقييم BTEC
"""

from backend.app import create_app
from backend.app.database import db

if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        db.create_all()
        print("تم إنشاء جداول قاعدة البيانات بنجاح!")