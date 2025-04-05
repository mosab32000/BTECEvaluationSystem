#!/usr/bin/env python
"""
سكريبت إعداد نظام تقييم BTEC وإنشاء بيئة العمل
"""

import os
import secrets
import sys
import time
from urllib.parse import urlparse
from cryptography.fernet import Fernet

# تعيين مسار السجل
LOG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs", "setup.log")
os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)

def setup_logging():
    """إعداد تسجيل السجلات"""
    import logging
    
    # إنشاء معالج السجلات
    logger = logging.getLogger("setup")
    logger.setLevel(logging.INFO)
    
    # معالج للملف
    file_handler = logging.FileHandler(LOG_FILE)
    file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(file_formatter)
    
    # معالج للطرفية
    console_handler = logging.StreamHandler()
    console_formatter = logging.Formatter('%(levelname)s: %(message)s')
    console_handler.setFormatter(console_formatter)
    
    # إضافة المعالجات
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger

# إنشاء سجل
logger = setup_logging()

def check_environment():
    """
    التحقق من المتغيرات البيئية الضرورية
    
    Returns:
        bool: ما إذا كانت جميع المتغيرات البيئية موجودة
    """
    logger.info("فحص متغيرات البيئة...")
    
    required_vars = [
        "DATABASE_URL",
        "SECRET_KEY",
        "JWT_SECRET_KEY",
        "ENCRYPTION_KEY"
    ]
    
    missing_vars = []
    
    for var in required_vars:
        if var not in os.environ:
            missing_vars.append(var)
    
    if missing_vars:
        logger.warning(f"المتغيرات البيئية التالية مفقودة: {', '.join(missing_vars)}")
        return False
    
    logger.info("تم التحقق من متغيرات البيئة بنجاح")
    return True

def generate_secret_key():
    """
    إنشاء مفتاح سري
    
    Returns:
        str: المفتاح السري
    """
    return secrets.token_hex(32)

def ensure_secret_keys():
    """
    التأكد من وجود المفاتيح السرية
    
    Returns:
        bool: ما إذا تم ضمان وجود المفاتيح السرية
    """
    logger.info("ضمان وجود المفاتيح السرية...")
    
    # تحقق من وجود المفتاح السري للتطبيق
    if "SECRET_KEY" not in os.environ:
        os.environ["SECRET_KEY"] = generate_secret_key()
        logger.info("تم إنشاء مفتاح SECRET_KEY جديد")
    
    # تحقق من وجود مفتاح JWT
    if "JWT_SECRET_KEY" not in os.environ:
        os.environ["JWT_SECRET_KEY"] = generate_secret_key()
        logger.info("تم إنشاء مفتاح JWT_SECRET_KEY جديد")
    
    # تحقق من وجود مفتاح CSRF
    if "WTF_CSRF_SECRET_KEY" not in os.environ:
        os.environ["WTF_CSRF_SECRET_KEY"] = generate_secret_key()
        logger.info("تم إنشاء مفتاح WTF_CSRF_SECRET_KEY جديد")
    
    # تحقق من وجود مفتاح التشفير
    if "ENCRYPTION_KEY" not in os.environ:
        os.environ["ENCRYPTION_KEY"] = Fernet.generate_key().decode()
        logger.info("تم إنشاء مفتاح ENCRYPTION_KEY جديد")
    
    logger.info("تم ضمان وجود جميع المفاتيح السرية")
    return True

def check_database():
    """
    التحقق من الاتصال بقاعدة البيانات
    
    Returns:
        bool: ما إذا تم الاتصال بقاعدة البيانات بنجاح
    """
    logger.info("التحقق من الاتصال بقاعدة البيانات...")
    
    try:
        import psycopg2
        
        # محاولة قراءة عنوان الاتصال من متغيرات البيئة
        db_url = os.environ.get("DATABASE_URL")
        
        if not db_url:
            logger.error("لم يتم العثور على متغير البيئة DATABASE_URL")
            return False
        
        # تحليل عنوان الاتصال
        parsed_url = urlparse(db_url)
        
        # إعداد معلمات الاتصال
        db_params = {
            'dbname': parsed_url.path[1:],
            'user': parsed_url.username,
            'password': parsed_url.password,
            'host': parsed_url.hostname,
            'port': parsed_url.port or 5432
        }
        
        logger.info(f"محاولة الاتصال بالخادم {db_params['host']}:{db_params['port']}...")
        
        # محاولة الاتصال
        conn = psycopg2.connect(**db_params)
        
        # اختبار الاستعلام
        cur = conn.cursor()
        cur.execute('SELECT version()')
        version = cur.fetchone()[0]
        logger.info(f"تم الاتصال بقاعدة البيانات: {version}")
        
        # إغلاق الاتصال
        cur.close()
        conn.close()
        
        return True
    
    except ImportError:
        logger.error("لم يتم العثور على مكتبة psycopg2. قم بتثبيتها باستخدام: pip install psycopg2-binary")
        return False
    
    except Exception as e:
        logger.error(f"فشل الاتصال بقاعدة البيانات: {str(e)}")
        return False

def setup_database():
    """
    إنشاء جداول قاعدة البيانات
    
    Returns:
        bool: ما إذا تم إنشاء الجداول بنجاح
    """
    logger.info("إنشاء جداول قاعدة البيانات...")
    
    try:
        from app import create_app
        from app.database import init_db
        
        # إنشاء سياق التطبيق
        app = create_app()
        
        with app.app_context():
            # تهيئة قاعدة البيانات
            init_db()
        
        logger.info("تم إنشاء جداول قاعدة البيانات بنجاح")
        return True
    
    except Exception as e:
        logger.error(f"فشل إنشاء جداول قاعدة البيانات: {str(e)}")
        return False

def create_admin_user():
    """
    إنشاء مستخدم مسؤول
    
    Returns:
        bool: ما إذا تم إنشاء المستخدم بنجاح
    """
    logger.info("إنشاء مستخدم مسؤول...")
    
    try:
        from app import create_app
        from app.models.user import User
        from werkzeug.security import generate_password_hash
        
        # إنشاء سياق التطبيق
        app = create_app()
        
        # القيم الافتراضية
        admin_email = os.environ.get("ADMIN_EMAIL", "admin@btec-eval.com")
        admin_password = os.environ.get("ADMIN_PASSWORD", "admin2024")
        
        with app.app_context():
            # التحقق مما إذا كان المستخدم موجوداً بالفعل
            from app.database import db
            
            admin = User.query.filter_by(email=admin_email).first()
            
            if not admin:
                admin = User(
                    email=admin_email,
                    password_hash=generate_password_hash(admin_password),
                    name="مدير النظام",
                    role="admin",
                    is_active=True
                )
                db.session.add(admin)
                db.session.commit()
                logger.info(f"تم إنشاء مستخدم مسؤول جديد: {admin_email}")
            else:
                logger.info(f"مستخدم المسؤول موجود بالفعل: {admin_email}")
        
        return True
    
    except Exception as e:
        logger.error(f"فشل إنشاء مستخدم مسؤول: {str(e)}")
        return False

def create_default_rubrics():
    """
    إنشاء معايير تقييم افتراضية
    
    Returns:
        bool: ما إذا تم إنشاء المعايير بنجاح
    """
    logger.info("إنشاء معايير تقييم افتراضية...")
    
    try:
        from app import create_app
        from app.models.rubric import Rubric
        
        # إنشاء سياق التطبيق
        app = create_app()
        
        with app.app_context():
            # التحقق من وجود معايير
            from app.database import db
            
            rubrics_count = Rubric.query.count()
            
            if rubrics_count == 0:
                # إنشاء معيار BTEC Level 2
                level2_rubric = Rubric(
                    name="BTEC Level 2 - المعيار القياسي",
                    description="معيار تقييم BTEC المستوى الثاني للمهام القياسية",
                    max_score=100,
                    criteria={
                        "pass": {
                            "description": "تحقيق الحد الأدنى من متطلبات النجاح",
                            "score_range": [40, 59]
                        },
                        "merit": {
                            "description": "تحقيق مستوى متميز يتجاوز الحد الأدنى",
                            "score_range": [60, 79]
                        },
                        "distinction": {
                            "description": "تحقيق مستوى استثنائي من الأداء",
                            "score_range": [80, 100]
                        }
                    }
                )
                db.session.add(level2_rubric)
                
                # إنشاء معيار BTEC Level 3
                level3_rubric = Rubric(
                    name="BTEC Level 3 - المعيار المتقدم",
                    description="معيار تقييم BTEC المستوى الثالث للمهام المتقدمة",
                    max_score=100,
                    criteria={
                        "pass": {
                            "description": "تحقيق الحد الأدنى من متطلبات النجاح",
                            "score_range": [40, 59]
                        },
                        "merit": {
                            "description": "تحقيق مستوى متميز يتجاوز الحد الأدنى",
                            "score_range": [60, 79]
                        },
                        "distinction": {
                            "description": "تحقيق مستوى استثنائي من الأداء",
                            "score_range": [80, 100]
                        }
                    }
                )
                db.session.add(level3_rubric)
                
                db.session.commit()
                logger.info("تم إنشاء معايير تقييم افتراضية بنجاح")
            else:
                logger.info(f"توجد معايير تقييم بالفعل ({rubrics_count} معيار)")
        
        return True
    
    except Exception as e:
        logger.error(f"فشل إنشاء معايير تقييم افتراضية: {str(e)}")
        return False

def run_system_check():
    """
    تشغيل فحص شامل للنظام
    """
    logger.info("=== بدء فحص نظام تقييم BTEC ===")
    
    # الخطوة 1: التحقق من متغيرات البيئة
    env_check = check_environment()
    
    # الخطوة 2: ضمان وجود المفاتيح السرية
    if not env_check:
        logger.info("إنشاء المفاتيح السرية المفقودة...")
        ensure_secret_keys()
    
    # الخطوة 3: التحقق من الاتصال بقاعدة البيانات
    db_check = check_database()
    
    if not db_check:
        logger.error("فشل الاتصال بقاعدة البيانات. تأكد من تكوين DATABASE_URL بشكل صحيح.")
        return False
    
    # الخطوة 4: إنشاء جداول قاعدة البيانات
    db_setup = setup_database()
    
    if not db_setup:
        logger.error("فشل إنشاء جداول قاعدة البيانات.")
        return False
    
    # الخطوة 5: إنشاء مستخدم مسؤول
    admin_setup = create_admin_user()
    
    if not admin_setup:
        logger.error("فشل إنشاء مستخدم مسؤول.")
        return False
    
    # الخطوة 6: إنشاء معايير تقييم افتراضية
    rubrics_setup = create_default_rubrics()
    
    if not rubrics_setup:
        logger.error("فشل إنشاء معايير تقييم افتراضية.")
        return False
    
    logger.info("=== تم إكمال فحص النظام بنجاح! ===")
    return True

def display_menu():
    """
    عرض قائمة الخيارات
    """
    print("\n=== نظام تقييم BTEC - أداة الإعداد ===")
    print("1. التحقق من متغيرات البيئة")
    print("2. إنشاء المفاتيح السرية")
    print("3. اختبار الاتصال بقاعدة البيانات")
    print("4. إنشاء جداول قاعدة البيانات")
    print("5. إنشاء مستخدم مسؤول")
    print("6. إنشاء معايير تقييم افتراضية")
    print("7. تشغيل جميع عمليات الإعداد")
    print("8. تشغيل خادم التطوير")
    print("9. الخروج")
    
    choice = input("\nاختر رقم العملية: ")
    return choice

def menu_loop():
    """
    حلقة القائمة الرئيسية
    """
    while True:
        choice = display_menu()
        
        if choice == '1':
            check_environment()
        elif choice == '2':
            ensure_secret_keys()
        elif choice == '3':
            check_database()
        elif choice == '4':
            setup_database()
        elif choice == '5':
            create_admin_user()
        elif choice == '6':
            create_default_rubrics()
        elif choice == '7':
            run_system_check()
        elif choice == '8':
            try:
                print("\nتشغيل خادم التطوير... (اضغط CTRL+C للإيقاف)")
                from run import app
                app.run(host="0.0.0.0", port=5000, debug=True)
            except KeyboardInterrupt:
                print("\nتم إيقاف الخادم")
            except Exception as e:
                print(f"\nحدث خطأ أثناء تشغيل الخادم: {str(e)}")
        elif choice == '9':
            print("\nشكرًا لاستخدام أداة إعداد نظام تقييم BTEC!")
            break
        else:
            print("\nاختيار غير صالح. الرجاء إدخال رقم من 1 إلى 9.")
        
        # انتظار قبل عرض القائمة مرة أخرى
        if choice != '8':  # تجنب الانتظار بعد الخروج من الخادم
            input("\nاضغط Enter للمتابعة...")

def main():
    """
    الدالة الرئيسية
    """
    # عرض ترحيب
    print("===========================================")
    print("  مرحبًا بك في أداة إعداد نظام تقييم BTEC  ")
    print("===========================================")
    print("\nتساعدك هذه الأداة في إعداد وتهيئة نظام تقييم BTEC.")
    
    # تحديد وضع التشغيل
    print("\nاختر وضع التشغيل:")
    print("1. الوضع التفاعلي (قائمة)")
    print("2. الإعداد التلقائي (تشغيل جميع عمليات الإعداد)")
    
    try:
        mode = input("\nاختر الوضع (1/2): ")
        
        if mode == '1':
            menu_loop()
        elif mode == '2':
            run_system_check()
        else:
            print("\nاختيار غير صالح. تشغيل الإعداد التلقائي كوضع افتراضي...")
            run_system_check()
    
    except KeyboardInterrupt:
        print("\n\nتم إلغاء العملية. الخروج...")
    
    print("\nشكرًا لاستخدام أداة إعداد نظام تقييم BTEC!")

if __name__ == "__main__":
    main()