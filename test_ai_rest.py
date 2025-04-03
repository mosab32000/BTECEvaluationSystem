#!/usr/bin/env python
"""
برنامج اختبار لواجهة REST API لخدمة الذكاء الاصطناعي المباشرة
"""

import os
import json
import logging
# التعامل مع الحالات التي لا تتوفر فيها مكتبة dotenv
try:
    from dotenv import load_dotenv
except ImportError:
    # في حالة عدم وجود المكتبة، نقوم بتعريف دالة فارغة
    def load_dotenv():
        pass
    print("تحذير: لم يتم العثور على مكتبة dotenv. تجاهل تحميل ملف .env")

from backend.app.services.ai_service_rest import AIEvaluatorREST

# إعداد السجل
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# تحميل متغيرات البيئة من ملف .env
load_dotenv()

def test_basic_evaluation():
    """اختبار التقييم الأساسي"""
    logger.info("اختبار التقييم الأساسي باستخدام REST API...")
    
    # إنشاء مثيل من خدمة التقييم
    api_key = os.environ.get('OPENAI_API_KEY')
    evaluator = AIEvaluatorREST(api_key=api_key)
    
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
    
    # إجراء التقييم
    result = evaluator.evaluate(sample_submission)
    logger.info(f"نتيجة التقييم الأساسي (REST):\n{result}\n")
    
    return result

def test_json_evaluation():
    """اختبار التقييم بتنسيق JSON"""
    logger.info("اختبار التقييم بتنسيق JSON باستخدام REST API...")
    
    # إنشاء مثيل من خدمة التقييم
    api_key = os.environ.get('OPENAI_API_KEY')
    evaluator = AIEvaluatorREST(api_key=api_key)
    
    # نص المهمة للتقييم (استخدام نفس النص السابق)
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
    
    # إجراء التقييم
    result = evaluator.evaluate_with_json(sample_submission)
    logger.info(f"نتيجة التقييم بتنسيق JSON (REST):\n{json.dumps(result, indent=2, ensure_ascii=False)}\n")
    
    return result

def test_rubric_evaluation():
    """اختبار التقييم باستخدام معيار تقييم"""
    logger.info("اختبار التقييم باستخدام معيار تقييم (REST)...")
    
    # إنشاء مثيل من خدمة التقييم
    api_key = os.environ.get('OPENAI_API_KEY')
    evaluator = AIEvaluatorREST(api_key=api_key)
    
    # نص المهمة للتقييم (استخدام نفس النص السابق)
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
    
    # معيار تقييم مخصص
    custom_rubric = {
        "sections": [
            {
                "name": "Research Design",
                "weight": 30,
                "criteria": ["Appropriateness of methods", "Sample size", "Data collection approach"]
            },
            {
                "name": "Budget Planning",
                "weight": 20,
                "criteria": ["Cost breakdown", "Reasonableness", "Completeness"]
            },
            {
                "name": "Timeline",
                "weight": 20,
                "criteria": ["Feasibility", "Sequencing", "Completeness"]
            },
            {
                "name": "Expected Outcomes",
                "weight": 30,
                "criteria": ["Clarity", "Relevance to business objectives", "Practicality"]
            }
        ]
    }
    
    # إجراء التقييم
    result = evaluator.evaluate_with_rubric(sample_submission, custom_rubric)
    logger.info(f"نتيجة التقييم باستخدام معيار تقييم (REST):\n{json.dumps(result, indent=2, ensure_ascii=False)}\n")
    
    return result

def main():
    """الدالة الرئيسية لاختبار خدمات الذكاء الاصطناعي المباشرة"""
    logger.info("بدء اختبار خدمات الذكاء الاصطناعي باستخدام REST API...")
    
    # التحقق من وجود مفتاح API
    api_key = os.environ.get('OPENAI_API_KEY')
    if not api_key:
        logger.warning("تحذير: لم يتم العثور على OPENAI_API_KEY في متغيرات البيئة. سيتم استخدام وضع المحاكاة.")
    
    # اختبار الطرق المختلفة
    try:
        # اختبار التقييم الأساسي
        test_basic_evaluation()
    except Exception as e:
        logger.error(f"فشل اختبار التقييم الأساسي: {e}")
    
    try:
        # اختبار التقييم بتنسيق JSON
        test_json_evaluation()
    except Exception as e:
        logger.error(f"فشل اختبار التقييم بتنسيق JSON: {e}")
    
    try:
        # اختبار التقييم باستخدام معيار تقييم
        test_rubric_evaluation()
    except Exception as e:
        logger.error(f"فشل اختبار التقييم باستخدام معيار تقييم: {e}")
    
    logger.info("اكتمل اختبار خدمات الذكاء الاصطناعي باستخدام REST API.")

if __name__ == "__main__":
    main()