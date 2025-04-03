"""
خدمة تقييم الذكاء الاصطناعي المتقدمة في نظام تقييم BTEC
تركز على تقييم مشاريع برمجية أكثر تعقيدًا وتوفر قدرات تحليل شاملة
"""

from openai import OpenAI
from flask import current_app
import logging
import json
import time
import os
import re
import base64
import tempfile
from pathlib import Path

class AIEvaluatorAdvanced:
    """
    مُقيِّم الذكاء الاصطناعي المتقدم لتحليل وتقييم المشاريع البرمجية والمهام المعقدة
    """
    
    def __init__(self):
        """تهيئة المُقيِّم باستخدام مفتاح OpenAI API"""
        api_key = current_app.config.get('OPENAI_API_KEY')
        if not api_key:
            logging.warning("لم يتم تكوين OPENAI_API_KEY. سيتم محاكاة التقييم المتقدم.")
            self.api_key = None
        else:
            self.api_key = api_key
            logging.info("تم تهيئة مُقيِّم الذكاء الاصطناعي المتقدم بمفتاح API صالح")

    def evaluate_code_project(self, project_files, project_description):
        """
        تقييم مشروع برمجي كامل يتكون من ملفات متعددة
        
        Args:
            project_files (dict): قاموس بمسارات الملفات ومحتوياتها
            project_description (str): وصف المشروع والمهمة المطلوبة
            
        Returns:
            dict: تقييم شامل للمشروع مع ملاحظات مفصلة
        """
        if not self.api_key:
            # محاكاة تقييم المشروع البرمجي
            logging.warning("استخدام تقييم محاكى للمشروع البرمجي (لا يوجد مفتاح API)")
            return {
                "grade": "جيد",
                "overall_score": 75,
                "summary": "هذا تقييم محاكى للمشروع البرمجي المقدم.",
                "code_quality": {
                    "score": 70,
                    "strengths": ["الكود منظم بشكل جيد", "استخدام التعليقات بشكل مناسب"],
                    "weaknesses": ["بعض التكرار في الكود", "يمكن تحسين معالجة الأخطاء"]
                },
                "functionality": {
                    "score": 80,
                    "working_features": ["المزايا الأساسية تعمل بشكل صحيح", "واجهة المستخدم مستجيبة"],
                    "issues": ["بعض حالات الحافة غير معالجة"]
                },
                "documentation": {
                    "score": 75,
                    "feedback": "التوثيق كافٍ ولكن يمكن تحسينه"
                },
                "innovation": {
                    "score": 65,
                    "feedback": "يظهر المشروع فهمًا جيدًا للمفاهيم ولكن مع ابتكار محدود"
                },
                "file_specific_feedback": {
                    "main.py": "الملف منظم بشكل جيد لكن يمكن تحسين التعليقات",
                    "utils.py": "وظائف مساعدة مفيدة، يمكن إضافة اختبارات إضافية"
                },
                "improvement_suggestions": [
                    "تحسين معالجة الأخطاء في جميع الملفات",
                    "إضافة اختبارات وحدة للوظائف الرئيسية",
                    "تحسين التوثيق بإضافة أمثلة للاستخدام"
                ],
                "simulated": True
            }
        
        try:
            # تحضير محتوى الملفات للتقييم
            files_content = "\n\n".join([
                f"### {file_path} ###\n```\n{content}\n```"
                for file_path, content in project_files.items()
            ])
            
            # استخدام عميل OpenAI للإصدار 1.0.0+
            client = OpenAI(api_key=self.api_key)
            start_time = time.time()
            
            # إنشاء إكمال الذكاء الاصطناعي لتقييم المشروع
            response = client.chat.completions.create(
                model="gpt-4o", # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
                # do not change this unless explicitly requested by the user
                messages=[
                    {"role": "system", "content": """أنت خبير تقييم مشاريع برمجية BTEC.
                     مهمتك هي تحليل وتقييم كود المشروع المقدم بناءً على وصف المشروع والمعايير التالية:
                     
                     1. جودة الكود (التنظيم، الأسلوب، الكفاءة)
                     2. الوظائف (المزايا العاملة والمشكلات)
                     3. التوثيق (التعليقات، الأسماء المعبرة، الوضوح)
                     4. الابتكار (الإبداع، استخدام التقنيات الحديثة)
                     
                     قم بتصنيف المشروع كـ: مقبول، جيد، أو ممتاز.
                     
                     قدم تقييمك بتنسيق JSON التالي:
                     {
                       "grade": "مقبول/جيد/ممتاز",
                       "overall_score": 0-100,
                       "summary": "ملخص عام للتقييم",
                       "code_quality": {
                         "score": 0-100,
                         "strengths": ["نقطة قوة 1", "نقطة قوة 2"],
                         "weaknesses": ["نقطة ضعف 1", "نقطة ضعف 2"]
                       },
                       "functionality": {
                         "score": 0-100,
                         "working_features": ["ميزة 1", "ميزة 2"],
                         "issues": ["مشكلة 1", "مشكلة 2"]
                       },
                       "documentation": {
                         "score": 0-100,
                         "feedback": "ملاحظات حول التوثيق"
                       },
                       "innovation": {
                         "score": 0-100,
                         "feedback": "ملاحظات حول الابتكار"
                       },
                       "file_specific_feedback": {
                         "اسم_الملف_1": "ملاحظات خاصة بالملف",
                         "اسم_الملف_2": "ملاحظات خاصة بالملف"
                       },
                       "improvement_suggestions": [
                         "اقتراح 1", "اقتراح 2", "اقتراح 3"
                       ]
                     }
                     
                     تأكد من أن تقييمك محدد ومفصل ويوفر ملاحظات عملية للتحسين.
                     """},
                    {"role": "user", "content": f"وصف المشروع:\n{project_description}\n\nملفات المشروع:\n{files_content}"}
                ],
                response_format={"type": "json_object"},
                max_tokens=4000,
                temperature=0.7
            )
            
            elapsed_time = time.time() - start_time
            logging.info(f"اكتمل تقييم المشروع البرمجي باستخدام OpenAI API في {elapsed_time:.2f} ثانية")
            
            result = json.loads(response.choices[0].message.content)
            return result
        except Exception as e:
            logging.error(f"خطأ في OpenAI API أثناء تقييم المشروع البرمجي: {e}")
            return {
                "grade": "خطأ",
                "overall_score": 0,
                "summary": f"حدث خطأ أثناء تقييم المشروع: {str(e)}",
                "code_quality": {"score": 0, "strengths": [], "weaknesses": []},
                "functionality": {"score": 0, "working_features": [], "issues": []},
                "documentation": {"score": 0, "feedback": ""},
                "innovation": {"score": 0, "feedback": ""},
                "file_specific_feedback": {},
                "improvement_suggestions": ["حاول مرة أخرى لاحقًا"],
                "error": True
            }
            
    def evaluate_database_design(self, er_diagram_path, schema_definition):
        """
        تقييم تصميم قاعدة البيانات باستخدام مخطط ER والتعريف النصي للمخطط
        
        Args:
            er_diagram_path (str): مسار ملف مخطط ER
            schema_definition (str): تعريف نصي لمخطط قاعدة البيانات (SQL DDL أو وصف)
            
        Returns:
            dict: تقييم شامل لتصميم قاعدة البيانات
        """
        if not self.api_key:
            # محاكاة تقييم تصميم قاعدة البيانات
            logging.warning("استخدام تقييم محاكى لتصميم قاعدة البيانات (لا يوجد مفتاح API)")
            return {
                "grade": "جيد",
                "overall_score": 75,
                "summary": "هذا تقييم محاكى لتصميم قاعدة البيانات المقدم.",
                "design_quality": {
                    "score": 80,
                    "strengths": ["تصميم منطقي للعلاقات", "التحقق من سلامة البيانات"],
                    "weaknesses": ["بعض المشكلات في التطبيع", "يمكن تحسين تصميم المفاتيح الأجنبية"]
                },
                "normalization": {
                    "score": 70,
                    "level": "3NF",
                    "issues": ["بعض الجداول لا تلبي متطلبات 3NF"]
                },
                "performance": {
                    "score": 75,
                    "feedback": "التصميم يدعم معظم استعلامات النظام لكن قد تكون هناك مشكلات أداء مع البيانات الكبيرة"
                },
                "diagram_quality": {
                    "score": 80,
                    "feedback": "المخطط واضح ومنظم بشكل عام"
                },
                "improvement_suggestions": [
                    "تطبيق قواعد التطبيع على جدول X",
                    "إضافة فهارس للاستعلامات الشائعة",
                    "تحسين تصميم المفاتيح الأجنبية للحفاظ على سلامة البيانات"
                ],
                "simulated": True
            }
        
        try:
            # تشفير مخطط ER
            er_base64 = None
            if er_diagram_path and os.path.exists(er_diagram_path):
                with open(er_diagram_path, "rb") as img_file:
                    er_base64 = base64.b64encode(img_file.read()).decode('utf-8')
            
            # تحضير المحتوى للتقييم
            content_parts = []
            
            # إضافة النص الوصفي
            content_parts.append({
                "type": "text",
                "text": f"قيّم تصميم قاعدة البيانات التالي:\n\nتعريف المخطط:\n{schema_definition}"
            })
            
            # إضافة المخطط إذا كان متاحًا
            if er_base64:
                content_parts.append({
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{er_base64}",
                        "detail": "high"
                    }
                })
            
            # استخدام عميل OpenAI للإصدار 1.0.0+
            client = OpenAI(api_key=self.api_key)
            start_time = time.time()
            
            # إنشاء إكمال الذكاء الاصطناعي لتقييم تصميم قاعدة البيانات
            response = client.chat.completions.create(
                model="gpt-4o", # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
                # do not change this unless explicitly requested by the user
                messages=[
                    {"role": "system", "content": """أنت خبير في تصميم قواعد البيانات وتقييمها لمشاريع BTEC.
                     مهمتك هي تحليل وتقييم تصميم قاعدة البيانات المقدم بناءً على المعايير التالية:
                     
                     1. جودة التصميم (العلاقات، القيود، التماسك)
                     2. التطبيع (مستوى التطبيع، تجنب التكرار)
                     3. الأداء (دعم الاستعلامات، الفهارس، التحسين)
                     4. جودة المخطط (الوضوح، التنظيم، الاكتمال)
                     
                     قم بتصنيف التصميم كـ: مقبول، جيد، أو ممتاز.
                     
                     قدم تقييمك بتنسيق JSON التالي:
                     {
                       "grade": "مقبول/جيد/ممتاز",
                       "overall_score": 0-100,
                       "summary": "ملخص عام للتقييم",
                       "design_quality": {
                         "score": 0-100,
                         "strengths": ["نقطة قوة 1", "نقطة قوة 2"],
                         "weaknesses": ["نقطة ضعف 1", "نقطة ضعف 2"]
                       },
                       "normalization": {
                         "score": 0-100,
                         "level": "1NF/2NF/3NF/BCNF",
                         "issues": ["مشكلة 1", "مشكلة 2"]
                       },
                       "performance": {
                         "score": 0-100,
                         "feedback": "ملاحظات حول الأداء"
                       },
                       "diagram_quality": {
                         "score": 0-100,
                         "feedback": "ملاحظات حول جودة المخطط"
                       },
                       "improvement_suggestions": [
                         "اقتراح 1", "اقتراح 2", "اقتراح 3"
                       ]
                     }
                     
                     تأكد من أن تقييمك محدد ومفصل ويوفر ملاحظات عملية للتحسين.
                     """},
                    {"role": "user", "content": content_parts}
                ],
                response_format={"type": "json_object"},
                max_tokens=3000,
                temperature=0.7
            )
            
            elapsed_time = time.time() - start_time
            logging.info(f"اكتمل تقييم تصميم قاعدة البيانات باستخدام OpenAI API في {elapsed_time:.2f} ثانية")
            
            result = json.loads(response.choices[0].message.content)
            return result
        except Exception as e:
            logging.error(f"خطأ في OpenAI API أثناء تقييم تصميم قاعدة البيانات: {e}")
            return {
                "grade": "خطأ",
                "overall_score": 0,
                "summary": f"حدث خطأ أثناء تقييم تصميم قاعدة البيانات: {str(e)}",
                "design_quality": {"score": 0, "strengths": [], "weaknesses": []},
                "normalization": {"score": 0, "level": "غير محدد", "issues": []},
                "performance": {"score": 0, "feedback": ""},
                "diagram_quality": {"score": 0, "feedback": ""},
                "improvement_suggestions": ["حاول مرة أخرى لاحقًا"],
                "error": True
            }

    def analyze_code_segment(self, code, language, assessment_criteria=None):
        """
        تحليل مقطع برمجي محدد وتقييمه وفقًا لمعايير التقييم
        
        Args:
            code (str): الكود المراد تحليله
            language (str): لغة البرمجة (مثل Python، Java، إلخ)
            assessment_criteria (dict, optional): معايير التقييم المخصصة
            
        Returns:
            dict: تحليل مفصل للكود مع اقتراحات التحسين
        """
        if not assessment_criteria:
            assessment_criteria = {
                "efficiency": {"weight": 25, "description": "كفاءة الكود من حيث الوقت والذاكرة"},
                "readability": {"weight": 25, "description": "سهولة قراءة وفهم الكود"},
                "functionality": {"weight": 30, "description": "أداء الوظائف المطلوبة بشكل صحيح"},
                "best_practices": {"weight": 20, "description": "اتباع أفضل الممارسات في لغة البرمجة"}
            }
        
        if not self.api_key:
            # محاكاة تحليل الكود
            logging.warning("استخدام تحليل محاكى للكود (لا يوجد مفتاح API)")
            return {
                "grade": "جيد",
                "overall_score": 72,
                "summary": "هذا تحليل محاكى لمقطع الكود المقدم.",
                "criteria_scores": {
                    "efficiency": {"score": 70, "feedback": "الكود يعمل بكفاءة مقبولة، لكن هناك مجال للتحسين"},
                    "readability": {"score": 75, "feedback": "الكود منظم بشكل جيد، مع تعليقات كافية"},
                    "functionality": {"score": 80, "feedback": "الكود يؤدي الوظائف المطلوبة بشكل صحيح"},
                    "best_practices": {"score": 60, "feedback": "بعض الانحرافات عن أفضل الممارسات"}
                },
                "issues": [
                    {"line": 5, "severity": "متوسط", "description": "استخدام متغير غير ضروري"},
                    {"line": 12, "severity": "منخفض", "description": "يمكن تبسيط الشرط"}
                ],
                "improvement_suggestions": [
                    "استخدام تعابير أكثر كفاءة في السطر 5",
                    "تحسين أسماء المتغيرات لتكون أكثر وصفية",
                    "إضافة معالجة للاستثناءات"
                ],
                "simulated": True
            }
        
        try:
            # استخدام عميل OpenAI للإصدار 1.0.0+
            client = OpenAI(api_key=self.api_key)
            start_time = time.time()
            
            # إنشاء إكمال الذكاء الاصطناعي لتحليل الكود
            response = client.chat.completions.create(
                model="gpt-4o", # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
                # do not change this unless explicitly requested by the user
                messages=[
                    {"role": "system", "content": f"""أنت محلل كود خبير متخصص في لغة {language}.
                     مهمتك هي تحليل وتقييم مقطع الكود المقدم بناءً على المعايير التالية:
                     
                     {json.dumps(assessment_criteria, ensure_ascii=False, indent=2)}
                     
                     قم بتصنيف الكود كـ: مقبول، جيد، أو ممتاز.
                     
                     قدم تحليلك بتنسيق JSON التالي:
                     {{
                       "grade": "مقبول/جيد/ممتاز",
                       "overall_score": 0-100,
                       "summary": "ملخص عام للتحليل",
                       "criteria_scores": {{
                         "معيار1": {{ "score": 0-100, "feedback": "ملاحظات" }},
                         "معيار2": {{ "score": 0-100, "feedback": "ملاحظات" }},
                         ...
                       }},
                       "issues": [
                         {{ "line": رقم_السطر, "severity": "مرتفع/متوسط/منخفض", "description": "وصف المشكلة" }},
                         ...
                       ],
                       "improvement_suggestions": [
                         "اقتراح 1", "اقتراح 2", "اقتراح 3"
                       ]
                     }}
                     
                     تأكد من تقديم تحليل دقيق ومفصل مع اقتراحات عملية للتحسين.
                     """},
                    {"role": "user", "content": f"قم بتحليل وتقييم مقطع الكود التالي بلغة {language}:\n\n```{language}\n{code}\n```"}
                ],
                response_format={"type": "json_object"},
                max_tokens=2500,
                temperature=0.7
            )
            
            elapsed_time = time.time() - start_time
            logging.info(f"اكتمل تحليل الكود باستخدام OpenAI API في {elapsed_time:.2f} ثانية")
            
            result = json.loads(response.choices[0].message.content)
            return result
        except Exception as e:
            logging.error(f"خطأ في OpenAI API أثناء تحليل الكود: {e}")
            return {
                "grade": "خطأ",
                "overall_score": 0,
                "summary": f"حدث خطأ أثناء تحليل الكود: {str(e)}",
                "criteria_scores": {},
                "issues": [],
                "improvement_suggestions": ["حاول مرة أخرى لاحقًا"],
                "error": True
            }