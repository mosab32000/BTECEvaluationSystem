"""
خدمة تقييم الذكاء الاصطناعي متعددة النماذج (نص + صور) في نظام تقييم BTEC
"""

from openai import OpenAI
from flask import current_app
import logging
import json
import time
import base64
import os
import tempfile
from PIL import Image
import io

class AIEvaluatorMultimodal:
    """
    مُقيِّم الذكاء الاصطناعي متعدد النماذج للمهام التي تحتوي على نصوص وصور
    """
    
    def __init__(self):
        """تهيئة المُقيِّم باستخدام مفتاح OpenAI API"""
        api_key = current_app.config.get('OPENAI_API_KEY')
        if not api_key:
            logging.warning("لم يتم تكوين OPENAI_API_KEY. سيتم محاكاة التقييم متعدد النماذج.")
            self.api_key = None
        else:
            self.api_key = api_key
            logging.info("تم تهيئة مُقيِّم الذكاء الاصطناعي متعدد النماذج بمفتاح API صالح")

    def encode_image(self, image_path):
        """
        تشفير الصورة إلى base64
        
        Args:
            image_path (str): مسار الصورة
            
        Returns:
            str: سلسلة الصورة المشفرة بـ base64
        """
        try:
            with open(image_path, "rb") as image_file:
                return base64.b64encode(image_file.read()).decode('utf-8')
        except Exception as e:
            logging.error(f"خطأ في تشفير الصورة: {e}")
            return None

    def resize_image_if_needed(self, image_path, max_size_mb=10):
        """
        تغيير حجم الصورة إذا تجاوزت الحد الأقصى للحجم
        
        Args:
            image_path (str): مسار الصورة
            max_size_mb (int): الحد الأقصى لحجم الصورة بالميجابايت
            
        Returns:
            str: مسار الصورة المحجمة أو الأصلية
        """
        # تحويل الحد الأقصى للحجم إلى بايت
        max_size_bytes = max_size_mb * 1024 * 1024
        
        # التحقق من حجم الملف
        file_size = os.path.getsize(image_path)
        if file_size <= max_size_bytes:
            return image_path  # الصورة ضمن الحجم المسموح
        
        try:
            # فتح الصورة
            img = Image.open(image_path)
            
            # حساب نسبة التقليص المطلوبة
            scale_factor = (max_size_bytes / file_size) ** 0.5
            
            # حساب الأبعاد الجديدة
            new_width = int(img.width * scale_factor)
            new_height = int(img.height * scale_factor)
            
            # تغيير حجم الصورة
            img_resized = img.resize((new_width, new_height), Image.LANCZOS)
            
            # حفظ الصورة في ملف مؤقت
            with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as temp_file:
                temp_path = temp_file.name
                img_resized.save(temp_path, "JPEG", quality=85)
            
            logging.info(f"تم تغيير حجم الصورة من {file_size/1024/1024:.2f}MB إلى {os.path.getsize(temp_path)/1024/1024:.2f}MB")
            return temp_path
        except Exception as e:
            logging.error(f"خطأ في تغيير حجم الصورة: {e}")
            return image_path  # إرجاع المسار الأصلي في حالة الخطأ

    def evaluate_with_images(self, task_submission, image_paths=None):
        """
        تقييم مهمة BTEC التي تحتوي على نص وصور
        
        Args:
            task_submission (str): نص المهمة المقدمة للتقييم
            image_paths (list): قائمة بمسارات الصور المرفقة بالمهمة
            
        Returns:
            dict: تقييم منظم مع الدرجة والملاحظات ومجالات التحسين
        """
        if not image_paths:
            image_paths = []
        
        if not self.api_key:
            # محاكاة تقييم الذكاء الاصطناعي متعدد النماذج
            logging.warning("استخدام تقييم ذكاء اصطناعي متعدد النماذج محاكى (لا يوجد مفتاح API)")
            image_count = len(image_paths)
            return {
                "grade": "جيد",
                "feedback": [
                    "هذا تقييم محاكى لمهمة متعددة النماذج (نص + صور).",
                    f"تم تقديم {image_count} صورة مع المهمة.",
                    "يُظهر العمل المقدم فهمًا جيدًا للموضوع.",
                    "الصور المرفقة تدعم النص بشكل جيد."
                ],
                "visual_elements_feedback": [
                    "الصور ذات جودة مناسبة وتساعد في توضيح المفاهيم المقدمة.",
                    "ترتيب العناصر المرئية منطقي ويدعم تدفق المعلومات."
                ],
                "improvement_areas": [
                    "تحسين التكامل بين النص والصور",
                    "إضافة تعليقات توضيحية أكثر تفصيلاً للصور",
                    "تضمين المزيد من الأمثلة العملية"
                ],
                "criteria_met": {
                    "knowledge": 75,
                    "application": 70,
                    "analysis": 65,
                    "visual_communication": 80,
                    "overall": 72
                },
                "simulated": True
            }
        
        # تحضير الصور لإرسالها إلى API
        content_parts = []
        
        # إضافة جزء النص أولاً
        content_parts.append({
            "type": "text",
            "text": "قيّم المهمة التالية التي تتكون من نص وصور. قدم تقييمًا شاملاً يغطي محتوى النص وجودة ودقة واستخدام العناصر المرئية:\n\n" + task_submission
        })
        
        # إضافة الصور
        for i, image_path in enumerate(image_paths):
            try:
                # تغيير حجم الصورة إذا لزم الأمر
                resized_path = self.resize_image_if_needed(image_path)
                
                # تشفير الصورة
                base64_image = self.encode_image(resized_path)
                
                # حذف الملف المؤقت إذا تم إنشاؤه
                if resized_path != image_path:
                    os.remove(resized_path)
                
                if base64_image:
                    content_parts.append({
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}",
                            "detail": "high"  # طلب تفاصيل عالية للصورة
                        }
                    })
                    logging.info(f"تمت إضافة الصورة {i+1} إلى المحتوى")
                else:
                    logging.warning(f"فشل في إضافة الصورة {i+1}")
            except Exception as e:
                logging.error(f"خطأ في معالجة الصورة {i+1}: {e}")
        
        try:
            # استخدام عميل OpenAI للإصدار 1.0.0+
            client = OpenAI(api_key=self.api_key)
            start_time = time.time()
            
            # إنشاء إكمال الذكاء الاصطناعي باستخدام ChatGPT مع المحتوى متعدد النماذج
            response = client.chat.completions.create(
                model="gpt-4o", # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
                # do not change this unless explicitly requested by the user
                messages=[
                    {"role": "system", "content": """أنت مقيّم BTEC خبير في المؤهلات المهنية البريطانية.
                     تخصصك هو تقييم المهام التي تتضمن نصوصًا وعناصر مرئية.
                     
                     قم بتقييم الأعمال المقدمة وتصنيفها بدقة كـ: مقبول، جيد، أو ممتاز بناءً على معايير BTEC.
                     
                     اتبع إرشادات تقييم BTEC التالية:
                     - مقبول: فهم أساسي، يلبي الحد الأدنى من المتطلبات، تحليل محدود (50-59%)
                     - جيد: فهم جيد، هيكل جيد، بعض التحليل النقدي (60-79%)
                     - ممتاز: فهم ممتاز، شامل، تحليل نقدي عميق (80-100%)
                     
                     يجب أن يشمل تقييمك كلاً من:
                     1. محتوى النص وجودته
                     2. العناصر المرئية المقدمة (الصور، الرسوم البيانية، إلخ)
                     3. التكامل والتنسيق بين النص والعناصر المرئية
                     
                     أرجع تقييمك بتنسيق JSON التالي:
                     {
                       "grade": "مقبول/جيد/ممتاز",
                       "feedback": ["نقطة 1", "نقطة 2", "نقطة 3", "نقطة 4"],
                       "visual_elements_feedback": ["تعليق 1 على العناصر المرئية", "تعليق 2 على العناصر المرئية"],
                       "improvement_areas": ["مجال 1", "مجال 2", "مجال 3"],
                       "criteria_met": {
                         "knowledge": 0-100,
                         "application": 0-100,
                         "analysis": 0-100,
                         "visual_communication": 0-100,
                         "overall": 0-100
                       }
                     }
                     
                     تأكد من أن ملاحظاتك محددة وقابلة للتنفيذ ومتوافقة مع معايير BTEC.
                     يجب أن تعكس النسب المئوية في criteria_met الأداء في كل مجال من 0 إلى 100.
                     """},
                    {"role": "user", "content": content_parts}
                ],
                response_format={"type": "json_object"},
                max_tokens=2000,
                temperature=0.7
            )
            
            elapsed_time = time.time() - start_time
            logging.info(f"اكتمل تقييم OpenAI API متعدد النماذج في {elapsed_time:.2f} ثانية")
            
            result = json.loads(response.choices[0].message.content)
            return result
        except Exception as e:
            logging.error(f"خطأ في OpenAI API في التقييم متعدد النماذج: {e}")
            return {
                "grade": "خطأ",
                "feedback": [f"حدث خطأ أثناء تقييم الذكاء الاصطناعي متعدد النماذج: {str(e)}"],
                "visual_elements_feedback": ["لم يتم تقييم العناصر المرئية بسبب خطأ"],
                "improvement_areas": ["حاول مرة أخرى لاحقًا"],
                "criteria_met": {
                    "knowledge": 0,
                    "application": 0,
                    "analysis": 0,
                    "visual_communication": 0,
                    "overall": 0
                },
                "error": True
            }
            
    def analyze_diagram(self, image_path, context=None):
        """
        تحليل مخطط أو رسم بياني وتقديم ملاحظات مفصلة عنه
        
        Args:
            image_path (str): مسار الصورة للمخطط أو الرسم البياني
            context (str, optional): سياق إضافي لفهم المخطط
            
        Returns:
            dict: تحليل مفصل للمخطط
        """
        if not context:
            context = "هذا مخطط أو رسم بياني مقدم كجزء من مهمة BTEC."
        
        if not self.api_key:
            # محاكاة تحليل المخطط
            logging.warning("استخدام تحليل مخطط محاكى (لا يوجد مفتاح API)")
            return {
                "title": "تحليل المخطط المقدم (محاكاة)",
                "summary": "هذا تحليل محاكى للمخطط المقدم.",
                "key_elements": [
                    "عنصر رئيسي 1 في المخطط",
                    "عنصر رئيسي 2 في المخطط",
                    "عنصر رئيسي 3 في المخطط"
                ],
                "accuracy": 75,
                "clarity": 80,
                "relevance": 70,
                "feedback": "المخطط المقدم واضح ومنظم، لكنه يفتقر إلى بعض التفاصيل المهمة.",
                "improvement_suggestions": [
                    "إضافة عناوين أكثر وضوحًا",
                    "تحسين تباين الألوان",
                    "إضافة مفتاح توضيحي"
                ],
                "simulated": True
            }
        
        try:
            # تغيير حجم الصورة إذا لزم الأمر
            resized_path = self.resize_image_if_needed(image_path)
            
            # تشفير الصورة
            base64_image = self.encode_image(resized_path)
            
            # حذف الملف المؤقت إذا تم إنشاؤه
            if resized_path != image_path:
                os.remove(resized_path)
            
            if not base64_image:
                raise Exception("فشل في تشفير الصورة")
            
            # استخدام عميل OpenAI للإصدار 1.0.0+
            client = OpenAI(api_key=self.api_key)
            start_time = time.time()
            
            # إنشاء إكمال الذكاء الاصطناعي لتحليل المخطط
            response = client.chat.completions.create(
                model="gpt-4o", # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
                # do not change this unless explicitly requested by the user
                messages=[
                    {"role": "system", "content": """أنت محلل محترف للمخططات والرسوم البيانية.
                     مهمتك هي تحليل المخطط المقدم وتقديم تقييم مفصل ودقيق عنه.
                     
                     قم بتحليل:
                     1. نوع المخطط والغرض منه
                     2. العناصر الرئيسية والعلاقات بينها
                     3. دقة المعلومات المقدمة
                     4. وضوح العرض وسهولة الفهم
                     5. الصلة بالسياق المقدم
                     
                     أرجع تحليلك بتنسيق JSON التالي:
                     {
                       "title": "عنوان وصفي للمخطط",
                       "summary": "ملخص موجز لما يمثله المخطط",
                       "key_elements": ["عنصر 1", "عنصر 2", "عنصر 3"],
                       "accuracy": 0-100,
                       "clarity": 0-100,
                       "relevance": 0-100,
                       "feedback": "تقييم عام للمخطط",
                       "improvement_suggestions": ["اقتراح 1", "اقتراح 2", "اقتراح 3"]
                     }
                     
                     تأكد من أن تحليلك دقيق وموضوعي ويقدم ملاحظات قيمة.
                     """},
                    {"role": "user", "content": [
                        {
                            "type": "text",
                            "text": f"حلل هذا المخطط وقدم تقييمًا مفصلاً له. السياق: {context}"
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}",
                                "detail": "high"
                            }
                        }
                    ]}
                ],
                response_format={"type": "json_object"},
                max_tokens=1500,
                temperature=0.7
            )
            
            elapsed_time = time.time() - start_time
            logging.info(f"اكتمل تحليل المخطط باستخدام OpenAI API في {elapsed_time:.2f} ثانية")
            
            result = json.loads(response.choices[0].message.content)
            return result
        except Exception as e:
            logging.error(f"خطأ في OpenAI API في تحليل المخطط: {e}")
            return {
                "title": "خطأ في تحليل المخطط",
                "summary": f"حدث خطأ أثناء تحليل المخطط: {str(e)}",
                "key_elements": [],
                "accuracy": 0,
                "clarity": 0,
                "relevance": 0,
                "feedback": "لم يتم تحليل المخطط بسبب خطأ فني.",
                "improvement_suggestions": ["حاول مرة أخرى لاحقًا"],
                "error": True
            }