#!/usr/bin/env python
"""
اختبار مباشر لواجهة OpenAI API باستخدام طلبات REST API
"""

import os
import json
import logging
import requests
from dotenv import load_dotenv

# إعداد السجل
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# تحميل متغيرات البيئة من ملف .env
load_dotenv()

def test_direct_evaluation():
    """اختبار مباشر لتقييم مهمة BTEC باستخدام OpenAI API"""
    
    # الحصول على مفتاح API من المتغيرات البيئية
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        logger.error("لم يتم العثور على OPENAI_API_KEY في متغيرات البيئة.")
        return None
    
    logger.info("تهيئة الطلب المباشر إلى OpenAI API...")
    
    api_url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    # نص المهمة للتقييم
    sample_submission = """
    BTEC Level 3 Business Assignment: Market Research Plan for a New Product
    
    Introduction:
    This report presents a comprehensive market research plan for launching a new eco-friendly water bottle that is biodegradable and made from sustainable materials. The research aims to understand customer preferences, market trends, and competitive landscape.
    
    Methodology:
    I will employ both qualitative and quantitative research methods:
    - Online surveys targeting 500 potential customers
    - Focus groups with 20 participants from different demographics
    - Interviews with 5 industry experts
    - Analysis of market reports and competitor products
    
    Data Collection:
    The surveys will collect data on:
    - Price sensitivity (£15-£30 range)
    - Color preferences
    - Important features (durability, design, eco-friendliness)
    - Purchase intent
    
    Focus groups will explore deeper motivations and reactions to product prototypes.
    
    Analysis Plan:
    Data will be analyzed using statistical software to identify:
    - Market segments with highest potential
    - Optimal price points
    - Most valued features
    - Barriers to purchase
    
    Timeline:
    - Week 1-2: Survey design and distribution
    - Week 3: Focus groups and interviews
    - Week 4: Data analysis
    - Week 5: Final report preparation
    
    Budget:
    Total budget allocation: £2,500
    - Survey platform: £500
    - Focus group incentives: £800
    - Data analysis software: £400
    - Expert interview compensation: £500
    - Miscellaneous expenses: £300
    
    Expected Outcomes:
    This research will inform product development, marketing strategy, and pricing decisions. It will help identify the most promising customer segments and optimal product positioning.
    """
    
    # إعداد الطلب للحصول على تقييم BTEC
    payload = {
        "model": "gpt-4o",  # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
        # do not change this unless explicitly requested by the user
        "messages": [
            {"role": "system", "content": """You are a BTEC evaluator with expertise in UK vocational qualifications. 
             Grade submissions strictly as: Pass, Merit, or Distinction based on BTEC criteria.
             
             Follow these BTEC grading guidelines:
             - Pass: Basic understanding, meets minimum requirements, limited analysis
             - Merit: Good understanding, well-structured, some critical analysis, good application of theory
             - Distinction: Excellent understanding, comprehensive, insightful critical analysis, creative application of theory to practice
             
             Format your response EXACTLY as:
             
             GRADE: [Pass/Merit/Distinction]
             
             FEEDBACK:
             • [Key point 1]
             • [Key point 2]
             • [Key point 3]
             • [Key point 4]
             
             AREAS FOR IMPROVEMENT:
             • [Improvement 1]
             • [Improvement 2]
             • [Improvement 3]
             
             Ensure your feedback is specific, actionable, and aligned with BTEC standards."""},
            {"role": "user", "content": f"Evaluate the following BTEC task submission:\n\n{sample_submission}"}
        ],
        "max_tokens": 1500,
        "temperature": 0.7
    }
    
    logger.info("إرسال طلب تقييم مهمة BTEC...")
    try:
        response = requests.post(api_url, headers=headers, json=payload, timeout=60)
        response.raise_for_status()
        
        response_data = response.json()
        
        logger.info("تم استلام الرد من OpenAI API بنجاح.")
        content = response_data['choices'][0]['message']['content']
        logger.info(f"التقييم:\n{content}")
        
        return content
    except Exception as e:
        logger.error(f"حدث خطأ أثناء استدعاء OpenAI API: {e}")
        if hasattr(e, 'response') and hasattr(e.response, 'text'):
            logger.error(f"رد API: {e.response.text}")
        return str(e)

def test_json_evaluation():
    """اختبار مباشر لتقييم مهمة BTEC بتنسيق JSON باستخدام OpenAI API"""
    
    # الحصول على مفتاح API من المتغيرات البيئية
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        logger.error("لم يتم العثور على OPENAI_API_KEY في متغيرات البيئة.")
        return None
    
    logger.info("تهيئة الطلب المباشر إلى OpenAI API للحصول على تقييم JSON...")
    
    api_url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    # نص المهمة للتقييم (نفس النص السابق)
    sample_submission = """
    BTEC Level 3 Business Assignment: Market Research Plan for a New Product
    
    Introduction:
    This report presents a comprehensive market research plan for launching a new eco-friendly water bottle that is biodegradable and made from sustainable materials. The research aims to understand customer preferences, market trends, and competitive landscape.
    
    Methodology:
    I will employ both qualitative and quantitative research methods:
    - Online surveys targeting 500 potential customers
    - Focus groups with 20 participants from different demographics
    - Interviews with 5 industry experts
    - Analysis of market reports and competitor products
    
    Data Collection:
    The surveys will collect data on:
    - Price sensitivity (£15-£30 range)
    - Color preferences
    - Important features (durability, design, eco-friendliness)
    - Purchase intent
    
    Focus groups will explore deeper motivations and reactions to product prototypes.
    
    Analysis Plan:
    Data will be analyzed using statistical software to identify:
    - Market segments with highest potential
    - Optimal price points
    - Most valued features
    - Barriers to purchase
    
    Timeline:
    - Week 1-2: Survey design and distribution
    - Week 3: Focus groups and interviews
    - Week 4: Data analysis
    - Week 5: Final report preparation
    
    Budget:
    Total budget allocation: £2,500
    - Survey platform: £500
    - Focus group incentives: £800
    - Data analysis software: £400
    - Expert interview compensation: £500
    - Miscellaneous expenses: £300
    
    Expected Outcomes:
    This research will inform product development, marketing strategy, and pricing decisions. It will help identify the most promising customer segments and optimal product positioning.
    """
    
    payload = {
        "model": "gpt-4o",  # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
        # do not change this unless explicitly requested by the user
        "messages": [
            {"role": "system", "content": """You are a BTEC evaluator with expertise in UK vocational qualifications.
             Grade submissions strictly as: Pass, Merit, or Distinction based on BTEC criteria.
             
             Follow these BTEC grading guidelines:
             - Pass: Basic understanding, meets minimum requirements, limited analysis (50-59%)
             - Merit: Good understanding, well-structured, some critical analysis (60-79%)
             - Distinction: Excellent understanding, comprehensive, insightful analysis (80-100%)
             
             Return your evaluation in the following JSON format:
             {
               "grade": "Pass/Merit/Distinction",
               "feedback": ["Point 1", "Point 2", "Point 3", "Point 4"],
               "improvement_areas": ["Area 1", "Area 2", "Area 3"],
               "criteria_met": {
                 "knowledge": 0-100,
                 "application": 0-100,
                 "analysis": 0-100,
                 "evaluation": 0-100
               }
             }
             
             Ensure your feedback is specific, actionable, and aligned with BTEC standards.
             The percentages in criteria_met should reflect performance in each area from 0-100.
             """},
            {"role": "user", "content": f"Evaluate the following BTEC task submission:\n\n{sample_submission}"}
        ],
        "response_format": {"type": "json_object"},
        "max_tokens": 1500,
        "temperature": 0.7
    }
    
    logger.info("إرسال طلب تقييم JSON...")
    try:
        response = requests.post(api_url, headers=headers, json=payload, timeout=60)
        response.raise_for_status()
        
        response_data = response.json()
        
        logger.info("تم استلام الرد من OpenAI API بنجاح.")
        content = response_data['choices'][0]['message']['content']
        result = json.loads(content)
        logger.info(f"تقييم JSON:\n{json.dumps(result, indent=2, ensure_ascii=False)}")
        
        return result
    except Exception as e:
        logger.error(f"حدث خطأ أثناء استدعاء OpenAI API للحصول على تقييم JSON: {e}")
        if hasattr(e, 'response') and hasattr(e.response, 'text'):
            logger.error(f"رد API: {e.response.text}")
        return {"error": str(e)}

if __name__ == "__main__":
    logger.info("بدء اختبار خدمات الذكاء الاصطناعي المباشرة...")
    
    # التحقق من وجود مفتاح API
    api_key = os.environ.get('OPENAI_API_KEY')
    if not api_key:
        logger.warning("تحذير: لم يتم العثور على OPENAI_API_KEY في متغيرات البيئة.")
    
    # اختبار التقييم العادي
    test_direct_evaluation()
    
    # اختبار التقييم بتنسيق JSON
    test_json_evaluation()
    
    logger.info("اكتمل اختبار خدمات الذكاء الاصطناعي المباشرة.")