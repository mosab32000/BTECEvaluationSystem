"""
وحدة تقييم المهام باستخدام الذكاء الاصطناعي
"""
import os
import json
import logging
from app.database import log_audit

class AIEvaluator:
    """
    فئة لتقييم مهام BTEC باستخدام الذكاء الاصطناعي
    """
    def __init__(self):
        self.api_key = os.environ.get('OPENAI_API_KEY')
        if not self.api_key:
            logging.warning("لم يتم العثور على مفتاح OpenAI API. سيتم استخدام وضع المحاكاة.")
            self.simulation_mode = True
        else:
            self.simulation_mode = False
    
    def evaluate_task(self, task_text, rubric=None):
        """
        تقييم مهمة باستخدام الذكاء الاصطناعي
        
        Args:
            task_text (str): نص المهمة المراد تقييمها
            rubric (dict, optional): معايير التقييم المخصصة
            
        Returns:
            dict: نتائج التقييم
        """
        try:
            if self.simulation_mode:
                # وضع المحاكاة عندما لا يكون هناك مفتاح API
                logging.info("استخدام وضع المحاكاة للتقييم")
                return self._simulate_evaluation(task_text, rubric)
            
            # الحصول على توجيه النظام
            system_prompt = self._get_system_prompt(rubric)
            
            # إعداد طلب OpenAI
            import openai
            openai.api_key = self.api_key
            
            # إرسال الطلب إلى OpenAI API
            response = openai.ChatCompletion.create(
                model="gpt-4",  # يمكن استخدام gpt-3.5-turbo للحصول على استجابة أسرع وتكلفة أقل
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": task_text}
                ],
                temperature=0.7,
                max_tokens=2000
            )
            
            # معالجة الاستجابة
            result = response.choices[0].message.content
            
            # محاولة تحليل النتيجة كـ JSON
            try:
                result_json = json.loads(result)
                return result_json
            except json.JSONDecodeError:
                # في حالة عدم توفر JSON، قم بتهيئة هيكل النتائج
                return {
                    "grade": self._extract_grade(result),
                    "feedback": result,
                    "criteria": {}
                }
        
        except Exception as e:
            logging.error(f"خطأ في تقييم المهمة: {str(e)}")
            # تسجيل الخطأ في سجل التدقيق
            log_audit("ai_evaluation_error", "System", str(e))
            
            # إرجاع نتيجة خطأ
            return {
                "error": True,
                "message": f"حدث خطأ أثناء التقييم: {str(e)}",
                "grade": "NA",
                "feedback": "لم يتم إكمال التقييم بسبب خطأ في الخدمة."
            }
    
    def _get_system_prompt(self, rubric=None):
        """
        إنشاء توجيه النظام لنموذج OpenAI استنادًا إلى معايير التقييم
        
        Args:
            rubric (dict, optional): معايير التقييم المخصصة
            
        Returns:
            str: توجيه النظام لنموذج OpenAI
        """
        if rubric:
            # توجيه مخصص استنادًا إلى معايير التقييم المقدمة
            criteria_text = "\n".join([
                f"- {criteria['title']} (الوزن: {criteria['weight']*100}%): {criteria['description']}"
                for key, criteria in rubric['criteria'].items()
            ])
            
            return f"""
            أنت مقيّم خبير لمهام BTEC. مهمتك هي تقييم المهمة المقدمة وفقًا للمعايير التالية:
            
            {criteria_text}
            
            قم بتقييم المهمة وتقديم درجة (Distinction, Merit, Pass, أو Fail) لكل معيار، ثم قدم درجة إجمالية.
            يجب أن تقدم تغذية راجعة مفصلة تشرح نقاط القوة والضعف وكيفية تحسين المهمة.
            
            قم بتنسيق إجابتك كـ JSON بالهيكل التالي:
            {{
                "grade": "الدرجة الإجمالية (Distinction, Merit, Pass, أو Fail)",
                "feedback": "تغذية راجعة عامة حول المهمة",
                "criteria": {{
                    "المعيار1": {{
                        "grade": "درجة المعيار",
                        "feedback": "تغذية راجعة محددة لهذا المعيار"
                    }},
                    ...
                }}
            }}
            """
        else:
            # توجيه قياسي للتقييم العام
            return """
            أنت مقيّم خبير لمهام BTEC. مهمتك هي تقييم المهمة المقدمة وتقديم تغذية راجعة مفصلة.
            
            قم بتقييم المهمة بناءً على المعايير التالية:
            1. المحتوى والفهم (40%): مدى اكتمال ودقة المحتوى وفهم الموضوع
            2. التحليل والتقييم (30%): مستوى التحليل والتفكير النقدي
            3. الهيكل والتنظيم (20%): تنظيم المهمة وتسلسل الأفكار
            4. اللغة والأسلوب (10%): صحة اللغة ووضوح الأسلوب
            
            قم بتنسيق إجابتك كـ JSON بالهيكل التالي:
            {{
                "grade": "الدرجة الإجمالية (Distinction, Merit, Pass, أو Fail)",
                "feedback": "تغذية راجعة عامة حول المهمة",
                "criteria": {{
                    "content": {{
                        "grade": "درجة المعيار",
                        "feedback": "تغذية راجعة محددة لهذا المعيار"
                    }},
                    "analysis": {{
                        "grade": "درجة المعيار",
                        "feedback": "تغذية راجعة محددة لهذا المعيار"
                    }},
                    "structure": {{
                        "grade": "درجة المعيار",
                        "feedback": "تغذية راجعة محددة لهذا المعيار"
                    }},
                    "language": {{
                        "grade": "درجة المعيار",
                        "feedback": "تغذية راجعة محددة لهذا المعيار"
                    }}
                }}
            }}
            """
    
    def _extract_grade(self, text):
        """
        استخراج الدرجة من النص
        """
        grades = ["Distinction", "Merit", "Pass", "Fail"]
        for grade in grades:
            if grade.lower() in text.lower():
                return grade
        return "NA"
    
    def _convert_grade_to_numerical(self, grade):
        """
        تحويل التقدير النصي إلى قيمة رقمية
        
        Args:
            grade (str): التقدير النصي
            
        Returns:
            float: القيمة الرقمية للتقدير
        """
        grade_map = {
            "Distinction": 4.0,
            "Merit": 3.0,
            "Pass": 2.0,
            "Fail": 0.0,
            "NA": 0.0
        }
        
        return grade_map.get(grade, 0.0)
    
    def _simulate_evaluation(self, task_text, rubric=None):
        """
        محاكاة تقييم المهمة (للاستخدام عندما لا يكون هناك مفتاح API)
        """
        # تقييم بسيط بناءً على طول المهمة
        word_count = len(task_text.split())
        
        if word_count < 100:
            grade = "Fail"
            feedback = "المهمة قصيرة جدًا ولا تلبي الحد الأدنى من المتطلبات."
        elif word_count < 300:
            grade = "Pass"
            feedback = "المهمة تلبي الحد الأدنى من المتطلبات ولكنها تفتقر إلى العمق والتحليل."
        elif word_count < 600:
            grade = "Merit"
            feedback = "المهمة جيدة مع تحليل مناسب ولكن يمكن تحسينها."
        else:
            grade = "Distinction"
            feedback = "المهمة ممتازة مع تحليل عميق ومحتوى شامل."
        
        # إنشاء نتيجة التقييم
        result = {
            "grade": grade,
            "feedback": feedback,
            "criteria": {}
        }
        
        # إضافة تقييم المعايير إذا تم توفير معايير
        if rubric:
            for key, criteria in rubric['criteria'].items():
                result["criteria"][key] = {
                    "grade": grade,
                    "feedback": f"تقييم {criteria['title']}: {feedback}"
                }
        else:
            # معايير افتراضية
            result["criteria"] = {
                "content": {
                    "grade": grade,
                    "feedback": f"المحتوى والفهم: {feedback}"
                },
                "analysis": {
                    "grade": grade,
                    "feedback": f"التحليل والتقييم: {feedback}"
                },
                "structure": {
                    "grade": grade,
                    "feedback": f"الهيكل والتنظيم: {feedback}"
                },
                "language": {
                    "grade": grade,
                    "feedback": f"اللغة والأسلوب: {feedback}"
                }
            }
        
        return result
