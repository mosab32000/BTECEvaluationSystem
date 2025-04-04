"""
وحدة تقييم الذكاء الاصطناعي في نظام تقييم BTEC
"""
import json
import logging
import os
import time
from datetime import datetime

import openai
import requests
from flask import current_app

logger = logging.getLogger(__name__)

class AIEvaluator:
    """
    فئة لتقييم المهام باستخدام نماذج الذكاء الاصطناعي (OpenAI)
    """
    
    def __init__(self, api_key=None, model="gpt-3.5-turbo"):
        """
        تهيئة المقيّم
        
        Args:
            api_key: مفتاح API لـ OpenAI
            model: اسم النموذج المستخدم
        """
        self.api_key = api_key or os.environ.get('OPENAI_API_KEY') or current_app.config.get('OPENAI_API_KEY')
        self.model = model
        self.client = None
        
        # محاولة تهيئة العميل
        try:
            if self.api_key:
                openai.api_key = self.api_key
                self.client = openai.OpenAI(api_key=self.api_key)
                logger.info(f"تم تهيئة مقيّم الذكاء الاصطناعي بنجاح باستخدام نموذج '{self.model}'")
            else:
                logger.warning("لم يتم توفير مفتاح API لـ OpenAI")
        except Exception as e:
            logger.error(f"خطأ في تهيئة مقيّم الذكاء الاصطناعي: {str(e)}")
    
    def evaluate_task(self, task_description, submission_text, rubric=None, output_format="text", max_retries=3):
        """
        تقييم مهمة باستخدام نموذج الذكاء الاصطناعي
        
        Args:
            task_description: وصف المهمة أو المطلوب
            submission_text: النص المقدم للتقييم
            rubric: معايير التقييم (اختياري)
            output_format: تنسيق الإخراج ("text" أو "json")
            max_retries: الحد الأقصى لعدد المحاولات في حالة الفشل
            
        Returns:
            dict: نتيجة التقييم
        """
        if not self.client:
            return {
                'success': False,
                'error': 'لم يتم تهيئة مقيّم الذكاء الاصطناعي. يرجى التحقق من مفتاح API.',
                'grade': None,
                'feedback': None
            }
        
        # إعداد السياق والتعليمات بناءً على معايير التقييم
        if rubric:
            system_message = self._prepare_system_message_with_rubric(rubric, output_format)
        else:
            system_message = self._prepare_system_message(output_format)
        
        # إعداد رسالة المستخدم
        user_message = self._prepare_user_message(task_description, submission_text)
        
        # المحاولة عدة مرات في حالة الفشل
        for attempt in range(max_retries):
            try:
                logger.info(f"محاولة تقييم المهمة (محاولة {attempt + 1}/{max_retries})")
                
                # إرسال الطلب إلى OpenAI
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": system_message},
                        {"role": "user", "content": user_message}
                    ],
                    temperature=0.5,
                    max_tokens=2000
                )
                
                # معالجة الاستجابة
                response_text = response.choices[0].message.content.strip()
                
                if output_format == "json":
                    # محاولة تحليل الاستجابة كـ JSON
                    try:
                        result_json = self._extract_json_from_response(response_text)
                        return {
                            'success': True,
                            'grade': result_json.get('grade'),
                            'feedback': result_json.get('feedback'),
                            'criteria_grades': result_json.get('criteria_grades', {}),
                            'raw_response': response_text
                        }
                    except json.JSONDecodeError as e:
                        logger.error(f"خطأ في تحليل استجابة JSON: {str(e)}")
                        if attempt < max_retries - 1:
                            time.sleep(2)  # انتظار قبل المحاولة مرة أخرى
                            continue
                        else:
                            # إذا فشلت جميع المحاولات، قم بإرجاع الاستجابة النصية
                            return {
                                'success': True,
                                'grade': self._extract_grade_from_text(response_text),
                                'feedback': response_text,
                                'raw_response': response_text
                            }
                else:
                    # استخراج الدرجة والملاحظات من النص
                    grade = self._extract_grade_from_text(response_text)
                    
                    return {
                        'success': True,
                        'grade': grade,
                        'feedback': response_text,
                        'raw_response': response_text
                    }
                
            except Exception as e:
                logger.error(f"خطأ في تقييم المهمة: {str(e)}")
                if attempt < max_retries - 1:
                    time.sleep(2)  # انتظار قبل المحاولة مرة أخرى
                    continue
                else:
                    return {
                        'success': False,
                        'error': str(e),
                        'grade': None,
                        'feedback': None
                    }
    
    def _prepare_system_message(self, output_format):
        """
        إعداد رسالة النظام العامة
        
        Args:
            output_format: تنسيق الإخراج
            
        Returns:
            str: رسالة النظام
        """
        if output_format == "json":
            return """أنت مقيّم مهام BTEC خبير. مهمتك هي تقييم نص مهمة مقدمة بناءً على متطلبات المهمة.
يجب تقييم المهمة على مقياس من 0 إلى 100 نقطة، حيث 100 هي الدرجة الكاملة.
قم بإرجاع النتيجة بتنسيق JSON يحتوي على:
1. "grade": الدرجة النهائية (رقم بين 0 و 100)
2. "feedback": ملاحظات مفصلة حول نقاط القوة والضعف

مثال:
{
    "grade": 85,
    "feedback": "تم تحقيق معظم متطلبات المهمة بشكل جيد. نقاط القوة: [...]، نقاط الضعف: [...]"
}

قم بالتقييم بشكل موضوعي وعادل، وقدم ملاحظات بناءة ومفيدة للتحسين."""
        else:
            return """أنت مقيّم مهام BTEC خبير. مهمتك هي تقييم نص مهمة مقدمة بناءً على متطلبات المهمة.
يجب تقييم المهمة على مقياس من 0 إلى 100 نقطة، حيث 100 هي الدرجة الكاملة.

قدم تقييمك في النموذج التالي:
1. ملخص التقييم بجملة أو جملتين.
2. الدرجة النهائية (رقم بين 0 و 100).
3. نقاط القوة.
4. نقاط الضعف.
5. اقتراحات للتحسين.

قم بالتقييم بشكل موضوعي وعادل، وقدم ملاحظات بناءة ومفيدة للتحسين."""
    
    def _prepare_system_message_with_rubric(self, rubric, output_format):
        """
        إعداد رسالة النظام مع معايير تقييم محددة
        
        Args:
            rubric: معايير التقييم
            output_format: تنسيق الإخراج
            
        Returns:
            str: رسالة النظام
        """
        # استخراج معايير التقييم
        if isinstance(rubric, dict):
            criteria = rubric.get('criteria', [])
        elif isinstance(rubric, list):
            criteria = rubric
        else:
            try:
                criteria = json.loads(rubric) if isinstance(rubric, str) else []
            except:
                criteria = []
        
        # إعداد نص معايير التقييم
        criteria_text = ""
        for i, criterion in enumerate(criteria):
            name = criterion.get('name', f'المعيار {i+1}')
            description = criterion.get('description', '')
            weight = criterion.get('weight', 0)
            
            criteria_text += f"{i+1}. {name} (الوزن: {weight}%): {description}\n"
        
        if output_format == "json":
            system_message = f"""أنت مقيّم مهام BTEC خبير. مهمتك هي تقييم نص مهمة مقدمة بناءً على متطلبات المهمة ومعايير التقييم المحددة.
يجب تقييم المهمة على مقياس من 0 إلى 100 نقطة لكل معيار، مع احتساب الدرجة النهائية بناءً على أوزان المعايير.

معايير التقييم:
{criteria_text}

قم بإرجاع النتيجة بتنسيق JSON يحتوي على:
1. "grade": الدرجة النهائية (رقم بين 0 و 100)
2. "feedback": ملاحظات مفصلة حول نقاط القوة والضعف
3. "criteria_grades": قاموس يحتوي على درجات كل معيار

مثال:
{{
    "grade": 85,
    "feedback": "تم تحقيق معظم متطلبات المهمة بشكل جيد. نقاط القوة: [...]، نقاط الضعف: [...]",
    "criteria_grades": {{
        "{name}": 90,
        ...
    }}
}}

قم بالتقييم بشكل موضوعي وعادل، وقدم ملاحظات بناءة ومفيدة للتحسين."""
        else:
            system_message = f"""أنت مقيّم مهام BTEC خبير. مهمتك هي تقييم نص مهمة مقدمة بناءً على متطلبات المهمة ومعايير التقييم المحددة.
يجب تقييم المهمة على مقياس من 0 إلى 100 نقطة لكل معيار، مع احتساب الدرجة النهائية بناءً على أوزان المعايير.

معايير التقييم:
{criteria_text}

قدم تقييمك في النموذج التالي:
1. ملخص التقييم بجملة أو جملتين.
2. الدرجة النهائية (رقم بين 0 و 100).
3. تقييم كل معيار مع الدرجة الخاصة به.
4. نقاط القوة.
5. نقاط الضعف.
6. اقتراحات للتحسين.

قم بالتقييم بشكل موضوعي وعادل، وقدم ملاحظات بناءة ومفيدة للتحسين."""
        
        return system_message
    
    def _prepare_user_message(self, task_description, submission_text):
        """
        إعداد رسالة المستخدم
        
        Args:
            task_description: وصف المهمة
            submission_text: النص المقدم
            
        Returns:
            str: رسالة المستخدم
        """
        return f"""وصف المهمة:
{task_description}

النص المقدم للتقييم:
{submission_text}

قم بتقييم النص المقدم بناءً على وصف المهمة ومعايير التقييم المحددة."""
    
    def _extract_json_from_response(self, response_text):
        """
        استخراج JSON من استجابة النص
        
        Args:
            response_text: نص الاستجابة
            
        Returns:
            dict: الاستجابة المحللة
        """
        # محاولة العثور على JSON في النص
        try:
            # محاولة تحليل النص كاملاً كـ JSON
            return json.loads(response_text)
        except json.JSONDecodeError:
            # البحث عن أقواس JSON
            start_idx = response_text.find('{')
            end_idx = response_text.rfind('}')
            
            if start_idx != -1 and end_idx != -1:
                try:
                    json_text = response_text[start_idx:end_idx+1]
                    return json.loads(json_text)
                except json.JSONDecodeError:
                    # محاولة تنظيف النص
                    lines = [line.strip() for line in response_text.split('\n') if line.strip()]
                    for i, line in enumerate(lines):
                        if line.startswith('{') or line.startswith('```json'):
                            json_lines = []
                            # البحث عن نهاية JSON
                            for j in range(i, len(lines)):
                                # إزالة علامات الكود
                                clean_line = lines[j].replace('```json', '').replace('```', '')
                                if clean_line:
                                    json_lines.append(clean_line)
                                if lines[j].endswith('}') or lines[j].startswith('```'):
                                    break
                            
                            json_text = ' '.join(json_lines)
                            try:
                                return json.loads(json_text)
                            except:
                                continue
        
        # إذا فشلت جميع المحاولات، قم بإرجاع قاموس فارغ
        return {'grade': 0, 'feedback': response_text}
    
    def _extract_grade_from_text(self, text):
        """
        استخراج الدرجة من النص
        
        Args:
            text: النص المحتوي على الدرجة
            
        Returns:
            float: الدرجة المستخرجة أو None
        """
        # البحث عن الدرجة في أنماط مختلفة
        import re
        
        # أنماط مختلفة للدرجات
        patterns = [
            r'الدرجة النهائية:?\s*(\d+(?:\.\d+)?)',
            r'الدرجة:?\s*(\d+(?:\.\d+)?)',
            r'التقييم النهائي:?\s*(\d+(?:\.\d+)?)',
            r'grade:?\s*(\d+(?:\.\d+)?)',
            r'score:?\s*(\d+(?:\.\d+)?)',
            r'(\d+(?:\.\d+)?)\/100',
            r'(\d+(?:\.\d+)?) من 100',
            r'(\d+(?:\.\d+)?)\/\d+',
            r'(\d+(?:\.\d+)?) out of 100',
            r'(\d+(?:\.\d+)?)\s*[نن]قطة',
            r'(\d+(?:\.\d+)?)\s*درجة'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
            if match:
                try:
                    grade = float(match.group(1))
                    # التأكد من أن الدرجة ضمن النطاق المناسب
                    if grade > 0:
                        if '/' in pattern and not '/100' in pattern:
                            # تحويل النسبة إلى درجة من 100
                            parts = match.group(0).split('/')
                            if len(parts) == 2 and parts[1].isdigit():
                                total = float(parts[1])
                                if total > 0:
                                    grade = (grade / total) * 100
                        
                        return min(100, max(0, grade))
                except (ValueError, TypeError):
                    continue
        
        # إذا لم يتم العثور على درجة، حاول البحث عن كلمة تدل على التقييم
        grade_words = {
            'ممتاز': 90,
            'جيد جدا': 80,
            'جيد': 70,
            'مقبول': 60,
            'ضعيف': 50,
            'راسب': 40,
            'فشل': 30,
            'excellent': 90,
            'very good': 80,
            'good': 70,
            'satisfactory': 60,
            'poor': 50,
            'fail': 40
        }
        
        for word, value in grade_words.items():
            if re.search(r'\b' + word + r'\b', text, re.IGNORECASE):
                return value
        
        # إذا لم يتم العثور على درجة
        return None


class AIEvaluatorREST:
    """
    فئة لتقييم المهام باستخدام واجهة REST API للذكاء الاصطناعي
    """
    
    def __init__(self, api_url=None, api_key=None):
        """
        تهيئة المقيّم
        
        Args:
            api_url: عنوان URL لواجهة REST API
            api_key: مفتاح API
        """
        self.api_url = api_url or os.environ.get('AI_API_URL') or current_app.config.get('AI_API_URL')
        self.api_key = api_key or os.environ.get('AI_API_KEY') or current_app.config.get('AI_API_KEY')
        
        if not self.api_url:
            logger.warning("لم يتم توفير عنوان URL لواجهة REST API")
    
    def evaluate_task(self, task_description, submission_text, rubric=None, output_format="json", max_retries=3):
        """
        تقييم مهمة باستخدام واجهة REST API
        
        Args:
            task_description: وصف المهمة أو المطلوب
            submission_text: النص المقدم للتقييم
            rubric: معايير التقييم (اختياري)
            output_format: تنسيق الإخراج ("text" أو "json")
            max_retries: الحد الأقصى لعدد المحاولات في حالة الفشل
            
        Returns:
            dict: نتيجة التقييم
        """
        if not self.api_url:
            return {
                'success': False,
                'error': 'لم يتم توفير عنوان URL لواجهة REST API',
                'grade': None,
                'feedback': None
            }
        
        # إعداد طلب API
        headers = {
            'Content-Type': 'application/json'
        }
        
        if self.api_key:
            headers['Authorization'] = f'Bearer {self.api_key}'
        
        data = {
            'task_description': task_description,
            'submission_text': submission_text,
            'output_format': output_format
        }
        
        if rubric:
            if isinstance(rubric, (dict, list)):
                data['rubric'] = rubric
            else:
                try:
                    data['rubric'] = json.loads(rubric) if isinstance(rubric, str) else None
                except:
                    pass
        
        # المحاولة عدة مرات في حالة الفشل
        for attempt in range(max_retries):
            try:
                logger.info(f"محاولة تقييم المهمة عبر REST API (محاولة {attempt + 1}/{max_retries})")
                
                # إرسال الطلب
                response = requests.post(
                    self.api_url,
                    headers=headers,
                    json=data,
                    timeout=60
                )
                
                # التحقق من الاستجابة
                if response.status_code == 200:
                    result = response.json()
                    return {
                        'success': True,
                        'grade': result.get('grade'),
                        'feedback': result.get('feedback'),
                        'criteria_grades': result.get('criteria_grades', {}),
                        'raw_response': result
                    }
                else:
                    logger.error(f"خطأ في استجابة API: {response.status_code} - {response.text}")
                    if attempt < max_retries - 1:
                        time.sleep(2)  # انتظار قبل المحاولة مرة أخرى
                        continue
                    else:
                        return {
                            'success': False,
                            'error': f"HTTP Error: {response.status_code}",
                            'grade': None,
                            'feedback': None
                        }
            
            except Exception as e:
                logger.error(f"خطأ في تقييم المهمة عبر REST API: {str(e)}")
                if attempt < max_retries - 1:
                    time.sleep(2)  # انتظار قبل المحاولة مرة أخرى
                    continue
                else:
                    return {
                        'success': False,
                        'error': str(e),
                        'grade': None,
                        'feedback': None
                    }


class AIEvaluatorArabic(AIEvaluator):
    """
    فئة لتقييم المهام باللغة العربية باستخدام نماذج الذكاء الاصطناعي
    """
    
    def _prepare_system_message(self, output_format):
        """
        إعداد رسالة النظام العامة باللغة العربية
        
        Args:
            output_format: تنسيق الإخراج
            
        Returns:
            str: رسالة النظام
        """
        if output_format == "json":
            return """أنت مقيّم مهام BTEC خبير يتحدث العربية بطلاقة. مهمتك هي تقييم نص مهمة مقدمة باللغة العربية بناءً على متطلبات المهمة.
يجب تقييم المهمة على مقياس من 0 إلى 100 نقطة، حيث 100 هي الدرجة الكاملة.
قم بإرجاع النتيجة بتنسيق JSON يحتوي على:
1. "grade": الدرجة النهائية (رقم بين 0 و 100)
2. "feedback": ملاحظات مفصلة باللغة العربية حول نقاط القوة والضعف

مثال:
{
    "grade": 85,
    "feedback": "تم تحقيق معظم متطلبات المهمة بشكل جيد. نقاط القوة: [...] نقاط الضعف: [...]"
}

قم بتقديم التقييم والملاحظات باللغة العربية الفصحى. يجب أن تقيّم المهمة بشكل موضوعي وعادل، وتقدم ملاحظات بناءة ومفيدة للتحسين."""
        else:
            return """أنت مقيّم مهام BTEC خبير يتحدث العربية بطلاقة. مهمتك هي تقييم نص مهمة مقدمة باللغة العربية بناءً على متطلبات المهمة.
يجب تقييم المهمة على مقياس من 0 إلى 100 نقطة، حيث 100 هي الدرجة الكاملة.

قدم تقييمك باللغة العربية في النموذج التالي:
1. ملخص التقييم بجملة أو جملتين.
2. الدرجة النهائية (رقم بين 0 و 100).
3. نقاط القوة.
4. نقاط الضعف.
5. اقتراحات للتحسين.

قم بالتقييم بشكل موضوعي وعادل، وقدم ملاحظات بناءة ومفيدة للتحسين باللغة العربية الفصحى."""
    
    def _prepare_system_message_with_rubric(self, rubric, output_format):
        """
        إعداد رسالة النظام مع معايير تقييم محددة باللغة العربية
        
        Args:
            rubric: معايير التقييم
            output_format: تنسيق الإخراج
            
        Returns:
            str: رسالة النظام
        """
        # استخراج معايير التقييم
        if isinstance(rubric, dict):
            criteria = rubric.get('criteria', [])
        elif isinstance(rubric, list):
            criteria = rubric
        else:
            try:
                criteria = json.loads(rubric) if isinstance(rubric, str) else []
            except:
                criteria = []
        
        # إعداد نص معايير التقييم
        criteria_text = ""
        for i, criterion in enumerate(criteria):
            name = criterion.get('name', f'المعيار {i+1}')
            description = criterion.get('description', '')
            weight = criterion.get('weight', 0)
            
            criteria_text += f"{i+1}. {name} (الوزن: {weight}%): {description}\n"
        
        if output_format == "json":
            system_message = f"""أنت مقيّم مهام BTEC خبير يتحدث العربية بطلاقة. مهمتك هي تقييم نص مهمة مقدمة باللغة العربية بناءً على متطلبات المهمة ومعايير التقييم المحددة.
يجب تقييم المهمة على مقياس من 0 إلى 100 نقطة لكل معيار، مع احتساب الدرجة النهائية بناءً على أوزان المعايير.

معايير التقييم:
{criteria_text}

قم بإرجاع النتيجة بتنسيق JSON يحتوي على:
1. "grade": الدرجة النهائية (رقم بين 0 و 100)
2. "feedback": ملاحظات مفصلة باللغة العربية حول نقاط القوة والضعف
3. "criteria_grades": قاموس يحتوي على درجات كل معيار

مثال:
{{
    "grade": 85,
    "feedback": "تم تحقيق معظم متطلبات المهمة بشكل جيد. نقاط القوة: [...] نقاط الضعف: [...]",
    "criteria_grades": {{
        "{name}": 90,
        ...
    }}
}}

قم بتقديم التقييم والملاحظات باللغة العربية الفصحى. يجب أن تقيّم المهمة بشكل موضوعي وعادل، وتقدم ملاحظات بناءة ومفيدة للتحسين."""
        else:
            system_message = f"""أنت مقيّم مهام BTEC خبير يتحدث العربية بطلاقة. مهمتك هي تقييم نص مهمة مقدمة باللغة العربية بناءً على متطلبات المهمة ومعايير التقييم المحددة.
يجب تقييم المهمة على مقياس من 0 إلى 100 نقطة لكل معيار، مع احتساب الدرجة النهائية بناءً على أوزان المعايير.

معايير التقييم:
{criteria_text}

قدم تقييمك باللغة العربية في النموذج التالي:
1. ملخص التقييم بجملة أو جملتين.
2. الدرجة النهائية (رقم بين 0 و 100).
3. تقييم كل معيار مع الدرجة الخاصة به.
4. نقاط القوة.
5. نقاط الضعف.
6. اقتراحات للتحسين.

قم بالتقييم بشكل موضوعي وعادل، وقدم ملاحظات بناءة ومفيدة للتحسين باللغة العربية الفصحى."""
        
        return system_message