"""
وحدة تقييم المهام باستخدام الذكاء الاصطناعي
"""

import json
import os
import requests
from flask import current_app

class AIEvaluator:
    """
    فئة لتقييم مهام BTEC باستخدام الذكاء الاصطناعي
    """
    def __init__(self):
        self.api_key = os.environ.get('OPENAI_API_KEY') or current_app.config.get('OPENAI_API_KEY')
        if not self.api_key:
            current_app.logger.error("مفتاح API غير متوفر لخدمة OpenAI")
            raise ValueError("مفتاح API غير متوفر لخدمة OpenAI")
        
        self.api_url = "https://api.openai.com/v1/chat/completions"
        self.model = "gpt-4"  # أو أي نموذج آخر متاح
    
    def evaluate_task(self, task_text, rubric=None):
        """
        تقييم مهمة باستخدام الذكاء الاصطناعي
        
        Args:
            task_text (str): نص المهمة المراد تقييمها
            rubric (dict, optional): معايير التقييم المخصصة
            
        Returns:
            dict: نتائج التقييم
        """
        # إعداد الرسالة لنموذج OpenAI
        messages = [
            {"role": "system", "content": self._get_system_prompt(rubric)},
            {"role": "user", "content": task_text}
        ]
        
        # إرسال الطلب إلى OpenAI
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": self.model,
            "messages": messages,
            "temperature": 0.3,  # درجة إبداعية منخفضة للحصول على نتائج متسقة
            "max_tokens": 2000,
            "response_format": {"type": "json_object"}  # طلب استجابة بتنسيق JSON
        }
        
        try:
            response = requests.post(self.api_url, headers=headers, json=data)
            response.raise_for_status()
            response_data = response.json()
            
            # استخراج الرد من OpenAI
            ai_response = response_data["choices"][0]["message"]["content"]
            
            # تحليل استجابة JSON
            evaluation_result = json.loads(ai_response)
            
            # إضافة الدرجة العددية إذا لم تكن موجودة
            if "grade_numerical" not in evaluation_result and "grade" in evaluation_result:
                evaluation_result["grade_numerical"] = self._convert_grade_to_numerical(evaluation_result["grade"])
            
            return evaluation_result
        
        except Exception as e:
            current_app.logger.error(f"خطأ في تقييم المهمة: {str(e)}")
            raise ValueError(f"حدث خطأ أثناء تقييم المهمة: {str(e)}")
    
    def _get_system_prompt(self, rubric=None):
        """
        إنشاء توجيه النظام لنموذج OpenAI استنادًا إلى معايير التقييم
        
        Args:
            rubric (dict, optional): معايير التقييم المخصصة
            
        Returns:
            str: توجيه النظام لنموذج OpenAI
        """
        base_prompt = """
        أنت مقيم BTEC خبير. مهمتك هي تقييم مهمة BTEC وتقديم تعليقات مفصلة.
        
        يجب أن تقيم المهمة وفقًا لمعايير BTEC القياسية وتعيد النتائج بتنسيق JSON.
        
        قدّم ردًا يتضمن العناصر التالية:
        1. "grade": تصنيف عام وفقًا لنظام BTEC (Pass, Merit, Distinction, أو Fail)
        2. "grade_numerical": قيمة رقمية للدرجة من 0 إلى 100
        3. "feedback": ملاحظات تفصيلية حول المهمة تشرح نقاط القوة والضعف
        4. "rubric_results": تقييم تفصيلي لكل معيار من معايير التقييم
        
        قدم تقييمًا عادلًا وموضوعيًا وشاملًا.
        """
        
        if rubric:
            # تضمين معايير التقييم المخصصة في التوجيه
            rubric_prompt = "\n\nيجب عليك تقييم المهمة وفقًا لمعايير التقييم التالية:\n"
            
            for criterion, details in rubric.items():
                # استخراج الوزن ووصف المعيار إذا وجد
                weight = details.get("weight", 0)
                description = details.get("description", "")
                
                rubric_prompt += f"- {criterion} (الوزن: {weight}%): {description}\n"
            
            rubric_prompt += "\nلكل معيار، قدم درجة وملاحظات مفصلة."
            
            return base_prompt + rubric_prompt
        
        return base_prompt
    
    def _convert_grade_to_numerical(self, grade):
        """
        تحويل التقدير النصي إلى قيمة رقمية
        
        Args:
            grade (str): التقدير النصي
            
        Returns:
            float: القيمة الرقمية للتقدير
        """
        grade = grade.lower()
        
        if "distinction" in grade:
            return 85.0
        elif "merit" in grade:
            return 70.0
        elif "pass" in grade:
            return 55.0
        else:
            return 30.0  # Fail
