
"""
اختبار بسيط لخدمة Google API في نظام تقييم BTEC
"""

import os
import logging
from dotenv import load_dotenv

# تهيئة التسجيل
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# تحميل متغيرات البيئة
load_dotenv()

# استيراد خدمة Google API
from app.services.google_api_service import GoogleAPIService

def test_translation():
    """اختبار خدمة الترجمة"""
    api_key = os.environ.get('GOOGLE_API_KEY')
    if not api_key:
        logger.error("لم يتم العثور على GOOGLE_API_KEY في متغيرات البيئة.")
        return
    
    service = GoogleAPIService(api_key=api_key)
    
    # اختبار ترجمة من الإنجليزية إلى العربية
    english_text = "Welcome to BTEC Evaluation System"
    logger.info(f"النص الإنجليزي: {english_text}")
    
    arabic_translation = service.translate_text(english_text, target_language='ar')
    logger.info(f"الترجمة العربية: {arabic_translation}")
    
    # اختبار ترجمة من العربية إلى الإنجليزية
    arabic_text = "مرحبا بكم في نظام تقييم BTEC"
    logger.info(f"النص العربي: {arabic_text}")
    
    english_translation = service.translate_text(arabic_text, target_language='en', source_language='ar')
    logger.info(f"الترجمة الإنجليزية: {english_translation}")
    
    return arabic_translation, english_translation

def test_language_detection():
    """اختبار خدمة اكتشاف اللغة"""
    api_key = os.environ.get('GOOGLE_API_KEY')
    if not api_key:
        logger.error("لم يتم العثور على GOOGLE_API_KEY في متغيرات البيئة.")
        return
    
    service = GoogleAPIService(api_key=api_key)
    
    # اختبار اكتشاف اللغة العربية
    arabic_text = "مرحبا بكم في نظام تقييم BTEC"
    detected_lang = service.detect_language(arabic_text)
    logger.info(f"اللغة المكتشفة للنص العربي: {detected_lang}")
    
    # اختبار اكتشاف اللغة الإنجليزية
    english_text = "Welcome to BTEC Evaluation System"
    detected_lang = service.detect_language(english_text)
    logger.info(f"اللغة المكتشفة للنص الإنجليزي: {detected_lang}")
    
    return detected_lang

if __name__ == "__main__":
    logger.info("بدء اختبار خدمة Google API...")
    test_translation()
    test_language_detection()
    logger.info("اكتمل اختبار خدمة Google API.")
