"""
سكريبت تشغيل منصة مُدقِّق لتدقيق المشاريع كجزء من نظام تقييم BTEC
"""
import os
import sys
import logging
from flask import Flask, redirect, url_for, render_template

def get_mudaqqiq_app():
    """استيراد وتهيئة تطبيق مُدقِّق"""
    try:
        sys.path.append(os.path.abspath('mudaqqiq'))
        from mudaqqiq.app import create_app
        return create_app()
    except ImportError as e:
        logging.error(f"فشل استيراد تطبيق مُدقِّق: {str(e)}")
        return None

def create_integration_app():
    """إنشاء تطبيق للتكامل بين نظام BTEC ومنصة مُدقِّق"""
    mudaqqiq_app = get_mudaqqiq_app()
    
    if not mudaqqiq_app:
        # إنشاء تطبيق بسيط إذا لم يمكن تحميل تطبيق مُدقِّق
        app = Flask(__name__)
        
        @app.route('/')
        def index():
            """الصفحة الرئيسية للتطبيق المتكامل"""
            return render_template('mudaqqiq_error.html', 
                                   error_message="تعذر تحميل منصة مُدقِّق. يرجى التحقق من التثبيت.")
        
        @app.route('/static/<path:filename>')
        def mudaqqiq_static(filename):
            """خدمة الملفات الثابتة لمنصة مُدقِّق"""
            try:
                return redirect(url_for('static', filename=filename))
            except:
                return "الملف غير موجود", 404
        
        @app.errorhandler(404)
        def error_page():
            return "الصفحة غير موجودة", 404
        
        return app
    
    return mudaqqiq_app

def main():
    """تشغيل خادم منصة مُدقِّق"""
    # إعداد التسجيل
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('mudaqqiq_server.log')
        ]
    )
    
    logging.info("بدء تشغيل منصة مُدقِّق...")
    
    # تهيئة التطبيق
    app = create_integration_app()
    
    # تحديد منفذ التشغيل (افتراضيًا 5001)
    port = int(os.environ.get('MUDAQQIQ_PORT', 5001))
    
    # تشغيل الخادم
    app.run(host='0.0.0.0', port=port, debug=True)

if __name__ == '__main__':
    main()