"""
خدمة التقييم الذكي باستخدام مكالمات REST API المباشرة
تتجاوز مشاكل SDK لـ OpenAI
"""

import os
import json
import logging
import requests
from typing import Dict, Any, Optional, List, Union
from flask import current_app

# إعداد السجل
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AIEvaluatorREST:
    """
    صنف لتقييم مهام BTEC باستخدام الذكاء الاصطناعي عبر مكالمات REST API المباشرة بدلاً من SDK
    يتجاوز مشاكل التوافق والاعتمادات في OpenAI SDK
    """

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
            logger.info("تم تهيئة AIEvaluatorREST بمفتاح API صالح")
            self.simulation_mode = False
        else:
            logger.warning("تحذير: لم يتم توفير مفتاح OpenAI API. سيتم استخدام وضع المحاكاة.")
            self.simulation_mode = True
        
        # إعداد عنوان API وترويسات HTTP
        self.api_url = "https://api.openai.com/v1"
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        # ضبط نموذج OpenAI المستخدم
        self.model = "gpt-4o"  # استخدام نموذج GPT-4o الأحدث
    
    def chat_completion_request(self, messages: List[Dict[str, Any]], **kwargs) -> Dict[str, Any]:
        """
        إجراء طلب استكمال المحادثة مباشرة عبر REST API
        
        Args:
            messages: قائمة برسائل المحادثة
            **kwargs: معلمات إضافية للطلب
            
        Returns:
            استجابة API كقاموس
        """
        if self.simulation_mode:
            return {
                "choices": [
                    {
                        "message": {
                            "role": "assistant",
                            "content": "هذه استجابة محاكية. لم يتم إجراء استدعاء فعلي لـ OpenAI API بسبب عدم وجود مفتاح API."
                        }
                    }
                ]
            }
        
        # إعداد URL الطلب
        url = f"{self.api_url}/chat/completions"
        
        # إعداد بيانات الطلب
        data = {
            "model": self.model,
            "messages": messages,
            "temperature": kwargs.get("temperature", 0.7),
            "max_tokens": kwargs.get("max_tokens", 1000)
        }
        
        # إضافة تنسيق الاستجابة إذا تم توفيره
        if "response_format" in kwargs:
            data["response_format"] = kwargs["response_format"]
        
        try:
            # إجراء الطلب
            response = requests.post(url, headers=self.headers, json=data, timeout=30)
            response.raise_for_status()  # رفع استثناء للأخطاء
            
            # إرجاع البيانات كقاموس
            return response.json()
            
        except requests.exceptions.RequestException as e:
            if hasattr(e, 'response') and e.response is not None:
                status_code = e.response.status_code
                try:
                    error_data = e.response.json()
                    error_message = error_data.get('error', {}).get('message', str(e))
                except:
                    error_message = str(e)
                
                logger.error(f"خطأ في OpenAI API (رمز الحالة {status_code}): {error_message}")
                
                if status_code == 429:
                    raise Exception("تم تجاوز حد معدل OpenAI API. يرجى المحاولة مرة أخرى لاحقًا.")
                elif status_code == 401:
                    raise Exception("خطأ في مصادقة OpenAI API. تحقق من صلاحية مفتاح API.")
                else:
                    raise Exception(f"خطأ في OpenAI API: {error_message}")
            else:
                logger.error(f"خطأ في الاتصال بـ OpenAI API: {e}")
                raise Exception(f"خطأ في الاتصال بـ OpenAI API: {e}")
    
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
            messages = [
                {
                    "role": "system",
                    "content": "أنت مقيّم تعليمي متخصص في تقييم مهام BTEC. قم بتقييم المهمة المقدمة وفق معايير BTEC."
                },
                {
                    "role": "user",
                    "content": f"""
                    قم بتقييم مهمة BTEC التالية:
                    
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
                }
            ]
            
            # إجراء طلب التقييم
            response = self.chat_completion_request(
                messages=messages,
                temperature=0.5,
                max_tokens=1500
            )
            
            # استخراج المحتوى من الاستجابة
            content = response["choices"][0]["message"]["content"].strip()
            return content
            
        except Exception as e:
            logger.error(f"خطأ في تقييم المهمة: {e}")
            return f"خطأ في تقييم المهمة: {e}"
    
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
            messages = [
                {
                    "role": "system",
                    "content": "أنت مقيّم تعليمي متخصص في تقييم مهام BTEC. قم بتقييم المهمة المقدمة وإرجاع النتائج بتنسيق JSON."
                },
                {
                    "role": "user",
                    "content": f"""
                    قم بتقييم مهمة BTEC التالية:
                    
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
                }
            ]
            
            # إجراء طلب التقييم
            response = self.chat_completion_request(
                messages=messages,
                temperature=0.5,
                max_tokens=1500,
                response_format={"type": "json_object"}
            )
            
            # استخراج المحتوى من الاستجابة
            content = response["choices"][0]["message"]["content"].strip()
            return json.loads(content)
            
        except Exception as e:
            logger.error(f"خطأ في تقييم المهمة: {e}")
            return {
                "grade": "خطأ",
                "summary": f"خطأ في تقييم المهمة: {e}",
                "strengths": [],
                "improvements": ["حاول مرة أخرى لاحقًا"],
                "score": 0
            }
    
    def evaluate_with_rubric(self, task: str, rubric: Dict[str, Any]) -> Dict[str, Any]:
        """
        تقييم مهمة BTEC باستخدام معيار تقييم مخصص
        
        Args:
            task: نص المهمة للتقييم
            rubric: معيار التقييم المخصص (قاموس)
            
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
            rubric_json = json.dumps(rubric, ensure_ascii=False)
            
            # إنشاء المطالبة (Prompt)
            messages = [
                {
                    "role": "system",
                    "content": "أنت مقيّم تعليمي متخصص في تقييم مهام BTEC باستخدام معايير مخصصة. قم بتقييم المهمة المقدمة وفق المعيار المحدد وإرجاع النتائج بتنسيق JSON."
                },
                {
                    "role": "user",
                    "content": f"""
                    قم بتقييم مهمة BTEC التالية باستخدام معيار التقييم المخصص:
                    
                    المهمة:
                    ```
                    {task}
                    ```
                    
                    معيار التقييم:
                    ```json
                    {rubric_json}
                    ```
                    
                    أرجو تقييم المهمة وفق معيار التقييم المخصص، وتقديم النتائج بتنسيق JSON يتضمن:
                    - grade: الدرجة النهائية حسب معايير BTEC (P, M, D)
                    - summary: ملخص التقييم العام
                    - rubric_results: كائن يحتوي على نتائج كل قسم من معيار التقييم (اسم القسم، الدرجة، التعليق)
                    - total_score: الدرجة الإجمالية المرجحة (0-100)
                    - strengths: قائمة بنقاط القوة (3-5 نقاط)
                    - improvements: قائمة بمجالات التحسين (3-5 مجالات)
                    """
                }
            ]
            
            # إجراء طلب التقييم
            response = self.chat_completion_request(
                messages=messages,
                temperature=0.5,
                max_tokens=2000,
                response_format={"type": "json_object"}
            )
            
            # استخراج المحتوى من الاستجابة
            content = response["choices"][0]["message"]["content"].strip()
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