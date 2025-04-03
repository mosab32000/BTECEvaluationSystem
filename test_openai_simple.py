#!/usr/bin/env python
"""
برنامج اختبار مبسط لواجهة OpenAI API
"""

import os
import logging
import requests
import json
from dotenv import load_dotenv

# إعداد السجل
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# تحميل متغيرات البيئة من ملف .env
load_dotenv()

def test_simple_completion():
    """اختبار بسيط لإكمال النص باستخدام OpenAI API مباشرة عبر REST API"""
    api_key = os.environ.get('OPENAI_API_KEY')
    if not api_key:
        logger.error("لم يتم العثور على OPENAI_API_KEY في متغيرات البيئة.")
        return None
    
    logger.info("تهيئة الطلب المباشر إلى OpenAI API...")
    
    api_url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "gpt-4o",  # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
        # do not change this unless explicitly requested by the user
        "messages": [
            {"role": "system", "content": "أنت مساعد مفيد."},
            {"role": "user", "content": "قم بتقديم ثلاثة أمثلة على كيفية استخدام الذكاء الاصطناعي في التعليم."}
        ],
        "max_tokens": 500,
        "temperature": 0.7
    }
    
    logger.info("إرسال طلب إكمال نص بسيط...")
    try:
        response = requests.post(api_url, headers=headers, json=payload)
        response.raise_for_status()
        
        response_data = response.json()
        
        logger.info("تم استلام الرد من OpenAI API بنجاح.")
        content = response_data['choices'][0]['message']['content']
        logger.info(f"الرد:\n{content}")
        
        return content
    except Exception as e:
        logger.error(f"حدث خطأ أثناء استدعاء OpenAI API: {e}")
        if hasattr(e, 'response') and hasattr(e.response, 'text'):
            logger.error(f"رد API: {e.response.text}")
        return str(e)

if __name__ == "__main__":
    logger.info("بدء اختبار OpenAI API المبسط...")
    result = test_simple_completion()
    if result:
        logger.info("اكتمل اختبار OpenAI API المبسط بنجاح.")
    else:
        logger.error("فشل اختبار OpenAI API المبسط.")