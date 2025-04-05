#!/usr/bin/env python
"""
سكريبت تشغيل منصة مُدقِّق لتدقيق المشاريع
"""

import os
import sys
import logging
from app import create_app, db
from app.models import User, Role, Project, AuditCriteria, AuditResult, Notification, ActivityLog

# إنشاء التطبيق
app = create_app()

# إعداد التسجيل
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('mudaqqiq.log')
    ]
)

def init_roles():
    """تهيئة الأدوار الأساسية في النظام"""
    roles = {
        'user': 'مستخدم عادي',
        'auditor': 'مدقق مشاريع',
        'admin': 'مدير نظام'
    }
    
    for role_name, description in roles.items():
        role = Role.query.filter_by(name=role_name).first()
        if not role:
            role = Role(name=role_name, description=description)
            db.session.add(role)
            logging.info(f'تم إنشاء دور جديد: {role_name}')
    
    db.session.commit()

def init_admin_user():
    """إنشاء حساب مدير النظام الافتراضي إذا لم يكن موجوداً"""
    admin_email = os.environ.get('ADMIN_EMAIL', 'admin@mudaqqiq.com')
    admin = User.query.filter_by(email=admin_email).first()
    
    if not admin:
        admin_role = Role.query.filter_by(name='admin').first()
        admin = User(
            username='admin',
            email=admin_email,
            full_name='مدير النظام',
            is_active=True
        )
        admin.password = 'Admin123456'
        if admin_role:
            admin.roles.append(admin_role)
        
        db.session.add(admin)
        db.session.commit()
        logging.info(f'تم إنشاء حساب مدير النظام: {admin_email}')

def init_audit_criteria():
    """إنشاء معايير التدقيق الأساسية إذا لم تكن موجودة"""
    default_criteria = [
        {
            'name': 'التوثيق',
            'description': 'مدى شمولية ودقة توثيق المشروع، بما في ذلك التعليقات البرمجية ودليل المستخدم والتوثيق الفني.',
            'category': 'التوثيق',
            'weight': 1.0
        },
        {
            'name': 'جودة الكود',
            'description': 'جودة الكود البرمجي من حيث التنظيم والقراءة والاتساق واتباع المعايير البرمجية.',
            'category': 'الأداء',
            'weight': 1.5
        },
        {
            'name': 'تغطية الاختبارات',
            'description': 'مدى تغطية الاختبارات للوظائف المختلفة في المشروع وجودة هذه الاختبارات.',
            'category': 'الأداء',
            'weight': 1.2
        },
        {
            'name': 'الأمان',
            'description': 'مستوى الأمان في المشروع ومدى تطبيق إجراءات الأمان المناسبة.',
            'category': 'الأمان',
            'weight': 2.0
        },
        {
            'name': 'الأداء والكفاءة',
            'description': 'أداء المشروع وكفاءته في استخدام الموارد والاستجابة للطلبات.',
            'category': 'الأداء',
            'weight': 1.2
        },
        {
            'name': 'واجهة المستخدم',
            'description': 'جودة تصميم واجهة المستخدم وسهولة الاستخدام والتفاعل.',
            'category': 'سهولة الاستخدام',
            'weight': 1.0
        },
        {
            'name': 'تلبية المتطلبات',
            'description': 'مدى تلبية المشروع للمتطلبات المحددة واكتمال الوظائف المطلوبة.',
            'category': 'المتطلبات',
            'weight': 1.8
        },
        {
            'name': 'قابلية التوسع',
            'description': 'مدى قابلية المشروع للتوسع والتعديل وإضافة ميزات جديدة في المستقبل.',
            'category': 'الأداء',
            'weight': 1.0
        }
    ]
    
    for criteria_data in default_criteria:
        criteria = AuditCriteria.query.filter_by(name=criteria_data['name']).first()
        if not criteria:
            criteria = AuditCriteria(
                name=criteria_data['name'],
                description=criteria_data['description'],
                category=criteria_data['category'],
                weight=criteria_data['weight']
            )
            db.session.add(criteria)
            logging.info(f"تم إنشاء معيار تدقيق جديد: {criteria_data['name']}")
    
    db.session.commit()

def init_database():
    """تهيئة قاعدة البيانات بالبيانات الأساسية"""
    with app.app_context():
        # إنشاء الجداول إذا لم تكن موجودة
        db.create_all()
        
        # تهيئة البيانات الأساسية
        init_roles()
        init_admin_user()
        init_audit_criteria()
        
        logging.info('تم تهيئة قاعدة البيانات بنجاح')

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'init':
        # تهيئة قاعدة البيانات فقط
        init_database()
    else:
        # تهيئة قاعدة البيانات وتشغيل التطبيق
        init_database()
        app.run(host='0.0.0.0', port=5000, debug=True)
