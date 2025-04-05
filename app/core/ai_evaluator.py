"""
مقيم الذكاء الاصطناعي للتقييمات في نظام تقييم BTEC
"""
import os
import json
import logging
import math
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Union, Any

import openai
from flask import current_app

# إعداد التسجيل
logger = logging.getLogger(__name__)

class AIEvaluator(ABC):
    """
    الصف الأساسي لمقيم الذكاء الاصطناعي.
    
    يوفر واجهة موحدة لتقييم النصوص باستخدام الذكاء الاصطناعي.
    """
    
    def __init__(self):
        """تهيئة مقيم الذكاء الاصطناعي"""
        pass
    
    @abstractmethod
    def evaluate_submission(self, task_description: str, submission_text: str, 
                           rubric: Optional[Dict] = None, language: str = 'ar') -> Dict:
        """
        تقييم النص المقدم للمهمة.
        
        Args:
            task_description: وصف المهمة
            submission_text: النص المقدم للتقييم
            rubric: معايير التقييم (اختياري)
            language: لغة التقييم ('ar' للعربية، 'en' للإنجليزية)
            
        Returns:
            Dict: نتائج التقييم
        """
        pass
    
    def _prepare_system_message(self) -> str:
        """
        تحضير رسالة النظام للنموذج.
        
        Returns:
            str: رسالة النظام
        """
        return 'أنت مقيّم مهام BTEC خبير. مهمتك هي تقييم نص مهمة مقدمة من الطالب بناءً على وصف المهمة ومعايير التقييم إن وجدت.'
    
    def _extract_strengths_weaknesses(self, text: str) -> Dict[str, List[str]]:
        """
        استخراج نقاط القوة والضعف من نص.
        
        Args:
            text: النص الذي يحتوي على نقاط القوة والضعف
            
        Returns:
            Dict: قاموس يحتوي على قوائم نقاط القوة والضعف
        """
        strengths = []
        weaknesses = []
        
        # تقسيم النص إلى أسطر
        lines = text.strip().split('\n')
        
        # تحديد الوضع الحالي (قوة أو ضعف)
        current_mode = None
        
        for line in lines:
            line = line.strip()
            
            # تخطي الأسطر الفارغة
            if not line:
                continue
            
            # تحديد إذا كان السطر يشير إلى نقاط القوة
            if 'نقاط القوة' in line or 'الإيجابيات' in line or 'مميزات' in line or 'محاسن' in line or 'strengths' in line.lower():
                current_mode = 'strengths'
                continue
            
            # تحديد إذا كان السطر يشير إلى نقاط الضعف
            if 'نقاط الضعف' in line or 'السلبيات' in line or 'عيوب' in line or 'مساوئ' in line or 'weaknesses' in line.lower():
                current_mode = 'weaknesses'
                continue
            
            # إضافة النقطة إلى القائمة المناسبة
            if current_mode == 'strengths' and (line.startswith('-') or line.startswith('*') or line.startswith('•') or line[0].isdigit()):
                strengths.append(line.lstrip('- *•0123456789.').strip())
            elif current_mode == 'weaknesses' and (line.startswith('-') or line.startswith('*') or line.startswith('•') or line[0].isdigit()):
                weaknesses.append(line.lstrip('- *•0123456789.').strip())
        
        return {
            'strengths': strengths,
            'weaknesses': weaknesses
        }
    
    def _extract_grade(self, text: str) -> Optional[float]:
        """
        استخراج الدرجة من النص.
        
        Args:
            text: النص الذي يحتوي على الدرجة
            
        Returns:
            float: الدرجة المستخرجة أو None إذا لم يتم العثور عليها
        """
        import re
        
        # البحث عن نمط الدرجة (مثل "الدرجة: 85" أو "85/100" أو "85%")
        patterns = [
            r'الدرجة:?\s*(\d+\.?\d*)',
            r'درجة:?\s*(\d+\.?\d*)',
            r'التقييم:?\s*(\d+\.?\d*)',
            r'النتيجة:?\s*(\d+\.?\d*)',
            r'(\d+\.?\d*)\s*/\s*100',
            r'(\d+\.?\d*)\s*%',
            r'grade:?\s*(\d+\.?\d*)',
            r'score:?\s*(\d+\.?\d*)',
            r'mark:?\s*(\d+\.?\d*)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    grade = float(match.group(1))
                    
                    # التحقق من أن الدرجة في النطاق الصحيح
                    if '%' in pattern and 0 <= grade <= 100:
                        return grade
                    elif '/100' in pattern and 0 <= grade <= 100:
                        return grade
                    elif 0 <= grade <= 100:
                        return grade
                    elif 0 <= grade <= 10:  # مقياس من 10
                        return grade * 10
                    elif 0 <= grade <= 5:  # مقياس من 5
                        return grade * 20
                except ValueError:
                    continue
        
        return None
    
    def _extract_criteria_scores(self, text: str, rubric: Dict) -> Dict[str, float]:
        """
        استخراج درجات المعايير من النص.
        
        Args:
            text: النص الذي يحتوي على درجات المعايير
            rubric: معايير التقييم
            
        Returns:
            Dict: قاموس يحتوي على درجات المعايير
        """
        criteria_scores = {}
        
        if not rubric:
            return criteria_scores
        
        for criterion_id, criterion in rubric.items():
            criterion_name = criterion.get('name')
            
            # البحث عن المعيار في النص
            if criterion_name in text:
                import re
                
                # البحث عن الدرجة بعد اسم المعيار
                pattern = r'{}\s*:?\s*(\d+\.?\d*)'.format(re.escape(criterion_name))
                match = re.search(pattern, text)
                
                if match:
                    try:
                        score = float(match.group(1))
                        
                        # التحقق من أن الدرجة في النطاق الصحيح
                        if 0 <= score <= 100:
                            criteria_scores[criterion_id] = score
                        elif 0 <= score <= 10:  # مقياس من 10
                            criteria_scores[criterion_id] = score * 10
                        elif 0 <= score <= 5:  # مقياس من 5
                            criteria_scores[criterion_id] = score * 20
                    except ValueError:
                        continue
        
        return criteria_scores


class OpenAIEvaluator(AIEvaluator):
    """
    مقيم الذكاء الاصطناعي باستخدام OpenAI.
    
    يستخدم واجهة برمجة تطبيقات OpenAI لتقييم النصوص.
    """
    
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        """
        تهيئة مقيم OpenAI.
        
        Args:
            api_key: مفتاح API لـ OpenAI (اختياري، سيتم استخدام مفتاح البيئة إذا لم يتم تحديده)
            model: اسم النموذج المستخدم (اختياري، سيتم استخدام النموذج الافتراضي إذا لم يتم تحديده)
        """
        super().__init__()
        
        # تعيين مفتاح API
        self.api_key = api_key or current_app.config.get('OPENAI_API_KEY')
        if not self.api_key:
            raise ValueError("مفتاح API لـ OpenAI مطلوب")
        
        openai.api_key = self.api_key
        
        # تعيين النموذج
        self.model = model or current_app.config.get('OPENAI_MODEL', 'gpt-4')
    
    def evaluate_submission(self, task_description: str, submission_text: str, 
                           rubric: Optional[Dict] = None, language: str = 'ar') -> Dict:
        """
        تقييم النص المقدم للمهمة باستخدام OpenAI.
        
        Args:
            task_description: وصف المهمة
            submission_text: النص المقدم للتقييم
            rubric: معايير التقييم (اختياري)
            language: لغة التقييم ('ar' للعربية، 'en' للإنجليزية)
            
        Returns:
            Dict: نتائج التقييم
        """
        # إنشاء محتوى الرسالة
        prompt = self._create_evaluation_prompt(task_description, submission_text, rubric, language)
        
        try:
            # إرسال الطلب إلى OpenAI
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self._prepare_system_message()},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=2000
            )
            
            # استخراج النتيجة
            result_text = response.choices[0].message.content.strip()
            
            # معالجة النتيجة
            feedback = result_text
            grade = self._extract_grade(result_text)
            sw_dict = self._extract_strengths_weaknesses(result_text)
            strengths = '; '.join(sw_dict['strengths'])
            weaknesses = '; '.join(sw_dict['weaknesses'])
            criteria_scores = self._extract_criteria_scores(result_text, rubric) if rubric else {}
            
            # حساب الدرجة الإجمالية من معايير التقييم إذا لم يتم العثور عليها
            if not grade and criteria_scores:
                total_weight = 0
                weighted_score = 0
                
                for criterion_id, score in criteria_scores.items():
                    weight = rubric[criterion_id].get('weight', 1)
                    total_weight += weight
                    weighted_score += score * weight
                
                if total_weight > 0:
                    grade = weighted_score / total_weight
            
            # التحقق من أن الدرجة في النطاق الصحيح
            if grade is not None:
                grade = max(0, min(100, grade))
            
            # إنشاء النتيجة
            result = {
                'grade': grade,
                'feedback': feedback,
                'strengths': strengths,
                'weaknesses': weaknesses,
                'criteria_scores': criteria_scores
            }
            
            return result
        
        except Exception as e:
            logger.error(f"خطأ في تقييم OpenAI: {str(e)}")
            raise
    
    def _create_evaluation_prompt(self, task_description: str, submission_text: str, 
                                 rubric: Optional[Dict] = None, language: str = 'ar') -> str:
        """
        إنشاء نص محفز للتقييم.
        
        Args:
            task_description: وصف المهمة
            submission_text: النص المقدم للتقييم
            rubric: معايير التقييم (اختياري)
            language: لغة التقييم ('ar' للعربية، 'en' للإنجليزية)
            
        Returns:
            str: نص محفز للتقييم
        """
        # تحديد اللغة
        is_arabic = language.lower() == 'ar'
        
        if is_arabic:
            prompt = "قم بتقييم النص المقدم للمهمة التالية:\n\n"
            prompt += f"وصف المهمة:\n{task_description}\n\n"
            prompt += f"النص المقدم:\n{submission_text}\n\n"
            
            if rubric:
                prompt += "معايير التقييم:\n"
                for criterion_id, criterion in rubric.items():
                    name = criterion.get('name', '')
                    description = criterion.get('description', '')
                    weight = criterion.get('weight', 0)
                    
                    prompt += f"- {name} ({weight}%): {description}\n"
                    
                    if 'levels' in criterion:
                        prompt += "  المستويات:\n"
                        for level, level_desc in criterion['levels'].items():
                            prompt += f"  - المستوى {level}: {level_desc}\n"
                
                prompt += "\n"
            
            prompt += "قم بإنشاء تقييم شامل يتضمن:\n"
            prompt += "1. تقييم عام للنص\n"
            prompt += "2. الدرجة النهائية من 100\n"
            prompt += "3. نقاط القوة في النص (على شكل نقاط)\n"
            prompt += "4. نقاط الضعف والتوصيات للتحسين (على شكل نقاط)\n"
            
            if rubric:
                prompt += "5. تقييم كل معيار من معايير التقييم مع الدرجة لكل معيار\n"
        else:
            prompt = "Evaluate the following submission for the given task:\n\n"
            prompt += f"Task Description:\n{task_description}\n\n"
            prompt += f"Submission Text:\n{submission_text}\n\n"
            
            if rubric:
                prompt += "Evaluation Criteria:\n"
                for criterion_id, criterion in rubric.items():
                    name = criterion.get('name', '')
                    description = criterion.get('description', '')
                    weight = criterion.get('weight', 0)
                    
                    prompt += f"- {name} ({weight}%): {description}\n"
                    
                    if 'levels' in criterion:
                        prompt += "  Levels:\n"
                        for level, level_desc in criterion['levels'].items():
                            prompt += f"  - Level {level}: {level_desc}\n"
                
                prompt += "\n"
            
            prompt += "Create a comprehensive evaluation that includes:\n"
            prompt += "1. General assessment of the text\n"
            prompt += "2. Final grade out of 100\n"
            prompt += "3. Strengths of the submission (as bullet points)\n"
            prompt += "4. Weaknesses and recommendations for improvement (as bullet points)\n"
            
            if rubric:
                prompt += "5. Evaluation of each criterion with a score for each\n"
        
        return prompt


class AIEvaluatorArabic(OpenAIEvaluator):
    """مقيم الذكاء الاصطناعي المتخصص باللغة العربية"""
    
    def _prepare_system_message(self) -> str:
        """تحضير رسالة النظام للنموذج باللغة العربية"""
        return 'أنت مقيّم مهام BTEC خبير يتحدث العربية بطلاقة. مهمتك هي تقييم نص مهمة مقدمة من الطالب بناءً على وصف المهمة ومعايير التقييم إن وجدت.'


class AIEvaluatorREST(AIEvaluator):
    """
    مقيم الذكاء الاصطناعي باستخدام خدمة REST API.
    
    يستخدم واجهة REST API لتقييم النصوص.
    """
    
    def __init__(self, api_url: Optional[str] = None):
        """
        تهيئة مقيم REST API.
        
        Args:
            api_url: عنوان URL لخدمة REST API (اختياري، سيتم استخدام العنوان من الإعدادات إذا لم يتم تحديده)
        """
        super().__init__()
        
        # تعيين عنوان URL
        self.api_url = api_url or current_app.config.get('AI_API_URL')
        if not self.api_url:
            raise ValueError("عنوان URL لخدمة REST API مطلوب")
    
    def evaluate_submission(self, task_description: str, submission_text: str, 
                           rubric: Optional[Dict] = None, language: str = 'ar') -> Dict:
        """
        تقييم النص المقدم للمهمة باستخدام خدمة REST API.
        
        Args:
            task_description: وصف المهمة
            submission_text: النص المقدم للتقييم
            rubric: معايير التقييم (اختياري)
            language: لغة التقييم ('ar' للعربية، 'en' للإنجليزية)
            
        Returns:
            Dict: نتائج التقييم
        """
        import requests
        
        # إنشاء محتوى الطلب
        data = {
            'task_description': task_description,
            'submission_text': submission_text,
            'language': language
        }
        
        if rubric:
            data['rubric'] = rubric
        
        try:
            # إرسال الطلب إلى خدمة REST API
            response = requests.post(self.api_url, json=data)
            response.raise_for_status()
            
            # استخراج النتيجة
            result = response.json()
            
            return result
        
        except Exception as e:
            logger.error(f"خطأ في تقييم REST API: {str(e)}")
            raise
    
    def _prepare_system_message(self) -> str:
        """تحضير رسالة النظام للنموذج بلغات متعددة"""
        if hasattr(self, 'language') and self.language.lower() == 'en':
            return 'You are an expert BTEC task evaluator. Your role is to evaluate a student\'s submission based on the task description and evaluation criteria if provided.'
        return 'أنت مقيّم مهام BTEC خبير يتحدث العربية بطلاقة. مهمتك هي تقييم نص مهمة مقدمة من الطالب بناءً على وصف المهمة ومعايير التقييم إن وجدت.'