"""
خدمة الذكاء الاصطناعي متعددة الوسائط لتقييم BTEC
تدعم تقييم النص والصور معًا
"""

import os
import base64
import json
import logging
import openai
from io import BytesIO
from PIL import Image
from flask import current_app
from typing import Dict, Any, Optional, Union, List, Tuple

# إعداد السجل
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AIEvaluatorMultimodal:
    """صنف لتقييم مهام BTEC باستخدام الذكاء الاصطناعي متعدد الوسائط"""

    def __init__(self, api_key: Optional[str] = None, use_context: bool = False):
        """
        تهيئة مقيم الذكاء الاصطناعي متعدد الوسائط
        
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
            logger.info("تم تهيئة AIEvaluatorMultimodal بمفتاح API صالح")
            openai.api_key = self.api_key
            self.simulation_mode = False
        else:
            logger.warning("تحذير: لم يتم توفير مفتاح OpenAI API. سيتم استخدام وضع المحاكاة.")
            self.simulation_mode = True
        
        # ضبط نموذج OpenAI المستخدم - استخدام نموذج يدعم الصور
        self.model = "gpt-4o"  # نموذج GPT-4o يدعم الصور والنصوص
    
    def _encode_image(self, image_path: str) -> str:
        """
        تحويل الصورة إلى تشفير base64
        
        Args:
            image_path: مسار الصورة على القرص
            
        Returns:
            سلسلة الصورة المشفرة بـ base64
        """
        try:
            with open(image_path, "rb") as image_file:
                return base64.b64encode(image_file.read()).decode('utf-8')
        except Exception as e:
            logger.error(f"خطأ في تشفير الصورة: {e}")
            raise
    
    def _encode_image_from_bytes(self, image_bytes: bytes) -> str:
        """
        تحويل البيانات الثنائية للصورة إلى تشفير base64
        
        Args:
            image_bytes: بيانات الصورة الثنائية
            
        Returns:
            سلسلة الصورة المشفرة بـ base64
        """
        try:
            return base64.b64encode(image_bytes).decode('utf-8')
        except Exception as e:
            logger.error(f"خطأ في تشفير الصورة من البيانات الثنائية: {e}")
            raise
    
    def _resize_image_if_needed(self, image_path: str, max_size: int = 4194304) -> str:
        """
        تغيير حجم الصورة إذا كان حجمها أكبر من الحد الأقصى
        
        Args:
            image_path: مسار الصورة
            max_size: الحد الأقصى لحجم الصورة بالبايت
            
        Returns:
            مسار الصورة بعد تغيير الحجم (قد يكون نفس المسار الأصلي)
        """
        try:
            file_size = os.path.getsize(image_path)
            if file_size <= max_size:
                return image_path
            
            # حساب نسبة التصغير المطلوبة
            ratio = (max_size / file_size) ** 0.5 * 0.9  # استخدام عامل أمان 0.9
            
            # فتح وتغيير حجم الصورة
            img = Image.open(image_path)
            new_width = int(img.width * ratio)
            new_height = int(img.height * ratio)
            resized_img = img.resize((new_width, new_height), Image.LANCZOS)
            
            # حفظ الصورة المعدلة
            output_path = f"{os.path.splitext(image_path)[0]}_resized{os.path.splitext(image_path)[1]}"
            resized_img.save(output_path, quality=85)
            
            logger.info(f"تم تغيير حجم الصورة من {file_size} إلى {os.path.getsize(output_path)} بايت")
            return output_path
            
        except Exception as e:
            logger.error(f"خطأ في تغيير حجم الصورة: {e}")
            return image_path  # العودة إلى المسار الأصلي في حالة الخطأ
    
    def evaluate_with_images(self, text: str, image_paths: List[str]) -> str:
        """
        تقييم مهمة BTEC مع صور مرفقة
        
        Args:
            text: نص المهمة للتقييم
            image_paths: قائمة مسارات الصور المرفقة
            
        Returns:
            نتيجة التقييم كنص
        """
        if self.simulation_mode:
            return f"هذا تقييم محاكي لمهمة مع {len(image_paths)} صورة مرفقة. لم يتم إجراء استدعاء فعلي لـ OpenAI API بسبب عدم وجود مفتاح API."
        
        try:
            # تحضير الرسائل للـ API
            messages = [
                {
                    "role": "system",
                    "content": "أنت مقيّم تعليمي متخصص في تقييم مهام BTEC التي تتضمن نصوصًا وصورًا. تقييماتك موضوعية ودقيقة وتأخذ في الاعتبار جميع عناصر المهمة."
                }
            ]
            
            # إنشاء رسالة المستخدم بمكونات متعددة (نص وصور)
            user_message = {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": f"""قم بتقييم مهمة BTEC التالية التي تتضمن نصًا وصورًا:
                        
النص:
```
{text}
```

يرجى تقديم تقييم شامل يتضمن:
1. تحليل النص والصور معًا كوحدة متكاملة
2. تقييم العلاقة بين النص والصور وكيف تدعم بعضها البعض
3. تقييم جودة الصور ووضوحها وملاءمتها للموضوع
4. تحديد نقاط القوة والضعف في المهمة ككل
5. اقتراح مجالات للتحسين
6. إعطاء درجة نهائية بناءً على معايير BTEC (P, M, D)
"""
                    }
                ]
            }
            
            # إضافة الصور إلى رسالة المستخدم
            for image_path in image_paths:
                try:
                    # تغيير حجم الصورة إذا لزم الأمر
                    resized_path = self._resize_image_if_needed(image_path)
                    
                    # تشفير الصورة بـ base64
                    base64_image = self._encode_image(resized_path)
                    
                    # إضافة الصورة إلى رسالة المستخدم
                    user_message["content"].append({
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}"
                        }
                    })
                    
                except Exception as e:
                    logger.error(f"خطأ في إضافة الصورة {image_path}: {e}")
                    # الاستمرار مع الصور الأخرى في حالة فشل إحداها
            
            # إضافة رسالة المستخدم المكتملة
            messages.append(user_message)
            
            # إجراء استدعاء API
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=messages,
                temperature=0.5,
                max_tokens=2000  # زيادة عدد الرموز لاستيعاب تحليل أكثر تفصيلاً
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
    
    def evaluate_image_content(self, image_path: str) -> Dict[str, Any]:
        """
        تحليل محتوى صورة مقدمة من الطالب
        
        Args:
            image_path: مسار الصورة للتحليل
            
        Returns:
            نتيجة تحليل الصورة كقاموس
        """
        if self.simulation_mode:
            return {
                "content_type": "محاكاة",
                "description": "هذا تحليل محاكي للصورة. لم يتم إجراء استدعاء فعلي لـ OpenAI API.",
                "elements": ["عنصر محاكي 1", "عنصر محاكي 2", "عنصر محاكي 3"],
                "quality_score": 0.75,
                "relevance_score": 0.8
            }
        
        try:
            # تغيير حجم الصورة إذا لزم الأمر
            resized_path = self._resize_image_if_needed(image_path)
            
            # تشفير الصورة بـ base64
            base64_image = self._encode_image(resized_path)
            
            # تحضير الرسائل للـ API
            messages = [
                {
                    "role": "system",
                    "content": "أنت محلل محتوى متخصص. قم بتحليل الصورة المقدمة وتقديم وصف تفصيلي وتقييم لجودتها وملاءمتها للسياق التعليمي."
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": """تحليل هذه الصورة وتقديم المعلومات التالية بتنسيق JSON:
1. نوع المحتوى (مخطط، رسم بياني، صورة توضيحية، صورة فوتوغرافية، نص، إلخ)
2. وصف تفصيلي للمحتوى
3. قائمة بالعناصر الرئيسية في الصورة
4. تقييم جودة الصورة (وضوح، دقة، إضاءة) من 0 إلى 1
5. تقييم مدى ملاءمة الصورة للسياق التعليمي من 0 إلى 1"""
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            }
                        }
                    ]
                }
            ]
            
            # إجراء استدعاء API
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=messages,
                temperature=0.3,
                max_tokens=1000,
                response_format={"type": "json_object"}  # طلب تنسيق JSON
            )
            
            # تحليل الاستجابة
            content = response.choices[0].message.content.strip()
            return json.loads(content)
            
        except Exception as e:
            logger.error(f"خطأ في تحليل الصورة: {e}")
            return {
                "content_type": "خطأ",
                "description": f"حدث خطأ أثناء تحليل الصورة: {str(e)}",
                "elements": [],
                "quality_score": 0,
                "relevance_score": 0
            }
    
    def analyze_document_image(self, image_path: str) -> str:
        """
        استخراج النص من مستند مصور (OCR)
        
        Args:
            image_path: مسار صورة المستند
            
        Returns:
            النص المستخرج من الصورة
        """
        if self.simulation_mode:
            return "هذا نص محاكي مستخرج من صورة المستند. لم يتم إجراء استدعاء فعلي لـ OpenAI API."
        
        try:
            # تغيير حجم الصورة إذا لزم الأمر
            resized_path = self._resize_image_if_needed(image_path)
            
            # تشفير الصورة بـ base64
            base64_image = self._encode_image(resized_path)
            
            # تحضير الرسائل للـ API
            messages = [
                {
                    "role": "system",
                    "content": "أنت أداة OCR متقدمة. استخرج كل النص المرئي من الصورة المقدمة بدقة عالية."
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "استخرج كل النص المرئي من هذه الصورة، مع الحفاظ على تنسيق الفقرات قدر الإمكان. إذا كان المستند متعدد الأعمدة، قم بمعالجة كل عمود على حدة بالترتيب المناسب للقراءة."
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            }
                        }
                    ]
                }
            ]
            
            # إجراء استدعاء API
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=messages,
                temperature=0.1,  # درجة حرارة منخفضة للحصول على نتائج أكثر دقة
                max_tokens=4000  # زيادة عدد الرموز لاستيعاب مستندات أطول
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"خطأ في استخراج النص من الصورة: {e}")
            return f"حدث خطأ أثناء استخراج النص: {str(e)}"
    
    def evaluate_combined_submission(self, text: str, image_paths: List[str], evaluation_criteria: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        تقييم شامل لمهمة BTEC تتضمن نصًا وصورًا مع معايير تقييم مخصصة
        
        Args:
            text: نص المهمة للتقييم
            image_paths: قائمة مسارات الصور المرفقة
            evaluation_criteria: معايير التقييم المخصصة (اختياري)
            
        Returns:
            نتيجة التقييم الشامل كقاموس
        """
        if self.simulation_mode:
            return {
                "grade": "محاكاة",
                "summary": f"هذا تقييم محاكي لمهمة تتضمن نصًا و{len(image_paths)} صورة.",
                "text_evaluation": "تقييم محاكي للنص",
                "image_evaluation": [f"تقييم محاكي للصورة {i+1}" for i in range(len(image_paths))],
                "strengths": ["نقطة قوة محاكية 1", "نقطة قوة محاكية 2"],
                "improvements": ["مجال تحسين محاكي 1", "مجال تحسين محاكي 2"],
                "score": 75
            }
        
        try:
            # تحضير معايير التقييم
            criteria_text = "معايير BTEC القياسية"
            if evaluation_criteria:
                criteria_text = json.dumps(evaluation_criteria, ensure_ascii=False)
            
            # تحضير الرسائل للـ API
            messages = [
                {
                    "role": "system",
                    "content": "أنت مقيّم تعليمي متخصص في تقييم مهام BTEC المتكاملة. تقييماتك شاملة وموضوعية وتتبع المعايير المحددة."
                }
            ]
            
            # إنشاء رسالة المستخدم بمكونات متعددة
            user_message = {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": f"""قم بتقييم مهمة BTEC التالية التي تتضمن نصًا وصورًا، واستخدم المعايير المحددة:
                        
النص:
```
{text}
```

معايير التقييم:
```
{criteria_text}
```

قم بتقديم تقييم شامل بتنسيق JSON يتضمن الحقول التالية:
- grade: الدرجة النهائية (P, M, D)
- summary: ملخص التقييم العام
- text_evaluation: تقييم مفصل للنص
- image_evaluation: تقييم مفصل لكل صورة
- strengths: قائمة بنقاط القوة الرئيسية
- improvements: قائمة بمجالات التحسين
- score: درجة رقمية من 0 إلى 100
"""
                    }
                ]
            }
            
            # إضافة الصور إلى رسالة المستخدم
            for image_path in image_paths:
                try:
                    # تغيير حجم الصورة إذا لزم الأمر
                    resized_path = self._resize_image_if_needed(image_path)
                    
                    # تشفير الصورة بـ base64
                    base64_image = self._encode_image(resized_path)
                    
                    # إضافة الصورة إلى رسالة المستخدم
                    user_message["content"].append({
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}"
                        }
                    })
                    
                except Exception as e:
                    logger.error(f"خطأ في إضافة الصورة {image_path}: {e}")
                    # الاستمرار مع الصور الأخرى في حالة فشل إحداها
            
            # إضافة رسالة المستخدم المكتملة
            messages.append(user_message)
            
            # إجراء استدعاء API
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=messages,
                temperature=0.4,
                max_tokens=2500,
                response_format={"type": "json_object"}  # طلب تنسيق JSON
            )
            
            # تحليل الاستجابة
            content = response.choices[0].message.content.strip()
            return json.loads(content)
            
        except Exception as e:
            logger.error(f"خطأ في تقييم المهمة المدمجة: {e}")
            return {
                "grade": "خطأ",
                "summary": f"حدث خطأ أثناء التقييم: {str(e)}",
                "text_evaluation": "غير متوفر بسبب خطأ",
                "image_evaluation": ["غير متوفر بسبب خطأ"] * len(image_paths),
                "strengths": [],
                "improvements": ["حاول مرة أخرى لاحقًا"],
                "score": 0
            }