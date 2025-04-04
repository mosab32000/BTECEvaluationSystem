"""
هذا البرنامج يقوم بإعداد نظام تقييم BTEC وفحص سلامة التطبيق
"""
import os
import sys
import logging
from datetime import datetime

# إعداد تسجيل الأحداث
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

def check_environment():
    """
    التحقق من المتغيرات البيئية الضرورية
    
    Returns:
        bool: ما إذا كانت جميع المتغيرات البيئية موجودة
    """
    required_vars = ['DATABASE_URL']
    optional_vars = ['SECRET_KEY', 'JWT_SECRET_KEY', 'ENCRYPTION_KEY', 'ADMIN_EMAIL', 'ADMIN_PASSWORD']
    
    all_required_present = True
    
    logger.info("فحص المتغيرات البيئية...")
    
    # التحقق من المتغيرات المطلوبة
    for var in required_vars:
        if var not in os.environ:
            logger.error(f"المتغير البيئي المطلوب غير موجود: {var}")
            all_required_present = False
    
    # التحقق من المتغيرات الاختيارية
    for var in optional_vars:
        if var not in os.environ:
            logger.warning(f"المتغير البيئي الاختياري غير موجود: {var}")
    
    return all_required_present

def generate_secret_key():
    """
    إنشاء مفتاح سري
    
    Returns:
        str: المفتاح السري
    """
    import secrets
    return secrets.token_hex(32)

def ensure_secret_keys():
    """
    التأكد من وجود المفاتيح السرية
    
    Returns:
        bool: ما إذا تم ضمان وجود المفاتيح السرية
    """
    from app.core.security import generate_encryption_key
    
    # التحقق من مفتاح SECRET_KEY
    if 'SECRET_KEY' not in os.environ:
        os.environ['SECRET_KEY'] = generate_secret_key()
        logger.info("تم إنشاء مفتاح SECRET_KEY جديد")
    
    # التحقق من مفتاح JWT_SECRET_KEY
    if 'JWT_SECRET_KEY' not in os.environ:
        os.environ['JWT_SECRET_KEY'] = generate_secret_key()
        logger.info("تم إنشاء مفتاح JWT_SECRET_KEY جديد")
    
    # التحقق من مفتاح ENCRYPTION_KEY
    if 'ENCRYPTION_KEY' not in os.environ:
        os.environ['ENCRYPTION_KEY'] = generate_encryption_key()
        logger.info("تم إنشاء مفتاح ENCRYPTION_KEY جديد")
    
    return True

def check_database():
    """
    التحقق من الاتصال بقاعدة البيانات
    
    Returns:
        bool: ما إذا تم الاتصال بقاعدة البيانات بنجاح
    """
    from app.database import check_database_connection
    
    logger.info("التحقق من الاتصال بقاعدة البيانات...")
    connected, error_message = check_database_connection()
    
    if connected:
        logger.info("تم الاتصال بقاعدة البيانات بنجاح")
        return True
    else:
        logger.error(f"فشل الاتصال بقاعدة البيانات: {error_message}")
        return False

def setup_database():
    """
    إنشاء جداول قاعدة البيانات
    
    Returns:
        bool: ما إذا تم إنشاء الجداول بنجاح
    """
    try:
        from app import create_app
        from app.models.user import User
        from app.models.evaluation import Evaluation
        from app.models.rubric import RubricTemplate
        
        logger.info("إنشاء تطبيق Flask...")
        app = create_app()
        
        with app.app_context():
            from app import db
            
            logger.info("إنشاء جداول قاعدة البيانات...")
            db.create_all()
            
            # التحقق من وجود جداول رئيسية
            table_checks = {
                'users': User.query.count(),
                'evaluations': Evaluation.query.count(),
                'rubric_templates': RubricTemplate.query.count()
            }
            
            for table, count in table_checks.items():
                logger.info(f"جدول {table}: {count} صفوف")
            
            return True
    except Exception as e:
        logger.error(f"فشل إعداد قاعدة البيانات: {str(e)}")
        return False

def create_admin_user():
    """
    إنشاء مستخدم مسؤول
    
    Returns:
        bool: ما إذا تم إنشاء المستخدم بنجاح
    """
    try:
        from app import create_app
        from app.models.user import User
        from werkzeug.security import generate_password_hash
        
        admin_email = os.environ.get('ADMIN_EMAIL', 'admin@btec-evaluation.com')
        admin_password = os.environ.get('ADMIN_PASSWORD', 'admin123')
        
        app = create_app()
        
        with app.app_context():
            from app import db
            
            # التحقق من وجود مستخدم مسؤول
            admin = User.query.filter_by(role='admin').first()
            
            if admin:
                logger.info(f"المستخدم المسؤول موجود بالفعل: {admin.email}")
                return True
            
            # إنشاء مستخدم مسؤول جديد
            logger.info(f"إنشاء مستخدم مسؤول جديد: {admin_email}")
            
            admin = User()
            admin.email = admin_email
            admin.password_hash = generate_password_hash(admin_password)
            admin.name = "مسؤول النظام"
            admin.role = "admin"
            admin.is_active = True
            admin.is_verified = True
            
            db.session.add(admin)
            db.session.commit()
            
            logger.info(f"تم إنشاء المستخدم المسؤول بنجاح: {admin.email}")
            return True
    except Exception as e:
        logger.error(f"فشل إنشاء المستخدم المسؤول: {str(e)}")
        return False

def create_default_rubrics():
    """
    إنشاء معايير تقييم افتراضية
    
    Returns:
        bool: ما إذا تم إنشاء المعايير بنجاح
    """
    try:
        from app import create_app
        from app.models.rubric import RubricTemplate
        
        app = create_app()
        
        with app.app_context():
            from app import db
            
            # التحقق من وجود معايير افتراضية
            default_rubric = RubricTemplate.query.filter_by(is_default=True).first()
            
            if default_rubric:
                logger.info(f"معايير التقييم الافتراضية موجودة بالفعل: {default_rubric.name}")
                return True
            
            # إنشاء معايير تقييم افتراضية
            logger.info("إنشاء معايير تقييم BTEC الافتراضية")
            
            default_rubric = RubricTemplate()
            default_rubric.name = "معايير تقييم BTEC الافتراضية"
            default_rubric.description = "معايير تقييم نظام BTEC القياسية"
            default_rubric.is_default = True
            
            # إعداد معايير التقييم
            criteria = [
                {
                    "name": "المعرفة والفهم",
                    "description": "إظهار المعرفة والفهم للمفاهيم والنظريات الرئيسية",
                    "weight": 25
                },
                {
                    "name": "التطبيق العملي",
                    "description": "تطبيق المعرفة والفهم في سياقات عملية",
                    "weight": 25
                },
                {
                    "name": "البحث والتحليل",
                    "description": "جمع المعلومات وتحليلها وتقييمها",
                    "weight": 20
                },
                {
                    "name": "التفكير النقدي",
                    "description": "تقييم المعلومات والأفكار بشكل نقدي",
                    "weight": 15
                },
                {
                    "name": "مهارات التواصل",
                    "description": "عرض المعلومات والأفكار بشكل فعال",
                    "weight": 15
                }
            ]
            
            default_rubric.set_criteria(criteria)
            
            db.session.add(default_rubric)
            db.session.commit()
            
            logger.info(f"تم إنشاء معايير التقييم الافتراضية بنجاح: {default_rubric.name}")
            return True
    except Exception as e:
        logger.error(f"فشل إنشاء معايير التقييم الافتراضية: {str(e)}")
        return False

def run_system_check():
    """
    تشغيل فحص شامل للنظام
    """
    logger.info("=" * 50)
    logger.info("بدء فحص نظام تقييم BTEC")
    logger.info("=" * 50)
    
    # فحص الوقت والتاريخ
    logger.info(f"الوقت الحالي: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # فحص المتغيرات البيئية
    env_ok = check_environment()
    logger.info(f"فحص المتغيرات البيئية: {'نجاح' if env_ok else 'فشل'}")
    
    # ضمان وجود المفاتيح السرية
    keys_ok = ensure_secret_keys()
    logger.info(f"ضمان وجود المفاتيح السرية: {'نجاح' if keys_ok else 'فشل'}")
    
    # فحص الاتصال بقاعدة البيانات
    db_ok = check_database()
    logger.info(f"الاتصال بقاعدة البيانات: {'نجاح' if db_ok else 'فشل'}")
    
    if not db_ok:
        logger.error("فشل الاتصال بقاعدة البيانات. لا يمكن متابعة الإعداد.")
        return False
    
    # إعداد قاعدة البيانات
    setup_ok = setup_database()
    logger.info(f"إعداد قاعدة البيانات: {'نجاح' if setup_ok else 'فشل'}")
    
    if not setup_ok:
        logger.error("فشل إعداد قاعدة البيانات. لا يمكن متابعة الإعداد.")
        return False
    
    # إنشاء مستخدم مسؤول
    admin_ok = create_admin_user()
    logger.info(f"إنشاء مستخدم مسؤول: {'نجاح' if admin_ok else 'فشل'}")
    
    # إنشاء معايير تقييم افتراضية
    rubrics_ok = create_default_rubrics()
    logger.info(f"إنشاء معايير تقييم افتراضية: {'نجاح' if rubrics_ok else 'فشل'}")
    
    # ملخص النتائج
    all_ok = env_ok and keys_ok and db_ok and setup_ok and admin_ok and rubrics_ok
    
    logger.info("=" * 50)
    logger.info(f"نتيجة فحص النظام: {'نجاح' if all_ok else 'فشل'}")
    logger.info("=" * 50)
    
    return all_ok

if __name__ == "__main__":
    run_system_check()