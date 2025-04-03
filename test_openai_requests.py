#!/usr/bin/env python
"""
برنامج اختبار لواجهة OpenAI API باستخدام طلبات REST API مباشرة
"""

import os
import json
import logging
import requests
from dotenv import load_dotenv

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
    
    logger.info("بدء اختبار بسيط لواجهة OpenAI API باستخدام REST API مباشرة...")
    
    api_url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "gpt-3.5-turbo",
        "messages": [
            {"role": "system", "content": "أنت مساعد مفيد."},
            {"role": "user", "content": "ما هو نظام تقييم BTEC؟"}
        ],
        "max_tokens": 100,
        "temperature": 0.7
    }
    
    try:
        response = requests.post(api_url, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        
        result = response.json()
        logger.info("تم الاتصال بـ OpenAI API بنجاح!")
        
        message_content = result['choices'][0]['message']['content']
        logger.info(f"الرد:\n{message_content}")
        
        return message_content
    except requests.exceptions.HTTPError as e:
        logger.error(f"خطأ HTTP: {e}")
        if hasattr(e, 'response') and e.response is not None:
            try:
                error_data = e.response.json()
                logger.error(f"تفاصيل الخطأ من OpenAI: {json.dumps(error_data, indent=2, ensure_ascii=False)}")
            except:
                logger.error(f"نص الاستجابة: {e.response.text}")
    except Exception as e:
        logger.error(f"حدث خطأ أثناء الاتصال بـ OpenAI API: {e}")
    
    return None

if __name__ == "__main__":
    result = test_simple_completion()
    if result:
        logger.info("تم إكمال الاختبار البسيط بنجاح!")
    else:
        logger.error("فشل الاختبار البسيط!")