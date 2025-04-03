"""
اختبار بسيط لواجهة OpenAI API
"""

import os
from dotenv import load_dotenv
import openai
import sys

def test_openai():
    """اختبار بسيط للاتصال بـ OpenAI API"""
    
    # تحميل المتغيرات البيئية
    load_dotenv()
    
    # التحقق من وجود مفتاح API
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("OPENAI_API_KEY غير موجود في متغيرات البيئة")
        sys.exit(1)
    
    # طباعة قيمة للتشخيص (بدون كشف المفتاح كاملاً)
    print(f"OPENAI_API_KEY متوفر: {api_key[:4]}{'*' * 10}")
    
    try:
        # تعيين مفتاح API
        openai.api_key = api_key
        
        # اختبار بسيط لإكمال النص
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # نستخدم نموذج متاح في الإصدار القديم
            messages=[
                {"role": "system", "content": "أنت مساعد مفيد لتقييم مهام BTEC."},
                {"role": "user", "content": "قم بتقييم الجملة التالية: مرحبا بالعالم"}
            ],
            max_tokens=100
        )
        
        # طباعة الاستجابة
        print("OpenAI API استجابة:")
        print(response.choices[0].message.content)
        return True
        
    except Exception as e:
        print(f"حدث خطأ أثناء الاتصال بـ OpenAI API: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    test_openai()