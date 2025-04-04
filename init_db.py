"""
هذا البرنامج يقوم بإنشاء قواعد البيانات المطلوبة لنظام تقييم BTEC
"""
import base64
import json
import logging
import os
import re
import secrets
import sys
from datetime import datetime

from cryptography.fernet import Fernet
from werkzeug.security import generate_password_hash

from app import create_app, db
from app.models.user import User
from app.models.evaluation import Course
from app.models.rubric import RubricTemplate
from app.core.security import generate_secure_password
from dotenv import load_dotenv

# إعداد التسجيل
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

def ensure_encryption_key():
    """التأكد من وجود مفتاح التشفير، وإنشاء واحد جديد إذا لم يكن موجودًا"""
    try:
        if not os.environ.get('DATA_ENCRYPTION_KEY'):
            key = Fernet.generate_key()
            with open('.env', 'a+') as f:
                f.seek(0)  # الذهاب إلى بداية الملف للقراءة
                content = f.read()
                
                # التحقق مما إذا كان المفتاح موجودًا بالفعل
                if not re.search(r'^DATA_ENCRYPTION_KEY=', content, re.MULTILINE):
                    # إذا لم يكن الملف فارغًا ولا ينتهي بسطر جديد، أضف سطر جديد
                    if content and not content.endswith('\n'):
                        f.write('\n')
                    
                    f.write(f"DATA_ENCRYPTION_KEY={key.decode('utf-8')}\n")
                    logger.info("Generated and stored new DATA_ENCRYPTION_KEY")
    except Exception as e:
        logger.error(f"Error ensuring encryption key: {e}")

def ensure_secret_key(env_var, length=32):
    """التأكد من وجود مفتاح سري، وإنشاء واحد جديد إذا لم يكن موجودًا"""
    try:
        if not os.environ.get(env_var):
            # Generate a random key
            key = secrets.token_hex(length)
            
            # Save to .env file
            with open('.env', 'a+') as f:
                f.seek(0)  # الذهاب إلى بداية الملف للقراءة
                content = f.read()
                
                # التحقق مما إذا كان المفتاح موجودًا بالفعل
                if not re.search(f'^{env_var}=', content, re.MULTILINE):
                    # إذا لم يكن الملف فارغًا ولا ينتهي بسطر جديد، أضف سطر جديد
                    if content and not content.endswith('\n'):
                        f.write('\n')
                    
                    f.write(f"{env_var}={key}\n")
                    logger.info(f"Generated and stored new {env_var}")
    except Exception as e:
        logger.error(f"Error ensuring {env_var}: {e}")

def create_default_admin():
    """إنشاء حساب مسؤول افتراضي إذا لم يكن موجودًا"""
    try:
        # التحقق مما إذا كان يوجد مستخدم مسؤول بالفعل
        admin = User.query.filter_by(role='admin').first()
        
        if admin:
            logger.info(f"Admin user exists: {admin.email}")
            return
        
        # إنشاء حساب مسؤول جديد
        admin_email = os.environ.get('ADMIN_EMAIL', 'admin@btec.edu')
        admin_password = os.environ.get('ADMIN_PASSWORD')
        
        if not admin_password:
            admin_password = generate_secure_password(length=12)
            logger.info(f"Generated admin password: {admin_password}")
        
        admin = User(
            email=admin_email,
            name='مسؤول النظام',
            role='admin',
            is_active=True,
            is_verified=True,
            institution='BTEC',
            position='مسؤول النظام',
            created_at=datetime.utcnow()
        )
        admin.password_hash = generate_password_hash(admin_password)
        
        db.session.add(admin)
        db.session.commit()
        
        logger.info(f"Created default admin user: {admin_email}")
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error creating default admin: {e}")

def create_default_rubrics():
    """إنشاء قوالب معايير تقييم افتراضية"""
    try:
        # التحقق مما إذا كان يوجد قالب افتراضي بالفعل
        default_rubric = RubricTemplate.query.filter_by(is_default=True).first()
        
        if default_rubric:
            logger.info(f"Default rubric exists: {default_rubric.name}")
            return
        
        # إنشاء قالب تقييم BTEC الأساسي
        basic_criteria = [
            {
                'name': 'المعرفة والفهم',
                'description': 'مدى فهم المفاهيم الأساسية والنظريات المتعلقة بالموضوع',
                'weight': 30
            },
            {
                'name': 'التطبيق العملي',
                'description': 'القدرة على تطبيق المعرفة النظرية في مواقف عملية',
                'weight': 30
            },
            {
                'name': 'المهارات التحليلية',
                'description': 'القدرة على تحليل المعلومات واستخلاص النتائج',
                'weight': 20
            },
            {
                'name': 'الإبداع والابتكار',
                'description': 'تقديم أفكار جديدة ومبتكرة وحلول إبداعية',
                'weight': 10
            },
            {
                'name': 'العرض والتنظيم',
                'description': 'تنظيم وعرض الأفكار والمعلومات بشكل منطقي وواضح',
                'weight': 10
            }
        ]
        
        basic_rubric = RubricTemplate(
            name='نموذج تقييم BTEC الأساسي',
            description='نموذج تقييم أساسي لمهام BTEC يتضمن المعايير الرئيسية',
            is_default=True,
            created_at=datetime.utcnow()
        )
        basic_rubric.set_criteria(basic_criteria)
        
        # إنشاء قالب تقييم BTEC المتقدم
        advanced_criteria = [
            {
                'name': 'الفهم المفاهيمي',
                'description': 'فهم عميق للمفاهيم والنظريات الأساسية وتطبيقاتها',
                'weight': 20
            },
            {
                'name': 'البحث والاستقصاء',
                'description': 'جمع البيانات والمعلومات من مصادر متنوعة وموثوقة',
                'weight': 15
            },
            {
                'name': 'التحليل النقدي',
                'description': 'تقييم المعلومات والحجج بشكل نقدي واستخلاص استنتاجات منطقية',
                'weight': 15
            },
            {
                'name': 'حل المشكلات',
                'description': 'تطبيق المعرفة والمهارات في حل مشكلات معقدة',
                'weight': 15
            },
            {
                'name': 'الابتكار والإبداع',
                'description': 'تطوير حلول وأفكار مبتكرة وأصلية',
                'weight': 10
            },
            {
                'name': 'التنفيذ العملي',
                'description': 'تنفيذ المشروع بكفاءة وفعالية وفقًا للمتطلبات',
                'weight': 10
            },
            {
                'name': 'العرض والتواصل',
                'description': 'عرض النتائج والأفكار بشكل واضح ومنظم وجذاب',
                'weight': 10
            },
            {
                'name': 'الإدارة والتنظيم',
                'description': 'إدارة الوقت والموارد بفعالية وتنظيم العمل بشكل منهجي',
                'weight': 5
            }
        ]
        
        advanced_rubric = RubricTemplate(
            name='نموذج تقييم BTEC المتقدم',
            description='نموذج تقييم متقدم لمهام BTEC يتضمن معايير تفصيلية',
            is_default=False,
            created_at=datetime.utcnow()
        )
        advanced_rubric.set_criteria(advanced_criteria)
        
        # إنشاء قالب تقييم المشاريع التقنية
        tech_criteria = [
            {
                'name': 'التصميم التقني',
                'description': 'جودة وكفاءة التصميم التقني للمشروع',
                'weight': 25
            },
            {
                'name': 'التنفيذ والتطوير',
                'description': 'جودة التنفيذ والترميز والتطوير',
                'weight': 25
            },
            {
                'name': 'الأمان والموثوقية',
                'description': 'مستوى الأمان والموثوقية والمتانة',
                'weight': 15
            },
            {
                'name': 'قابلية الاستخدام',
                'description': 'سهولة الاستخدام وتجربة المستخدم',
                'weight': 15
            },
            {
                'name': 'التوثيق',
                'description': 'جودة واكتمال التوثيق التقني',
                'weight': 10
            },
            {
                'name': 'الاختبار والتحقق',
                'description': 'شمولية وفعالية اختبارات المشروع',
                'weight': 10
            }
        ]
        
        tech_rubric = RubricTemplate(
            name='نموذج تقييم المشاريع التقنية',
            description='نموذج تقييم خاص بالمشاريع التقنية والبرمجية',
            is_default=False,
            created_at=datetime.utcnow()
        )
        tech_rubric.set_criteria(tech_criteria)
        
        # حفظ جميع القوالب
        db.session.add(basic_rubric)
        db.session.add(advanced_rubric)
        db.session.add(tech_rubric)
        db.session.commit()
        
        logger.info("Created default rubric templates")
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error creating default rubrics: {e}")

def create_default_courses():
    """إنشاء مساقات افتراضية"""
    try:
        # التحقق مما إذا كانت هناك مساقات موجودة بالفعل
        if Course.query.count() > 0:
            logger.info("Default courses already exist")
            return
        
        # إنشاء مساقات افتراضية
        courses = [
            {
                'code': 'BTEC101',
                'name': 'مقدمة في تقنية المعلومات',
                'description': 'مساق تمهيدي يغطي المفاهيم الأساسية في تقنية المعلومات',
                'institution': 'كلية BTEC',
                'level': 'المستوى 3',
                'credits': 15
            },
            {
                'code': 'BTEC201',
                'name': 'تطوير تطبيقات الويب',
                'description': 'تعلم أساسيات تطوير مواقع وتطبيقات الويب باستخدام HTML, CSS, وJavaScript',
                'institution': 'كلية BTEC',
                'level': 'المستوى 4',
                'credits': 20
            },
            {
                'code': 'BTEC301',
                'name': 'قواعد البيانات وإدارة المعلومات',
                'description': 'تصميم وتطوير وإدارة قواعد البيانات وأنظمة استرجاع المعلومات',
                'institution': 'كلية BTEC',
                'level': 'المستوى 4',
                'credits': 20
            },
            {
                'code': 'BTEC401',
                'name': 'أمن المعلومات والشبكات',
                'description': 'مبادئ وتقنيات أمن المعلومات وحماية الشبكات',
                'institution': 'كلية BTEC',
                'level': 'المستوى 5',
                'credits': 25
            },
            {
                'code': 'BTEC501',
                'name': 'مشروع تقني متكامل',
                'description': 'تطبيق المهارات والمعارف المكتسبة في مشروع تقني شامل',
                'institution': 'كلية BTEC',
                'level': 'المستوى 5',
                'credits': 30
            }
        ]
        
        for course_data in courses:
            course = Course(**course_data)
            db.session.add(course)
        
        db.session.commit()
        logger.info(f"Created {len(courses)} default courses")
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error creating default courses: {e}")

def setup_database():
    """إعداد وتهيئة قاعدة البيانات بالكامل"""
    # تحميل المتغيرات البيئية
    load_dotenv()
    
    # التأكد من وجود المفاتيح السرية
    ensure_secret_key('SECRET_KEY')
    ensure_secret_key('JWT_SECRET_KEY')
    ensure_encryption_key()
    
    # إنشاء تطبيق Flask وسياق التطبيق
    app = create_app()
    
    with app.app_context():
        # إنشاء جميع الجداول
        logger.info("Creating database tables...")
        db.create_all()
        
        # إنشاء البيانات الافتراضية
        logger.info("Creating default admin user...")
        create_default_admin()
        
        logger.info("Creating default rubric templates...")
        create_default_rubrics()
        
        logger.info("Creating default courses...")
        create_default_courses()
        
        logger.info("Database setup completed successfully!")

if __name__ == '__main__':
    setup_database()