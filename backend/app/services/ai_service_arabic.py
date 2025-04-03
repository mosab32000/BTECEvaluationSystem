"""
خدمة تقييم الذكاء الاصطناعي المخصصة للغة العربية في نظام تقييم BTEC
"""

from openai import OpenAI
from flask import current_app
import logging
import json
import time

class AIEvaluatorArabic:
    """
    مُقيِّم الذكاء الاصطناعي المتخصص بتقييم المهام باللغة العربية
    """
    
    def __init__(self):
        """تهيئة المُقيِّم باستخدام مفتاح OpenAI API"""
        api_key = current_app.config.get('OPENAI_API_KEY')
        if not api_key:
            logging.warning("لم يتم تكوين OPENAI_API_KEY. سيتم محاكاة التقييم.")
            self.api_key = None
        else:
            self.api_key = api_key
            logging.info("تم تهيئة مُقيِّم الذكاء الاصطناعي باللغة العربية بمفتاح API صالح")

    def evaluate(self, task_submission):
        """
        تقييم مهمة BTEC المقدمة باللغة العربية
        يعيد درجة وملاحظات مفصلة بتنسيق نصي
        
        Args:
            task_submission (str): نص المهمة المقدمة للتقييم
            
        Returns:
            str: نص التقييم المنسق مع الدرجة والملاحظات
        """
        if not self.api_key:
            # محاكاة تقييم الذكاء الاصطناعي إذا لم يكن مفتاح API متاحًا
            logging.warning("استخدام تقييم ذكاء اصطناعي محاكى (لا يوجد مفتاح API)")
            return (
                "الدرجة: جيد جدًا\n\n"
                "الملاحظات:\n"
                "• هذا تقييم محاكى لأن مفتاح OpenAI API غير متوفر.\n"
                "• يُظهر العمل المقدم فهمًا جيدًا للموضوع.\n"
                "• تم شرح بعض المفاهيم الأساسية بشكل جيد ولكنها تفتقر إلى العمق.\n\n"
                "مجالات التحسين:\n"
                "• إضافة المزيد من التحليل النقدي\n"
                "• تضمين المزيد من الأمثلة العملية\n"
                "• التوسع في الأطر النظرية"
            )
        
        try:
            # استخدام عميل OpenAI للإصدار 1.0.0+
            client = OpenAI(api_key=self.api_key)
            start_time = time.time()
            
            # إنشاء إكمال الذكاء الاصطناعي باستخدام ChatGPT
            response = client.chat.completions.create(
                model="gpt-4o", # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
                # do not change this unless explicitly requested by the user
                messages=[
                    {"role": "system", "content": """أنت مقيّم BTEC خبير في المؤهلات المهنية البريطانية.
                     قم بتقييم الأعمال المقدمة وتصنيفها بدقة كـ: مقبول، جيد، أو ممتاز بناءً على معايير BTEC.
                     
                     اتبع إرشادات تقييم BTEC التالية:
                     - مقبول: فهم أساسي، يلبي الحد الأدنى من المتطلبات، تحليل محدود
                     - جيد: فهم جيد، هيكل جيد، بعض التحليل النقدي، تطبيق جيد للنظرية
                     - ممتاز: فهم ممتاز، شامل، تحليل نقدي عميق، تطبيق إبداعي للنظرية على الممارسة
                     
                     نسّق ردك بالضبط كما يلي:
                     
                     الدرجة: [مقبول/جيد/ممتاز]
                     
                     الملاحظات:
                     • [نقطة رئيسية 1]
                     • [نقطة رئيسية 2]
                     • [نقطة رئيسية 3]
                     • [نقطة رئيسية 4]
                     
                     مجالات التحسين:
                     • [تحسين 1]
                     • [تحسين 2]
                     • [تحسين 3]
                     
                     تأكد من أن ملاحظاتك محددة وقابلة للتنفيذ ومتوافقة مع معايير BTEC."""},
                    {"role": "user", "content": f"قيّم مهمة BTEC التالية:\n\n{task_submission}"}
                ],
                max_tokens=1500,
                temperature=0.7
            )
            
            elapsed_time = time.time() - start_time
            logging.info(f"اكتمل تقييم OpenAI API في {elapsed_time:.2f} ثانية")
            
            return response.choices[0].message.content.strip()
        except Exception as e:
            logging.error(f"خطأ في OpenAI API: {e}")
            return f"حدث خطأ أثناء تقييم الذكاء الاصطناعي: {str(e)}"
            
    def evaluate_with_json(self, task_submission):
        """
        تقييم مهمة BTEC المقدمة باللغة العربية وإرجاع استجابة JSON منظمة
        
        Args:
            task_submission (str): نص المهمة المقدمة للتقييم
            
        Returns:
            dict: تقييم منظم مع الدرجة والملاحظات ومجالات التحسين
        """
        if not self.api_key:
            # محاكاة تقييم الذكاء الاصطناعي إذا لم يكن مفتاح API متاحًا
            logging.warning("استخدام تقييم ذكاء اصطناعي محاكى (لا يوجد مفتاح API)")
            return {
                "grade": "جيد",
                "feedback": [
                    "هذا تقييم محاكى لأن مفتاح OpenAI API غير متوفر.",
                    "يُظهر العمل المقدم فهمًا جيدًا للموضوع.",
                    "تم شرح بعض المفاهيم الأساسية بشكل جيد ولكنها تفتقر إلى العمق."
                ],
                "improvement_areas": [
                    "إضافة المزيد من التحليل النقدي",
                    "تضمين المزيد من الأمثلة العملية",
                    "التوسع في الأطر النظرية"
                ],
                "criteria_met": {
                    "knowledge": 80,
                    "application": 75,
                    "analysis": 65,
                    "evaluation": 60
                }
            }
        
        try:
            # استخدام عميل OpenAI للإصدار 1.0.0+
            client = OpenAI(api_key=self.api_key)
            start_time = time.time()
            
            # إنشاء إكمال الذكاء الاصطناعي باستخدام ChatGPT مع مخرجات JSON
            response = client.chat.completions.create(
                model="gpt-4o", # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
                # do not change this unless explicitly requested by the user
                messages=[
                    {"role": "system", "content": """أنت مقيّم BTEC خبير في المؤهلات المهنية البريطانية.
                     قم بتقييم الأعمال المقدمة وتصنيفها بدقة كـ: مقبول، جيد، أو ممتاز بناءً على معايير BTEC.
                     
                     اتبع إرشادات تقييم BTEC التالية:
                     - مقبول: فهم أساسي، يلبي الحد الأدنى من المتطلبات، تحليل محدود (50-59%)
                     - جيد: فهم جيد، هيكل جيد، بعض التحليل النقدي (60-79%)
                     - ممتاز: فهم ممتاز، شامل، تحليل نقدي عميق (80-100%)
                     
                     أرجع تقييمك بتنسيق JSON التالي:
                     {
                       "grade": "مقبول/جيد/ممتاز",
                       "feedback": ["نقطة 1", "نقطة 2", "نقطة 3", "نقطة 4"],
                       "improvement_areas": ["مجال 1", "مجال 2", "مجال 3"],
                       "criteria_met": {
                         "knowledge": 0-100,
                         "application": 0-100,
                         "analysis": 0-100,
                         "evaluation": 0-100
                       }
                     }
                     
                     تأكد من أن ملاحظاتك محددة وقابلة للتنفيذ ومتوافقة مع معايير BTEC.
                     يجب أن تعكس النسب المئوية في criteria_met الأداء في كل مجال من 0 إلى 100.
                     """}, 
                    {"role": "user", "content": f"قيّم مهمة BTEC التالية:\n\n{task_submission}"}
                ],
                response_format={"type": "json_object"},
                max_tokens=1500,
                temperature=0.7
            )
            
            elapsed_time = time.time() - start_time
            logging.info(f"اكتمل تقييم OpenAI API بتنسيق JSON في {elapsed_time:.2f} ثانية")
            
            result = json.loads(response.choices[0].message.content)
            return result
        except Exception as e:
            logging.error(f"خطأ في OpenAI API في تقييم JSON: {e}")
            return {
                "grade": "خطأ",
                "feedback": [f"حدث خطأ أثناء تقييم الذكاء الاصطناعي: {str(e)}"],
                "improvement_areas": ["حاول مرة أخرى لاحقًا"],
                "criteria_met": {
                    "knowledge": 0,
                    "application": 0,
                    "analysis": 0,
                    "evaluation": 0
                }
            }
    
    def evaluate_with_rubric(self, task_submission, rubric=None):
        """
        تقييم عمل مقدم باستخدام معيار محدد
        
        Args:
            task_submission (str): نص العمل المقدم للتقييم
            rubric (dict, optional): معيار تقييم مخصص. إذا كان None، يتم استخدام معيار BTEC الافتراضي.
            
        Returns:
            dict: تقييم مفصل مع درجات لكل معيار تقييم
        """
        if not rubric:
            # معيار BTEC الافتراضي باللغة العربية
            rubric = {
                "sections": [
                    {
                        "name": "المعرفة والفهم",
                        "weight": 25,
                        "criteria": ["استخدام دقيق للمفاهيم", "تغطية المواضيع الرئيسية", "عمق الفهم"]
                    },
                    {
                        "name": "تطبيق النظرية",
                        "weight": 25,
                        "criteria": ["أمثلة ذات صلة", "التطبيق العملي", "سياق الصناعة"]
                    },
                    {
                        "name": "التحليل",
                        "weight": 25,
                        "criteria": ["التفكير النقدي", "تقييم الأدلة", "الحجج المنطقية"]
                    },
                    {
                        "name": "التواصل",
                        "weight": 25,
                        "criteria": ["الهيكل", "الوضوح", "الكتابة الأكاديمية"]
                    }
                ]
            }
            
        if not self.api_key:
            # محاكاة تقييم الذكاء الاصطناعي باستخدام معيار
            logging.warning("استخدام تقييم ذكاء اصطناعي محاكى مع معيار (لا يوجد مفتاح API)")
            
            # توليد درجات محاكاة لكل قسم
            sections_result = []
            total_score = 0
            
            for section in rubric["sections"]:
                section_score = min(85, max(60, 70 + hash(section["name"]) % 20))  # درجة شبه عشوائية ولكن ثابتة
                criteria_scores = {}
                
                for criterion in section["criteria"]:
                    criteria_scores[criterion] = min(90, max(55, section_score + hash(criterion) % 15))
                
                section_result = {
                    "name": section["name"],
                    "score": section_score,
                    "criteria_scores": criteria_scores,
                    "feedback": f"ملاحظات محاكاة لـ {section['name']}"
                }
                sections_result.append(section_result)
                total_score += section_score * section["weight"] / 100
            
            # تحديد الدرجة بناءً على الدرجة الكلية
            grade = "مقبول"
            if total_score >= 80:
                grade = "ممتاز"
            elif total_score >= 60:
                grade = "جيد"
                
            return {
                "grade": grade,
                "total_score": round(total_score, 1),
                "sections": sections_result,
                "overall_feedback": "هذا تقييم محاكى قائم على معيار (لا يوجد مفتاح API)",
                "simulated": True
            }
            
        try:
            # تحويل المعيار إلى تنسيق سلسلة للموجه
            rubric_str = json.dumps(rubric, indent=2, ensure_ascii=False)
            client = OpenAI(api_key=self.api_key)
            start_time = time.time()
            
            response = client.chat.completions.create(
                model="gpt-4o", # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
                # do not change this unless explicitly requested by the user
                messages=[
                    {"role": "system", "content": f"""أنت مقيّم BTEC يستخدم معيارًا محددًا لتقييم الأعمال المقدمة.
                     
                     استخدم معيار التقييم هذا:
                     {rubric_str}
                     
                     لكل قسم:
                     1. قيّم العمل المقدم مقابل كل معيار
                     2. قدم درجة من 0-100 لكل معيار
                     3. احسب درجة إجمالية للقسم (متوسط المعايير)
                     4. قدم ملاحظات محددة للقسم
                     
                     احسب الدرجة النهائية كمتوسط مرجح لدرجات الأقسام.
                     
                     حدد الدرجة على النحو التالي:
                     - ممتاز: 80-100
                     - جيد: 60-79
                     - مقبول: 40-59
                     - راسب: 0-39
                     
                     أرجع تقييمك ككائن JSON بهذه البنية:
                     {{
                       "grade": "مقبول/جيد/ممتاز/راسب",
                       "total_score": رقم (0-100),
                       "sections": [
                         {{
                           "name": "اسم القسم",
                           "score": رقم (0-100),
                           "criteria_scores": {{ "معيار1": درجة, "معيار2": درجة, ... }},
                           "feedback": "ملاحظات محددة لهذا القسم"
                         }},
                         ...
                       ],
                       "overall_feedback": "ملاحظات ملخصة تتناول نقاط القوة والضعف"
                     }}
                     """}, 
                    {"role": "user", "content": f"قيّم العمل المقدم التالي باستخدام المعيار المقدم:\n\n{task_submission}"}
                ],
                response_format={"type": "json_object"},
                max_tokens=2000,
                temperature=0.7
            )
            
            elapsed_time = time.time() - start_time
            logging.info(f"اكتمل تقييم المعيار باستخدام OpenAI API في {elapsed_time:.2f} ثانية")
            
            result = json.loads(response.choices[0].message.content)
            return result
        except Exception as e:
            logging.error(f"خطأ في OpenAI API في تقييم المعيار: {e}")
            return {
                "grade": "خطأ",
                "total_score": 0,
                "sections": [],
                "overall_feedback": f"حدث خطأ أثناء تقييم الذكاء الاصطناعي: {str(e)}",
                "error": True
            }