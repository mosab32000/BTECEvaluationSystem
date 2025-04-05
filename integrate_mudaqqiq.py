#!/usr/bin/env python
"""
سكريبت دمج منصة مُدقِّق مع نظام تقييم BTEC
"""

import os
import sys
import logging
import importlib.util
from shutil import copyfile

# إعداد التسجيل
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('integration.log')
    ]
)

logger = logging.getLogger(__name__)

def load_app_init():
    """تحميل ملف __init__.py من مجلد app لتسجيل مخطط التكامل"""
    try:
        # محاولة استيراد ملف app/__init__.py
        app_init_path = "app/__init__.py"
        if not os.path.exists(app_init_path):
            logger.error(f"ملف {app_init_path} غير موجود")
            return None
        
        # استيراد الملف
        spec = importlib.util.spec_from_file_location("app_init", app_init_path)
        if spec is None or spec.loader is None:
            logger.error(f"فشل في تحميل ملف {app_init_path}")
            return None
        
        app_init = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(app_init)
        
        logger.info(f"تم تحميل ملف {app_init_path} بنجاح")
        return app_init
    except Exception as e:
        logger.error(f"حدث خطأ أثناء محاولة تحميل ملف app/__init__.py: {str(e)}")
        return None

def add_mudaqqiq_route():
    """إضافة مسار للوصول إلى منصة مُدقِّق في ملف app/routes/main.py"""
    try:
        routes_file = "app/routes/main.py"
        
        # التحقق من وجود الملف
        if not os.path.exists(routes_file):
            logger.error(f"ملف {routes_file} غير موجود")
            return False
        
        # قراءة محتوى الملف
        with open(routes_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # التحقق مما إذا تم إضافة المسار بالفعل
        if "mudaqqiq = Blueprint" in content:
            logger.info("تم إضافة مسار مُدقِّق بالفعل")
            return True
        
        # إنشاء نسخة احتياطية من الملف
        backup_file = f"{routes_file}.bak"
        copyfile(routes_file, backup_file)
        logger.info(f"تم إنشاء نسخة احتياطية من الملف في {backup_file}")
        
        # الكود الذي سيتم إضافته
        mudaqqiq_code = """
# مسار للوصول إلى منصة مُدقِّق
@main.route('/mudaqqiq')
def mudaqqiq_redirect():
    \"\"\"إعادة توجيه إلى منصة مُدقِّق\"\"\"
    return redirect(url_for('btec_mudaqqiq.index'))
"""
        
        # إضافة الاستيراد إذا لم يكن موجودًا
        import_line = "from flask import Blueprint, render_template, redirect, url_for"
        if "from flask import Blueprint" in content and "redirect" not in content:
            content = content.replace("from flask import Blueprint", import_line)
        
        # إضافة الكود في نهاية الملف
        content += mudaqqiq_code
        
        # كتابة المحتوى المحدث
        with open(routes_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        logger.info(f"تم إضافة مسار مُدقِّق إلى ملف {routes_file} بنجاح")
        return True
    except Exception as e:
        logger.error(f"حدث خطأ أثناء إضافة مسار مُدقِّق: {str(e)}")
        return False

def update_app_init():
    """تحديث ملف app/__init__.py لتسجيل مخطط مُدقِّق"""
    try:
        app_init_file = "app/__init__.py"
        
        # التحقق من وجود الملف
        if not os.path.exists(app_init_file):
            logger.error(f"ملف {app_init_file} غير موجود")
            return False
        
        # قراءة محتوى الملف
        with open(app_init_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # التحقق مما إذا تم إضافة التسجيل بالفعل
        if "from btec_mudaqqiq_integration import register_mudaqqiq_integration" in content:
            logger.info("تم تسجيل مخطط مُدقِّق بالفعل")
            return True
        
        # إنشاء نسخة احتياطية من الملف
        backup_file = f"{app_init_file}.bak"
        copyfile(app_init_file, backup_file)
        logger.info(f"تم إنشاء نسخة احتياطية من الملف في {backup_file}")
        
        # البحث عن دالة create_app
        create_app_start = content.find("def create_app")
        if create_app_start == -1:
            logger.error("لم يتم العثور على دالة create_app في الملف")
            return False
        
        # البحث عن نهاية دالة create_app
        create_app_end = content.find("return app", create_app_start)
        if create_app_end == -1:
            logger.error("لم يتم العثور على نهاية دالة create_app في الملف")
            return False
        
        # الاستيراد الذي سيتم إضافته
        import_code = """
# استيراد وحدة التكامل مع منصة مُدقِّق
from btec_mudaqqiq_integration import register_mudaqqiq_integration
"""
        
        # الكود الذي سيتم إضافته قبل return app
        register_code = """
    # تسجيل مخطط تكامل مُدقِّق
    register_mudaqqiq_integration(app)
    """
        
        # إضافة الاستيراد في بداية الملف
        content = import_code + content
        
        # إضافة تسجيل المخطط قبل return app
        content = content[:create_app_end] + register_code + content[create_app_end:]
        
        # كتابة المحتوى المحدث
        with open(app_init_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        logger.info(f"تم تحديث ملف {app_init_file} لتسجيل مخطط مُدقِّق بنجاح")
        return True
    except Exception as e:
        logger.error(f"حدث خطأ أثناء تحديث ملف app/__init__.py: {str(e)}")
        return False

def add_navbar_link():
    """إضافة رابط منصة مُدقِّق إلى شريط التنقل"""
    try:
        # البحث عن قالب القاعدة
        base_template = "app/templates/base.html"
        if not os.path.exists(base_template):
            # البحث في مجلدات أخرى
            for root, dirs, files in os.walk("app/templates"):
                for file in files:
                    if file.lower() == "base.html" or file.lower() == "layout.html":
                        base_template = os.path.join(root, file)
                        break
        
        # التحقق من وجود الملف
        if not os.path.exists(base_template):
            logger.error("لم يتم العثور على قالب القاعدة")
            return False
        
        # قراءة محتوى الملف
        with open(base_template, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # التحقق مما إذا تم إضافة الرابط بالفعل
        if "منصة مُدقِّق" in content:
            logger.info("تم إضافة رابط مُدقِّق بالفعل")
            return True
        
        # إنشاء نسخة احتياطية من الملف
        backup_file = f"{base_template}.bak"
        copyfile(base_template, backup_file)
        logger.info(f"تم إنشاء نسخة احتياطية من الملف في {backup_file}")
        
        # البحث عن شريط التنقل
        navbar_start = content.find("<ul", content.find("nav"))
        if navbar_start == -1:
            logger.error("لم يتم العثور على شريط التنقل في القالب")
            return False
        
        navbar_end = content.find("</ul>", navbar_start)
        if navbar_end == -1:
            logger.error("لم يتم العثور على نهاية شريط التنقل في القالب")
            return False
        
        # رابط مُدقِّق الذي سيتم إضافته
        mudaqqiq_link = """
                <li class="nav-item">
                    <a class="nav-link" href="{{ url_for('btec_mudaqqiq.index') }}">
                        <i class="fas fa-check-circle"></i> منصة مُدقِّق
                    </a>
                </li>"""
        
        # إضافة الرابط قبل نهاية شريط التنقل
        content = content[:navbar_end] + mudaqqiq_link + content[navbar_end:]
        
        # كتابة المحتوى المحدث
        with open(base_template, 'w', encoding='utf-8') as f:
            f.write(content)
        
        logger.info(f"تم إضافة رابط مُدقِّق إلى شريط التنقل في {base_template} بنجاح")
        return True
    except Exception as e:
        logger.error(f"حدث خطأ أثناء إضافة رابط مُدقِّق إلى شريط التنقل: {str(e)}")
        return False

def create_static_placeholder():
    """إنشاء صورة توضيحية للوحة التحكم"""
    try:
        # التأكد من وجود مجلد الصور
        img_dir = "static/img"
        os.makedirs(img_dir, exist_ok=True)
        
        # إنشاء صورة بسيطة باستخدام كود HTML
        html_img = """<svg width="800" height="600" xmlns="http://www.w3.org/2000/svg">
  <rect width="800" height="600" fill="#f8f9fa"/>
  <rect x="50" y="50" width="700" height="100" rx="10" fill="#0d6efd"/>
  <text x="400" y="105" font-family="Arial" font-size="30" fill="white" text-anchor="middle">لوحة تحكم مُدقِّق</text>
  
  <rect x="50" y="170" width="220" height="150" rx="10" fill="#198754"/>
  <text x="160" y="230" font-family="Arial" font-size="50" fill="white" text-anchor="middle">48</text>
  <text x="160" y="280" font-family="Arial" font-size="20" fill="white" text-anchor="middle">مشروع مكتمل</text>
  
  <rect x="290" y="170" width="220" height="150" rx="10" fill="#ffc107"/>
  <text x="400" y="230" font-family="Arial" font-size="50" fill="#333" text-anchor="middle">23</text>
  <text x="400" y="280" font-family="Arial" font-size="20" fill="#333" text-anchor="middle">قيد الانتظار</text>
  
  <rect x="530" y="170" width="220" height="150" rx="10" fill="#0dcaf0"/>
  <text x="640" y="230" font-family="Arial" font-size="50" fill="white" text-anchor="middle">85</text>
  <text x="640" y="280" font-family="Arial" font-size="20" fill="white" text-anchor="middle">متوسط الدرجات</text>
  
  <rect x="50" y="340" width="700" height="200" rx="10" fill="white" stroke="#dee2e6" stroke-width="2"/>
  <text x="400" y="380" font-family="Arial" font-size="20" fill="#333" text-anchor="middle">آخر المشاريع المدققة</text>
  
  <line x1="50" y1="400" x2="750" y2="400" stroke="#dee2e6" stroke-width="2"/>
  
  <text x="100" y="430" font-family="Arial" font-size="16" fill="#333">مشروع تطبيق ويب</text>
  <text x="550" y="430" font-family="Arial" font-size="16" fill="#198754">92/100</text>
  
  <text x="100" y="460" font-family="Arial" font-size="16" fill="#333">مشروع قاعدة بيانات</text>
  <text x="550" y="460" font-family="Arial" font-size="16" fill="#198754">88/100</text>
  
  <text x="100" y="490" font-family="Arial" font-size="16" fill="#333">مشروع تطبيق جوال</text>
  <text x="550" y="490" font-family="Arial" font-size="16" fill="#198754">95/100</text>
</svg>"""
        
        # حفظ الصورة في ملف SVG
        dashboard_svg = os.path.join(img_dir, "dashboard.svg")
        with open(dashboard_svg, 'w', encoding='utf-8') as f:
            f.write(html_img)
        
        logger.info(f"تم إنشاء صورة توضيحية للوحة التحكم في {dashboard_svg}")
        
        # إنشاء رابط للصورة بتنسيق JPG
        dashboard_jpg = os.path.join(img_dir, "dashboard.jpg")
        with open(dashboard_jpg, 'w', encoding='utf-8') as f:
            f.write('<!-- صورة توضيحية -->')
        
        logger.info(f"تم إنشاء رابط للصورة بتنسيق JPG في {dashboard_jpg}")
        return True
    except Exception as e:
        logger.error(f"حدث خطأ أثناء إنشاء صورة توضيحية: {str(e)}")
        return False

def setup_integration():
    """إعداد التكامل بين نظام تقييم BTEC ومنصة مُدقِّق"""
    logger.info("بدء إعداد التكامل بين نظام تقييم BTEC ومنصة مُدقِّق")
    
    success = True
    
    # تحميل ملف app/__init__.py
    app_init = load_app_init()
    if app_init is None:
        success = False
    
    # إضافة مسار للوصول إلى منصة مُدقِّق
    if not add_mudaqqiq_route():
        success = False
    
    # تحديث ملف app/__init__.py
    if not update_app_init():
        success = False
    
    # إضافة رابط منصة مُدقِّق إلى شريط التنقل
    if not add_navbar_link():
        success = False
    
    # إنشاء صورة توضيحية للوحة التحكم
    if not create_static_placeholder():
        # هذا ليس ضروريًا للتكامل
        logger.warning("لم يتم إنشاء صورة توضيحية للوحة التحكم")
    
    if success:
        logger.info("تم إعداد التكامل بين نظام تقييم BTEC ومنصة مُدقِّق بنجاح")
        print("✅ تم إعداد التكامل بين نظام تقييم BTEC ومنصة مُدقِّق بنجاح")
        print("🚀 يمكنك الآن الوصول إلى منصة مُدقِّق من خلال الرابط في شريط التنقل")
    else:
        logger.error("فشل في إعداد بعض جوانب التكامل. يرجى مراجعة السجل للتفاصيل.")
        print("❌ حدث خطأ أثناء إعداد التكامل. يرجى مراجعة السجل للتفاصيل.")

if __name__ == "__main__":
    setup_integration()
