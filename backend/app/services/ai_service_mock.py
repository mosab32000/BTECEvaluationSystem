"""
خدمة الذكاء الاصطناعي المبسطة للاختبار
تستخدم هذه الخدمة لاختبار واجهة التطبيق بدون الحاجة إلى مفتاح OpenAI API
"""

import json
import logging
import time
from datetime import datetime

# إعداد التسجيل
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AIServiceMock:
    """واجهة مبسطة تحاكي خدمة الذكاء الاصطناعي للاختبار"""
    
    def __init__(self, api_key=None, model="gpt-3.5-turbo"):
        """تهيئة الخدمة المبسطة"""
        self.model = model
        self.api_key = api_key or "mock-api-key"
        logger.info(f"تم تهيئة خدمة الذكاء الاصطناعي المبسطة باستخدام النموذج: {model}")
    
    def evaluate_task(self, task_text, rubric=None):
        """
        تقييم مهمة BTEC باستخدام محاكاة الذكاء الاصطناعي
        
        المعلمات:
            task_text (str): نص المهمة المراد تقييمها
            rubric (dict, optional): معايير التقييم
            
        العائد:
            dict: نتائج التقييم بتنسيق قياسي
        """
        logger.info(f"بدء تقييم مهمة (طول النص: {len(task_text)})")
        
        # محاكاة وقت المعالجة
        time.sleep(1)
        
        # إنشاء تقييم عام افتراضي
        grade = "ناجح"
        grade_numerical = 85.0
        feedback = "تم تقييم المهمة بنجاح. تظهر فهماً جيداً للموضوع مع بعض النقاط التي تحتاج إلى تحسين."
        
        # إذا تم توفير معايير تقييم، قم بتقييم كل معيار
        rubric_results = {}
        if rubric:
            for criterion_id, criterion in rubric.items():
                # محاكاة تقييم لكل معيار
                score = min(criterion.get("max_score", 10), max(5, 10 - (hash(criterion_id) % 5)))
                feedback_text = f"تقييم جيد في معيار {criterion.get('name', 'معيار')}. {criterion.get('description', '')}"
                
                rubric_results[criterion_id] = {
                    "score": score,
                    "max_score": criterion.get("max_score", 10),
                    "feedback": feedback_text
                }
        
        # تجميع النتائج
        result = {
            "grade": grade,
            "grade_numerical": grade_numerical,
            "feedback": feedback,
            "rubric_results": rubric_results,
            "model": self.model,
            "timestamp": datetime.utcnow().isoformat(),
            "mock": True  # علامة تشير إلى أن هذا تقييم مبسط للاختبار
        }
        
        logger.info(f"اكتمل تقييم المهمة: {grade}")
        return result
    
    def evaluate_task_json(self, task_text, rubric=None):
        """
        تقييم مهمة BTEC وإرجاع النتائج بتنسيق JSON
        
        المعلمات:
            task_text (str): نص المهمة المراد تقييمها
            rubric (dict, optional): معايير التقييم
            
        العائد:
            str: نتائج التقييم بتنسيق JSON
        """
        result = self.evaluate_task(task_text, rubric)
        return json.dumps(result, ensure_ascii=False, indent=2)

# للاختبار
if __name__ == "__main__":
    service = AIServiceMock()
    task = "هذا مثال على مهمة BTEC لاختبار خدمة الذكاء الاصطناعي المبسطة."
    result = service.evaluate_task(task)
    print(json.dumps(result, ensure_ascii=False, indent=2))