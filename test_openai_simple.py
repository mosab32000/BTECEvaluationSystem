#!/usr/bin/env python
"""
برنامج اختبار مبسط لواجهة OpenAI API
"""

import os
import logging
import json
from dotenv import load_dotenv
from openai import OpenAI

# إعداد السجل
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# تحميل متغيرات البيئة
load_dotenv()

def test_simple_completion():
    """اختبار بسيط لإكمال النص باستخدام OpenAI API مباشرة عبر REST API"""
    
    # الحصول على مفتاح API
    api_key = os.environ.get('OPENAI_API_KEY')
    if not api_key:
        logger.error("لم يتم العثور على OPENAI_API_KEY في متغيرات البيئة.")
        return
    
    logger.info("بدء اختبار بسيط لواجهة OpenAI API...")
    
    try:
        # إنشاء عميل OpenAI API
        client = OpenAI(api_key=api_key)
        
        # إنشاء طلب بسيط
        response = client.chat.completions.create(
            model="gpt-3.5-turbo", # استخدام نموذج أقل تكلفة
            messages=[
                {"role": "system", "content": "أنت مساعد مفيد."},
                {"role": "user", "content": "ما هو نظام تقييم BTEC؟"}
            ],
            max_tokens=100,
            temperature=0.7
        )
        
        # عرض النتيجة
        logger.info("تم الاتصال بـ OpenAI API بنجاح!")
        message_content = response.choices[0].message.content
        logger.info(f"الرد:\n{message_content}")
        
        return message_content
    except Exception as e:
        # عرض تفاصيل الخطأ للتصحيح
        logger.error(f"حدث خطأ أثناء الاتصال بـ OpenAI API: {e}")
        logger.error(f"نوع الخطأ: {type(e).__name__}")
        
        if hasattr(e, "__dict__"):
            for attr_name in dir(e):
                if not attr_name.startswith("_"):
                    try:
                        attr_value = getattr(e, attr_name)
                        if not callable(attr_value):
                            logger.error(f"  {attr_name}: {attr_value}")
                    except:
                        pass
        
        return None

if __name__ == "__main__":
    result = test_simple_completion()
    if result:
        logger.info("تم إكمال الاختبار البسيط بنجاح!")
    else:
        logger.error("فشل الاختبار البسيط!")