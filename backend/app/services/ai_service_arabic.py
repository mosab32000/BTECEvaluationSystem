"""
خدمة التقييم باللغة العربية للذكاء الاصطناعي في نظام تقييم BTEC
"""

import os
import json
import logging
import openai
from flask import current_app
from typing import Dict, Any, Optional

# إعداد السجل
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AIEvaluatorArabic:
    """صنف لتقييم مهام BTEC باستخدام الذكاء الاصطناعي بتركيز على اللغة العربية"""

    def __init__(self, api_key: Optional[str] = None, use_context: bool = False):
        """
        تهيئة مقيم الذكاء الاصطناعي العربي
        
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
            logger.info("تم تهيئة AIEvaluatorArabic بمفتاح API صالح")
            openai.api_key = self.api_key
            self.simulation_mode = False
        else:
            logger.warning("تحذير: لم يتم توفير مفتاح OpenAI API. سيتم استخدام وضع المحاكاة.")
            self.simulation_mode = True
        
        # ضبط نموذج OpenAI المستخدم
        self.model = "gpt-4o"  # استخدام نموذج GPT-4o الأحدث
    
    def evaluate_arabic(self, task: str) -> str:
        """
        تقييم مهمة BTEC بالعربية وإرجاع نتيجة التقييم
        
        Args:
            task: نص المهمة للتقييم باللغة العربية
            
        Returns:
            نتيجة التقييم باللغة العربية
        """
        if self.simulation_mode:
            return "هذا تقييم محاكي باللغة العربية. لم يتم إجراء استدعاء فعلي لـ OpenAI API بسبب عدم وجود مفتاح API."
        
        try:
            # إنشاء المطالبة (Prompt) بالعربية
            prompt = f"""
            أنت مقيّم تعليمي متخصص في تقييم مهام BTEC باللغة العربية. قم بتحليل المهمة التالية بدقة وموضوعية:
            
            المهمة:
            ```
            {task}
            ```
            
            يرجى تقديم تقييم شامل يتضمن:
            
            1. تلخيص المهمة ومدى وضوحها
            2. تقييم التنظيم والهيكل
            3. تقييم المحتوى والفهم العميق للموضوع
            4. تقييم الاستخدام السليم للغة العربية والمصطلحات الفنية
            5. تحديد نقاط القوة في المهمة
            6. تحديد مجالات التحسين
            7. درجة التقييم حسب معايير BTEC (P, M, D)
            8. توصيات محددة للتحسين
            
            قدم تحليلًا عميقًا وبنّاءً مع أمثلة محددة من النص.
            """
            
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "أنت مقيّم تعليمي متخصص في تقييم مهام BTEC باللغة العربية. تحليلاتك دقيقة وموضوعية ومفيدة للطلاب."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.4,  # درجة حرارة منخفضة للحصول على نتائج متسقة
                max_tokens=1500   # زيادة الحد الأقصى للرموز للسماح بتقييمات مفصلة
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
    
    def evaluate_arabic_json(self, task: str) -> Dict[str, Any]:
        """
        تقييم مهمة BTEC بالعربية وإرجاع نتيجة التقييم كقاموس JSON
        
        Args:
            task: نص المهمة للتقييم باللغة العربية
            
        Returns:
            نتيجة التقييم كقاموس بالعربية
        """
        if self.simulation_mode:
            return {
                "درجة": "محاكاة",
                "تلخيص": "هذا تقييم محاكي. لم يتم إجراء استدعاء فعلي لـ OpenAI API.",
                "نقاط_القوة": ["نقطة قوة محاكية 1", "نقطة قوة محاكية 2"],
                "مجالات_التحسين": ["مجال تحسين محاكي 1", "مجال تحسين محاكي 2"],
                "توصيات": ["توصية محاكية 1", "توصية محاكية 2"]
            }
        
        try:
            # إنشاء المطالبة (Prompt) بالعربية مع طلب تنسيق JSON
            prompt = f"""
            أنت مقيّم تعليمي متخصص في تقييم مهام BTEC باللغة العربية. قم بتحليل المهمة التالية بدقة وموضوعية:
            
            المهمة:
            ```
            {task}
            ```
            
            يرجى تقديم تقييم شامل في تنسيق JSON يتضمن الحقول التالية:
            - درجة: الدرجة النهائية حسب معايير BTEC (P, M, D)
            - تلخيص: تلخيص موجز للمهمة وتقييمها العام
            - تنظيم: تقييم لتنظيم وهيكل المهمة
            - محتوى: تقييم لجودة المحتوى والفهم
            - لغة: تقييم للاستخدام السليم للغة العربية
            - نقاط_القوة: قائمة بنقاط القوة الرئيسية
            - مجالات_التحسين: قائمة بمجالات التحسين
            - توصيات: قائمة بالتوصيات المحددة للتحسين
            
            قدم تحليلًا عميقًا وبنّاءً مع أمثلة محددة من النص.
            """
            
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "أنت مقيّم تعليمي متخصص في تقييم مهام BTEC باللغة العربية. قم بإرجاع تقييمك بتنسيق JSON فقط."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.4,  # درجة حرارة منخفضة للحصول على نتائج متسقة
                max_tokens=1500,   # زيادة الحد الأقصى للرموز للسماح بتقييمات مفصلة
                response_format={"type": "json_object"}  # طلب تنسيق JSON
            )
            
            content = response.choices[0].message.content.strip()
            return json.loads(content)
        
        except openai.error.RateLimitError:
            logger.error("تم تجاوز حد معدل OpenAI API")
            return {
                "درجة": "خطأ",
                "تلخيص": "تم تجاوز حد معدل OpenAI API. يرجى المحاولة مرة أخرى لاحقًا.",
                "نقاط_القوة": [],
                "مجالات_التحسين": [],
                "توصيات": ["حاول مرة أخرى لاحقًا"]
            }
        except openai.error.AuthenticationError:
            logger.error("خطأ في مصادقة OpenAI API")
            return {
                "درجة": "خطأ",
                "تلخيص": "فشل مصادقة OpenAI API. تحقق من صلاحية مفتاح API.",
                "نقاط_القوة": [],
                "مجالات_التحسين": [],
                "توصيات": ["تحقق من صلاحية مفتاح API"]
            }
        except Exception as e:
            logger.error(f"خطأ في OpenAI API: {e}")
            return {
                "درجة": "خطأ",
                "تلخيص": f"خطأ أثناء تقييم الذكاء الاصطناعي: {e}",
                "نقاط_القوة": [],
                "مجالات_التحسين": [],
                "توصيات": ["حاول مرة أخرى لاحقًا"]
            }
    
    def detect_language(self, text: str) -> str:
        """
        اكتشاف لغة النص المدخل
        
        Args:
            text: النص للتحليل
            
        Returns:
            رمز اللغة المكتشفة (ar, en, etc.) أو 'unknown'
        """
        if self.simulation_mode:
            if any("\u0600" <= c <= "\u06FF" for c in text):
                return "ar"
            else:
                return "en"
        
        try:
            prompt = f"""
            حدد اللغة الرئيسية المستخدمة في النص التالي. أرجع رمز اللغة فقط (مثل: ar للعربية، en للإنجليزية، fr للفرنسية، إلخ).
            
            النص:
            ```
            {text[:500]}  # استخدام أول 500 حرف فقط للاقتصاد في استخدام الرموز
            ```
            
            رمز اللغة:
            """
            
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "أنت أداة لتحديد اللغات. أرجع رمز اللغة فقط بدون أي نص إضافي."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,  # درجة حرارة منخفضة جدًا للحصول على إجابة محددة
                max_tokens=10     # نحتاج فقط لعدد قليل من الرموز للإجابة
            )
            
            language_code = response.choices[0].message.content.strip().lower()
            
            # تنظيف الإخراج لضمان الحصول على رمز اللغة فقط
            language_code = language_code.replace(".", "").replace(",", "").strip()
            if language_code in ["ar", "arabic", "العربية"]:
                return "ar"
            elif language_code in ["en", "english", "الإنجليزية"]:
                return "en"
            else:
                return language_code[:2]  # رجوع أول حرفين كرمز اللغة
            
        except Exception as e:
            logger.error(f"خطأ في اكتشاف اللغة: {e}")
            # التحقق البسيط من وجود أحرف عربية
            if any("\u0600" <= c <= "\u06FF" for c in text):
                return "ar"
            else:
                return "unknown"