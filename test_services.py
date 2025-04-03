"""
برنامج اختبار لخدمات الذكاء الاصطناعي المتقدمة في نظام تقييم BTEC
"""

import os
import logging
import json
from backend.app.services.ai_service_rest import AIEvaluatorREST
from backend.app.services.ai_service_arabic import AIEvaluatorArabic
from backend.app.services.ai_service_multimodal import AIEvaluatorMultimodal
from backend.app.services.ai_service_advanced import AIEvaluatorAdvanced

# تكوين التسجيل
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ملاحظة: تم حذف تحميل متغيرات البيئة هنا لأنه يتم تحميلها تلقائيًا في الخدمات

def test_rest_api():
    """اختبار AIEvaluatorREST"""
    logger.info("اختبار AIEvaluatorREST...")
    
    evaluator = AIEvaluatorREST()
    task = """
    قم بتحليل مفهوم الخوارزميات الوراثية وشرح كيفية استخدامها في حل مشاكل التحسين المعقدة.
    يجب أن يتضمن التحليل:
    1. تعريف الخوارزميات الوراثية ومبادئها الأساسية
    2. مقارنة مع طرق التحسين التقليدية
    3. مثال عملي على استخدام الخوارزميات الوراثية في حل مشكلة حقيقية
    """
    
    result = evaluator.evaluate(task)
    logger.info("نتيجة التقييم:")
    logger.info(result[:200] + "..." if len(result) > 200 else result)
    
    return result

def test_arabic_evaluator():
    """اختبار AIEvaluatorArabic"""
    logger.info("اختبار AIEvaluatorArabic...")
    
    evaluator = AIEvaluatorArabic()
    task = """
    قم بتحليل وتقييم الأثر الاقتصادي للثورة الصناعية الرابعة على سوق العمل العربي،
    مع التركيز على التحديات والفرص المتاحة للمهنيين الشباب في مجالات التكنولوجيا المتقدمة.
    قدم أمثلة واقعية واقتراحات للتعامل مع هذه التغييرات.
    """
    
    result = evaluator.evaluate_arabic(task)
    logger.info("نتيجة التقييم:")
    logger.info(result[:200] + "..." if len(result) > 200 else result)
    
    return result

def test_advanced_evaluator():
    """اختبار AIEvaluatorAdvanced"""
    logger.info("اختبار AIEvaluatorAdvanced...")
    
    evaluator = AIEvaluatorAdvanced()
    task = """
    قم بتصميم نظام مراقبة بيئية باستخدام إنترنت الأشياء (IoT) لمراقبة جودة الهواء في المناطق الحضرية. 
    يجب أن يتضمن التصميم:
    1. هيكل النظام والمكونات المادية المطلوبة
    2. نوع البيانات التي سيتم جمعها وكيفية معالجتها
    3. واجهة المستخدم وطرق عرض البيانات
    4. تحليل للتكلفة والفوائد البيئية المتوقعة
    """
    
    criteria = {
        "sections": [
            {
                "name": "التصميم التقني",
                "weight": 30,
                "criteria": ["شمولية التصميم", "اختيار المكونات المناسبة", "قابلية التوسع"]
            },
            {
                "name": "معالجة البيانات",
                "weight": 25,
                "criteria": ["أساليب الجمع", "طرق التحليل", "أمن البيانات"]
            },
            {
                "name": "واجهة المستخدم",
                "weight": 20,
                "criteria": ["سهولة الاستخدام", "تصور البيانات", "تجربة المستخدم"]
            },
            {
                "name": "الجدوى والاستدامة",
                "weight": 25,
                "criteria": ["تحليل التكلفة", "الآثار البيئية", "قابلية التنفيذ"]
            }
        ]
    }
    
    result = evaluator.evaluate_with_detailed_feedback(task, criteria)
    logger.info("نتيجة التقييم:")
    logger.info(str(result)[:500] + "..." if len(str(result)) > 500 else str(result))
    
    return result

def run_tests():
    """تشغيل جميع الاختبارات"""
    try:
        logger.info("بدء اختبار خدمات الذكاء الاصطناعي المتقدمة...")
        
        # اختبار AIEvaluatorREST
        rest_result = test_rest_api()
        
        # اختبار AIEvaluatorArabic
        arabic_result = test_arabic_evaluator()
        
        # اختبار AIEvaluatorAdvanced
        advanced_result = test_advanced_evaluator()
        
        logger.info("تم إكمال جميع الاختبارات بنجاح.")
        return True
    except Exception as e:
        logger.error(f"حدث خطأ أثناء الاختبار: {e}")
        return False
        
if __name__ == "__main__":
    success = run_tests()
    if success:
        logger.info("تم إكمال جميع الاختبارات بنجاح.")
    else:
        logger.error("فشل في إكمال الاختبارات.")