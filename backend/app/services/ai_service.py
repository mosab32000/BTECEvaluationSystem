"""
خدمة التقييم المركزية بالذكاء الاصطناعي لنظام تقييم BTEC
"""

import os
import json
import logging
from typing import Dict, Any, Optional, List, Union
from flask import current_app
import openai

# إعداد السجل
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AIEvaluator:
    """صنف أساسي لتقييم مهام BTEC باستخدام الذكاء الاصطناعي"""

    def __init__(self, api_key: Optional[str] = None, use_context: bool = False):
        """
        تهيئة مقيم الذكاء الاصطناعي
        
        Args:
            api_key: مفتاح API الخاص بـ OpenAI (اختياري، سيتم استخدام المتغير البيئي أو سياق التطبيق)
            use_context: استخدام سياق تطبيق Flask (اختياري، افتراضيًا False)
        """
        # استخدام مفتاح API المقدم أو البحث عنه في سياق التطبيق أو المتغيرات البيئية
        if api_key:
            self.api_key = api_key
        elif use_context:
            self.api_key = current_app.config.get('OPENAI_API_KEY')
        else:
            self.api_key = os.environ.get('OPENAI_API_KEY')
        
        if self.api_key:
            logger.info("تم تهيئة AIEvaluator بمفتاح API صالح")
            openai.api_key = self.api_key
            self.simulation_mode = False
        else:
            logger.warning("تحذير: لم يتم توفير مفتاح OpenAI API. سيتم استخدام وضع المحاكاة.")
            self.simulation_mode = True
        
        # ضبط نموذج OpenAI المستخدم
        self.model = "gpt-4o"  # استخدام نموذج GPT-4o الأحدث
    
    def evaluate(self, task: str) -> str:
        """
        تقييم مهمة BTEC وإرجاع نتيجة التقييم
        
        Args:
            task: نص المهمة للتقييم
            
        Returns:
            نتيجة التقييم
        """
        if self.simulation_mode:
            return "هذا تقييم محاكي. لم يتم إجراء استدعاء فعلي لـ OpenAI API بسبب عدم وجود مفتاح API."
        
        try:
            # إنشاء المطالبة (Prompt)
            prompt = f"""
            أنت مقيّم تعليمي متخصص في تقييم مهام BTEC. قم بتحليل المهمة التالية:
            
            ```
            {task}
            ```
            
            أرجو تقديم تقييم شامل يتضمن:
            
            1. ملخص المهمة ومدى وضوحها
            2. تقييم التنظيم والهيكل
            3. تقييم المحتوى والفهم العميق للموضوع
            4. نقاط القوة في المهمة
            5. مجالات التحسين
            6. درجة التقييم حسب معايير BTEC (P, M, D)
            
            قدم تحليلًا عميقًا وبنّاءً.
            """
            
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "أنت مقيّم تعليمي متخصص في تقييم مهام BTEC. تقييماتك موضوعية ودقيقة وبناءة."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=1000
            )
            
            return response.choices[0].message.content.strip()
        
        except openai.error.RateLimitError:
            logger.error("تم تجاوز حد معدل OpenAI API")
            return "خطأ: تم تجاوز حد معدل OpenAI API. يرجى المحاولة مرة أخرى لاحقًا."
        except openai.error.AuthenticationError:
            logger.error("خطأ في مصادقة OpenAI API")
            return "خطأ: فشل مصادقة OpenAI API. تحقق من صلاحية مفتاح API."
        except Exception as e:
            logger.error(f"خطأ في OpenAI API: {e}")
            return f"خطأ أثناء تقييم الذكاء الاصطناعي: {e}"
    
    def evaluate_json(self, task: str) -> Dict[str, Any]:
        """
        تقييم مهمة BTEC وإرجاع نتيجة التقييم كقاموس
        
        Args:
            task: نص المهمة للتقييم
            
        Returns:
            نتيجة التقييم كقاموس
        """
        if self.simulation_mode:
            return {
                "grade": "محاكاة",
                "summary": "هذا تقييم محاكي. لم يتم إجراء استدعاء فعلي لـ OpenAI API.",
                "strengths": ["نقطة قوة محاكية 1", "نقطة قوة محاكية 2"],
                "improvements": ["مجال تحسين محاكي 1", "مجال تحسين محاكي 2"],
                "score": 75
            }
        
        try:
            # إنشاء المطالبة (Prompt)
            prompt = f"""
            أنت مقيّم تعليمي متخصص في تقييم مهام BTEC. قم بتحليل المهمة التالية وتقديم تقييم بتنسيق JSON:
            
            ```
            {task}
            ```
            
            أرجو تقديم تقييم شامل بتنسيق JSON يتضمن الحقول التالية:
            - grade: الدرجة النهائية حسب معايير BTEC (P, M, D)
            - summary: ملخص التقييم العام
            - organization: تقييم التنظيم والهيكل (0-10)
            - content: تقييم المحتوى والفهم (0-10)
            - strengths: قائمة بنقاط القوة (3-5 نقاط)
            - improvements: قائمة بمجالات التحسين (3-5 مجالات)
            - feedback: تعليقات تفصيلية
            - score: درجة رقمية من 0 إلى 100
            """
            
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "أنت مقيّم تعليمي متخصص في تقييم مهام BTEC. قم بإرجاع تقييمك بتنسيق JSON فقط."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=1000,
                response_format={"type": "json_object"}
            )
            
            content = response.choices[0].message.content.strip()
            return json.loads(content)
        
        except openai.error.RateLimitError:
            logger.error("تم تجاوز حد معدل OpenAI API")
            return {
                "grade": "خطأ",
                "summary": "تم تجاوز حد معدل OpenAI API. يرجى المحاولة مرة أخرى لاحقًا.",
                "strengths": [],
                "improvements": ["حاول مرة أخرى لاحقًا"],
                "score": 0
            }
        except openai.error.AuthenticationError:
            logger.error("خطأ في مصادقة OpenAI API")
            return {
                "grade": "خطأ",
                "summary": "فشل مصادقة OpenAI API. تحقق من صلاحية مفتاح API.",
                "strengths": [],
                "improvements": ["تحقق من صلاحية مفتاح API"],
                "score": 0
            }
        except Exception as e:
            logger.error(f"خطأ في OpenAI API: {e}")
            return {
                "grade": "خطأ",
                "summary": f"خطأ أثناء تقييم الذكاء الاصطناعي: {e}",
                "strengths": [],
                "improvements": ["حاول مرة أخرى لاحقًا"],
                "score": 0
            }
    
    def evaluate_with_rubric(self, task: str, rubric: Dict[str, Any]) -> Dict[str, Any]:
        """
        تقييم مهمة BTEC باستخدام معيار تقييم مخصص
        
        Args:
            task: نص المهمة للتقييم
            rubric: معيار التقييم المخصص
            
        Returns:
            نتيجة التقييم كقاموس
        """
        if self.simulation_mode:
            return {
                "grade": "محاكاة",
                "summary": "هذا تقييم محاكي باستخدام معيار مخصص. لم يتم إجراء استدعاء فعلي لـ OpenAI API.",
                "rubric_results": {section["name"]: {"score": 7, "feedback": f"تعليق محاكي لقسم {section['name']}"} for section in rubric.get("sections", [])},
                "total_score": 75,
                "strengths": ["نقطة قوة محاكية 1", "نقطة قوة محاكية 2"],
                "improvements": ["مجال تحسين محاكي 1", "مجال تحسين محاكي 2"]
            }
        
        try:
            # تحويل معيار التقييم إلى نص
            rubric_str = json.dumps(rubric, ensure_ascii=False)
            
            # إنشاء المطالبة (Prompt)
            prompt = f"""
            أنت مقيّم تعليمي متخصص في تقييم مهام BTEC باستخدام معايير مخصصة. قم بتقييم المهمة التالية باستخدام معيار التقييم المخصص:
            
            المهمة:
            ```
            {task}
            ```
            
            معيار التقييم:
            ```json
            {rubric_str}
            ```
            
            أرجو تقييم المهمة وفق معيار التقييم المخصص، وتقديم النتائج بتنسيق JSON يتضمن:
            - grade: الدرجة النهائية حسب معايير BTEC (P, M, D)
            - summary: ملخص التقييم العام
            - rubric_results: كائن يحتوي على نتائج كل قسم من معيار التقييم (اسم القسم، الدرجة، التعليق)
            - total_score: الدرجة الإجمالية المرجحة (0-100)
            - strengths: قائمة بنقاط القوة (3-5 نقاط)
            - improvements: قائمة بمجالات التحسين (3-5 مجالات)
            """
            
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "أنت مقيّم تعليمي متخصص في تقييم مهام BTEC باستخدام معايير مخصصة. قم بإرجاع تقييمك بتنسيق JSON فقط."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.5,
                max_tokens=2000,
                response_format={"type": "json_object"}
            )
            
            content = response.choices[0].message.content.strip()
            return json.loads(content)
            
        except Exception as e:
            logger.error(f"خطأ في تقييم المهمة باستخدام معيار مخصص: {e}")
            return {
                "grade": "خطأ",
                "summary": f"خطأ في تقييم المهمة: {e}",
                "rubric_results": {},
                "total_score": 0,
                "strengths": [],
                "improvements": ["حاول مرة أخرى لاحقًا"]
            }