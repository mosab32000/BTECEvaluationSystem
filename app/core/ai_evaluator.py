"""
وحدة تقييم المهام باستخدام الذكاء الاصطناعي

هذه الوحدة مسؤولة عن تقييم مهام الطلاب باستخدام نماذج الذكاء الاصطناعي
وتوفر واجهة موحدة للتقييم باللغتين العربية والإنجليزية.
"""
import json
import logging
import os
import time
from typing import Dict, List, Optional, Union, Any

from flask import current_app
import openai

logger = logging.getLogger(__name__)

class AIEvaluator:
    """
    فئة تقييم المهام باستخدام الذكاء الاصطناعي
    """
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        """
        تهيئة مقيّم الذكاء الاصطناعي
        
        Args:
            api_key: مفتاح API للذكاء الاصطناعي (اختياري، يمكن استخدام المتغير البيئي)
            model: نموذج الذكاء الاصطناعي المستخدم (اختياري، يمكن استخدام المتغير البيئي)
        """
        # تعيين المفتاح من المتغيرات البيئية أو المعطى
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY")
        
        # تعيين النموذج من المتغيرات البيئية أو المعطى أو القيمة الافتراضية
        self.model = model or os.environ.get("OPENAI_MODEL", "gpt-4")
        
        # تهيئة المفتاح
        if self.api_key:
            openai.api_key = self.api_key
            # استخدام واجهة openai القديمة للتوافق
            self.client = openai
            logger.info(f"AI Evaluator initialized with model: {self.model}")
        else:
            logger.warning("OPENAI_API_KEY not set. AI evaluation will not work.")
            self.client = None
        
        # قوالب عمليات التقييم
        self.evaluation_templates = {
            'ar': {
                'basic': """
                أنت مقيّم مهام BTEC محترف. قم بتقييم المهمة التالية بناءً على المعايير المحددة.
                
                معايير التقييم:
                - المعرفة والفهم (30%): فهم المفاهيم الأساسية والنظريات
                - التطبيق العملي (30%): القدرة على تطبيق المعرفة في مواقف عملية
                - المهارات التحليلية (20%): تحليل المعلومات واستخلاص النتائج
                - الإبداع والابتكار (10%): تقديم أفكار جديدة ومبتكرة
                - التنظيم والعرض (10%): تنظيم الأفكار وعرضها بشكل منطقي وواضح
                
                المهمة: {task_description}
                
                تقديم الطالب: {submission}
                
                يرجى تقييم المهمة وتقديم:
                1. درجة نهائية (من 100)
                2. درجات تفصيلية لكل معيار
                3. ملاحظات إيجابية
                4. مجالات للتحسين
                5. توصيات محددة
                """,
                
                'detailed': """
                أنت مقيّم مهام BTEC خبير بخبرة واسعة. قم بتقييم المهمة التالية بعمق ودقة.
                
                معايير التقييم:
                {criteria}
                
                المهمة: {task_description}
                
                تقديم الطالب: {submission}
                
                يرجى تقييم المهمة وتقديم:
                1. درجة نهائية (من 100)
                2. درجات تفصيلية لكل معيار مع تبرير
                3. تحليل نقاط القوة بالتفصيل
                4. تحديد نقاط الضعف والمجالات للتحسين
                5. توصيات محددة وعملية للتطوير
                6. مقارنة مع معايير BTEC المهنية
                """
            },
            'en': {
                'basic': """
                You are a professional BTEC task evaluator. Evaluate the following task based on the specified criteria.
                
                Evaluation Criteria:
                - Knowledge and Understanding (30%): Understanding of core concepts and theories
                - Practical Application (30%): Ability to apply knowledge in practical situations
                - Analytical Skills (20%): Analyzing information and drawing conclusions
                - Creativity and Innovation (10%): Presenting new and innovative ideas
                - Organization and Presentation (10%): Organizing ideas and presenting them logically and clearly
                
                Task: {task_description}
                
                Student Submission: {submission}
                
                Please evaluate the task and provide:
                1. Final grade (out of 100)
                2. Detailed grades for each criterion
                3. Positive feedback
                4. Areas for improvement
                5. Specific recommendations
                """,
                
                'detailed': """
                You are an expert BTEC task evaluator with extensive experience. Evaluate the following task with depth and precision.
                
                Evaluation Criteria:
                {criteria}
                
                Task: {task_description}
                
                Student Submission: {submission}
                
                Please evaluate the task and provide:
                1. Final grade (out of 100)
                2. Detailed grades for each criterion with justification
                3. Analysis of strengths in detail
                4. Identification of weaknesses and areas for improvement
                5. Specific and practical recommendations for development
                6. Comparison with professional BTEC standards
                """
            }
        }
    
    def evaluate(self, 
                submission: str, 
                task_description: str, 
                language: str = 'ar', 
                template_type: str = 'basic',
                criteria: Optional[List[Dict]] = None,
                output_format: str = 'text',
                max_retries: int = 3) -> Dict:
        """
        تقييم تقديم الطالب لمهمة معينة
        
        Args:
            submission: نص تقديم الطالب
            task_description: وصف المهمة
            language: لغة التقييم ('ar' للعربية، 'en' للإنجليزية)
            template_type: نوع قالب التقييم ('basic' أو 'detailed')
            criteria: معايير التقييم المخصصة (اختياري)
            output_format: تنسيق الإخراج ('text' أو 'json')
            max_retries: الحد الأقصى لعدد إعادة المحاولات في حالة الفشل
            
        Returns:
            dict: نتائج التقييم
        """
        if not self.client:
            return {
                'success': False,
                'error': 'AI evaluation service not initialized. Missing API key.',
                'grade': 0,
                'feedback': 'Unable to evaluate without OpenAI API key.'
            }
        
        start_time = time.time()
        retry_count = 0
        
        # التأكد من أن اللغة ونوع القالب صالحان
        if language not in ['ar', 'en']:
            language = 'ar'  # استخدام العربية كلغة افتراضية
        
        if template_type not in ['basic', 'detailed']:
            template_type = 'basic'  # استخدام القالب الأساسي كافتراضي
        
        # استخراج قالب التقييم
        template = self.evaluation_templates[language][template_type]
        
        # تحويل معايير التقييم إلى نص إذا تم توفيرها
        criteria_text = ""
        if criteria:
            for i, criterion in enumerate(criteria):
                name = criterion.get('name', f'Criterion {i+1}')
                description = criterion.get('description', '')
                weight = criterion.get('weight', '')
                
                criteria_text += f"- {name}"
                if weight:
                    criteria_text += f" ({weight}%)"
                if description:
                    criteria_text += f": {description}"
                criteria_text += "\n"
        
        # تحضير السياق لنموذج التقييم
        prompt = template.format(
            task_description=task_description,
            submission=submission,
            criteria=criteria_text or "Use standard BTEC evaluation criteria"
        )
        
        # إضافة تعليمات تنسيق JSON إذا كان التنسيق المطلوب هو JSON
        if output_format.lower() == 'json':
            json_instructions = """
            قم بتقديم التقييم بتنسيق JSON باستخدام الهيكل التالي:
            {
                "grade": <الدرجة النهائية (رقم)>,
                "criteria_grades": {
                    "<اسم المعيار 1>": <الدرجة (رقم)>,
                    "<اسم المعيار 2>": <الدرجة (رقم)>,
                    ...
                },
                "strengths": [
                    "<نقطة قوة 1>",
                    "<نقطة قوة 2>",
                    ...
                ],
                "improvements": [
                    "<مجال للتحسين 1>",
                    "<مجال للتحسين 2>",
                    ...
                ],
                "recommendations": [
                    "<توصية 1>",
                    "<توصية 2>",
                    ...
                ],
                "feedback": "<ملخص التقييم العام>"
            }
            
            تأكد من أن الخرج صالح بتنسيق JSON بدون أي نص تمهيدي أو ختامي.
            """
            prompt += json_instructions
        
        # معالجة التقييم مع إعادة المحاولة في حالة الفشل
        while retry_count < max_retries:
            try:
                logger.info(f"Sending evaluation request to AI model: {self.model}")
                
                # استخدام واجهة الإصدار القديم من OpenAI
                response = self.client.ChatCompletion.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": "أنت مقيّم BTEC محترف ومتخصص."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.2,
                    max_tokens=2000
                )
                
                # استخراج النص من استجابة الذكاء الاصطناعي
                response_text = response.choices[0].message.content
                
                # إذا كان التنسيق المطلوب هو JSON، حاول تحليل النص كـ JSON
                if output_format.lower() == 'json':
                    try:
                        # البحث عن بداية ونهاية JSON
                        json_start = response_text.find('{')
                        json_end = response_text.rfind('}') + 1
                        
                        if json_start >= 0 and json_end > json_start:
                            json_text = response_text[json_start:json_end]
                            evaluation_data = json.loads(json_text)
                        else:
                            raise ValueError("Could not find valid JSON in response")
                        
                        # التحقق من صحة البيانات
                        if 'grade' not in evaluation_data:
                            raise ValueError("Missing required 'grade' field in JSON response")
                        
                        # تحويل الدرجة إلى رقم إذا كانت نصًا
                        if isinstance(evaluation_data.get('grade'), str):
                            try:
                                evaluation_data['grade'] = float(evaluation_data['grade'])
                            except ValueError:
                                # إذا لم يمكن التحويل مباشرة، حاول استخراج رقم من النص
                                grade_str = evaluation_data['grade']
                                grade_digits = ''.join(c for c in grade_str if c.isdigit() or c == '.')
                                try:
                                    evaluation_data['grade'] = float(grade_digits)
                                except (ValueError, TypeError):
                                    evaluation_data['grade'] = 0
                        
                        # إضافة بيانات إضافية
                        evaluation_data['success'] = True
                        evaluation_data['processing_time'] = time.time() - start_time
                        
                        return evaluation_data
                    
                    except (json.JSONDecodeError, ValueError) as e:
                        logger.error(f"Failed to parse AI response as JSON: {e}")
                        logger.debug(f"Raw AI response: {response_text}")
                        
                        # إعادة المحاولة إذا فشل تحليل JSON
                        retry_count += 1
                        if retry_count >= max_retries:
                            # إذا فشلت جميع المحاولات، أرجع التقييم كنص
                            return {
                                'success': True,
                                'format_error': f"Could not parse as JSON: {e}",
                                'raw_response': response_text,
                                'grade': 0,  # قيمة افتراضية
                                'processing_time': time.time() - start_time
                            }
                        continue
                
                # تنسيق النص العادي
                return {
                    'success': True,
                    'evaluation': response_text,
                    'processing_time': time.time() - start_time
                }
                
            except Exception as e:
                logger.error(f"AI evaluation error: {e}")
                retry_count += 1
                time.sleep(2)  # انتظار قبل إعادة المحاولة
        
        # إذا فشلت جميع المحاولات
        return {
            'success': False,
            'error': f'Failed to evaluate after {max_retries} attempts',
            'grade': 0,
            'feedback': 'Error in AI evaluation service.'
        }
    
    def extract_grade(self, evaluation_text: str) -> float:
        """
        استخراج الدرجة من نص التقييم
        
        Args:
            evaluation_text: نص التقييم
            
        Returns:
            float: الدرجة المستخرجة
        """
        try:
            # محاولة العثور على أنماط متعددة للدرجات
            grade_patterns = [
                r'درجة نهائية:?\s*(\d+(?:\.\d+)?)',
                r'الدرجة النهائية:?\s*(\d+(?:\.\d+)?)',
                r'درجة:?\s*(\d+(?:\.\d+)?)',
                r'(\d+(?:\.\d+)?)\/100',
                r'Final grade:?\s*(\d+(?:\.\d+)?)',
                r'Grade:?\s*(\d+(?:\.\d+)?)'
            ]
            
            for pattern in grade_patterns:
                import re
                match = re.search(pattern, evaluation_text)
                if match:
                    return float(match.group(1))
            
            # إذا لم يتم العثور على أي نمط، حاول استخراج أي رقم
            import re
            numbers = re.findall(r'\d+(?:\.\d+)?', evaluation_text)
            if numbers:
                for num in numbers:
                    try:
                        grade = float(num)
                        if 0 <= grade <= 100:
                            return grade
                    except ValueError:
                        continue
            
            # إذا لم يتم العثور على أي درجة واضحة
            logger.warning(f"Could not extract grade from evaluation text: {evaluation_text[:100]}...")
            return 0
        
        except Exception as e:
            logger.error(f"Error extracting grade: {e}")
            return 0
    
    def summarize_evaluation(self, evaluation_data: Dict, max_length: int = 200) -> str:
        """
        تلخيص بيانات التقييم في نص قصير
        
        Args:
            evaluation_data: بيانات التقييم
            max_length: الحد الأقصى لطول الملخص
            
        Returns:
            str: ملخص التقييم
        """
        try:
            if not evaluation_data.get('success', False):
                return f"فشل التقييم: {evaluation_data.get('error', 'خطأ غير معروف')}"
            
            if 'evaluation' in evaluation_data:
                # للتقييمات النصية
                text = evaluation_data['evaluation']
                if len(text) > max_length:
                    return text[:max_length] + "..."
                return text
            
            # للتقييمات بتنسيق JSON
            grade = evaluation_data.get('grade', 0)
            strengths = evaluation_data.get('strengths', [])
            improvements = evaluation_data.get('improvements', [])
            feedback = evaluation_data.get('feedback', '')
            
            summary = f"الدرجة: {grade}/100. "
            
            if feedback:
                summary += f"{feedback} "
            
            if strengths:
                summary += f"نقاط القوة: {', '.join(strengths[:2])}. "
            
            if improvements:
                summary += f"للتحسين: {', '.join(improvements[:2])}."
            
            if len(summary) > max_length:
                return summary[:max_length] + "..."
            
            return summary
            
        except Exception as e:
            logger.error(f"Error summarizing evaluation: {e}")
            return "خطأ في تلخيص التقييم"


class AIEvaluatorREST(AIEvaluator):
    """
    فئة تقييم تستخدم واجهة REST API
    """
    def __init__(self, api_url: Optional[str] = None, api_key: Optional[str] = None):
        """
        تهيئة مقيّم يستخدم REST API
        
        Args:
            api_url: عنوان URL لخدمة API (اختياري، يمكن استخدام المتغير البيئي)
            api_key: مفتاح API (اختياري، يمكن استخدام المتغير البيئي)
        """
        self.api_url = api_url or os.environ.get("AI_API_URL")
        self.api_key = api_key or os.environ.get("AI_API_KEY")
        
        if not self.api_url:
            logger.warning("AI_API_URL not set. AI evaluation service will not work.")
        
        super().__init__(api_key=self.api_key)
        
    def evaluate(self, 
                submission: str, 
                task_description: str, 
                language: str = 'ar', 
                template_type: str = 'basic',
                criteria: Optional[List[Dict]] = None,
                output_format: str = 'text',
                max_retries: int = 3) -> Dict:
        """
        تقييم تقديم الطالب لمهمة معينة باستخدام REST API
        
        Args:
            [نفس المعلمات كما في الفئة الأساسية]
            
        Returns:
            dict: نتائج التقييم
        """
        import requests
        
        if not self.api_url:
            return {
                'success': False,
                'error': 'AI evaluation service URL not configured.',
                'grade': 0,
                'feedback': 'Unable to evaluate without API URL.'
            }
        
        start_time = time.time()
        retry_count = 0
        
        # تحضير بيانات الطلب
        payload = {
            'submission': submission,
            'task_description': task_description,
            'language': language,
            'template_type': template_type,
            'criteria': criteria,
            'output_format': output_format
        }
        
        headers = {
            'Content-Type': 'application/json'
        }
        
        if self.api_key:
            headers['Authorization'] = f'Bearer {self.api_key}'
        
        # إرسال الطلب مع إعادة المحاولة في حالة الفشل
        while retry_count < max_retries:
            try:
                response = requests.post(
                    self.api_url, 
                    json=payload, 
                    headers=headers, 
                    timeout=60
                )
                
                if response.ok:
                    try:
                        result = response.json()
                        result['processing_time'] = time.time() - start_time
                        return result
                    except json.JSONDecodeError:
                        logger.error("Invalid JSON response from API")
                        return {
                            'success': False,
                            'error': 'Invalid response from AI service',
                            'raw_response': response.text,
                            'processing_time': time.time() - start_time
                        }
                else:
                    logger.error(f"API error: {response.status_code} - {response.text}")
                    retry_count += 1
                    time.sleep(2)  # انتظار قبل إعادة المحاولة
            
            except Exception as e:
                logger.error(f"API request error: {e}")
                retry_count += 1
                time.sleep(2)  # انتظار قبل إعادة المحاولة
        
        # إذا فشلت جميع المحاولات
        return {
            'success': False,
            'error': f'Failed to evaluate after {max_retries} attempts',
            'grade': 0,
            'feedback': 'Error connecting to AI evaluation service.'
        }


class AIEvaluatorArabic(AIEvaluator):
    """
    فئة تقييم متخصصة في اللغة العربية
    """
    def __init__(self, api_key: Optional[str] = None):
        """
        تهيئة مقيّم متخصص في اللغة العربية
        
        Args:
            api_key: مفتاح API (اختياري، يمكن استخدام المتغير البيئي)
        """
        super().__init__(api_key=api_key)
        
        # تحديث القوالب للتركيز على اللغة العربية
        arabic_template = """
        أنت مقيّم محترف متخصص في تقييم المهام باللغة العربية وفق معايير BTEC.
        قم بتقييم المهمة التالية مع التركيز على جودة اللغة العربية واستخدام المصطلحات التقنية العربية بشكل صحيح.
        
        معايير التقييم:
        {criteria}
        
        المهمة: {task_description}
        
        تقديم الطالب: {submission}
        
        يرجى تقييم المهمة وتقديم:
        1. درجة نهائية (من 100)
        2. درجات تفصيلية لكل معيار مع تبرير
        3. تحليل نقاط القوة في استخدام اللغة العربية والمصطلحات التقنية
        4. مجالات التحسين في التعبير والصياغة باللغة العربية
        5. توصيات محددة لتحسين الكتابة التقنية باللغة العربية
        6. تصحيح الأخطاء اللغوية والإملائية والنحوية الرئيسية
        """
        
        self.evaluation_templates['ar']['detailed'] = arabic_template
    
    def evaluate(self, 
                submission: str, 
                task_description: str, 
                language: str = 'ar', 
                template_type: str = 'detailed',
                criteria: Optional[List[Dict]] = None,
                output_format: str = 'text',
                max_retries: int = 3) -> Dict:
        """
        تقييم تقديم الطالب لمهمة معينة مع التركيز على اللغة العربية
        
        Args:
            [نفس المعلمات كما في الفئة الأساسية]
            
        Returns:
            dict: نتائج التقييم
        """
        # دائمًا استخدام اللغة العربية
        return super().evaluate(
            submission=submission,
            task_description=task_description,
            language='ar',
            template_type=template_type,
            criteria=criteria,
            output_format=output_format,
            max_retries=max_retries
        )


class AIEvaluatorAdvanced(AIEvaluator):
    """
    فئة تقييم متقدمة تجمع بين مصادر متعددة
    """
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        """
        تهيئة مقيّم متقدم
        
        Args:
            api_key: مفتاح API (اختياري، يمكن استخدام المتغير البيئي)
            model: نموذج الذكاء الاصطناعي المستخدم (اختياري، يمكن استخدام المتغير البيئي)
        """
        super().__init__(api_key=api_key, model=model)
        
        # تحديث القوالب للتقييم المتقدم
        advanced_template = """
        أنت خبير تقييم متخصص في معايير BTEC. مهمتك تقييم المشروع المقدم بأقصى درجات الدقة والعمق.
        
        معايير التقييم:
        {criteria}
        
        المهمة: {task_description}
        
        تقديم الطالب: {submission}
        
        يجب أن يتضمن تقييمك العناصر التالية:
        
        1. ملخص تنفيذي (50-100 كلمة): نظرة عامة على التقييم والنتائج الرئيسية.
        
        2. درجة نهائية: تقييم شامل من 100 درجة مع تبرير واضح لكيفية التوصل إلى هذه النتيجة.
        
        3. تقييم تفصيلي لكل معيار:
           - الدرجة من 100
           - تحليل نقاط القوة
           - تحديد نقاط الضعف
           - أمثلة محددة من تقديم الطالب
           - مقارنة بمعايير BTEC المهنية
        
        4. تحليل جودة المحتوى:
           - الفهم المفاهيمي
           - الدقة التقنية
           - شمولية المحتوى
           - العمق التحليلي
        
        5. توصيات محددة للتحسين:
           - 3-5 توصيات رئيسية واضحة وقابلة للتنفيذ
           - استراتيجيات للتطوير المهني
        
        6. تقييم الجوانب المهنية:
           - القابلية للتطبيق في بيئات العمل
           - الالتزام بأفضل الممارسات والمعايير المهنية
        
        تأكد من أن تقييمك:
        - موضوعي ودقيق
        - مدعوم بأمثلة محددة
        - بناء ويقدم مسارات واضحة للتحسين
        - متوافق مع أحدث معايير BTEC المهنية
        """
        
        self.evaluation_templates['ar']['advanced'] = advanced_template
    
    def evaluate_with_rubric(self, 
                           submission: str, 
                           task_description: str, 
                           rubric: Dict,
                           language: str = 'ar',
                           output_format: str = 'json') -> Dict:
        """
        تقييم تقديم الطالب باستخدام معايير تقييم محددة
        
        Args:
            submission: نص تقديم الطالب
            task_description: وصف المهمة
            rubric: معايير التقييم (rubric)
            language: لغة التقييم
            output_format: تنسيق الإخراج
            
        Returns:
            dict: نتائج التقييم
        """
        # استخراج معايير التقييم من rubric
        criteria = []
        if 'criteria' in rubric:
            for criterion in rubric['criteria']:
                criteria.append({
                    'name': criterion.get('name', ''),
                    'description': criterion.get('description', ''),
                    'weight': criterion.get('weight', 0)
                })
        
        # استخدام نوع القالب المتقدم
        return self.evaluate(
            submission=submission,
            task_description=task_description,
            language=language,
            template_type='advanced',
            criteria=criteria,
            output_format=output_format
        )
    
    def evaluate_with_multimedia(self, 
                              submission: Dict, 
                              task_description: str,
                              language: str = 'ar') -> Dict:
        """
        تقييم تقديم الطالب متضمنًا وسائط متعددة (نص، صور، صوت)
        
        Args:
            submission: بيانات التقديم (نص، صور، صوت)
            task_description: وصف المهمة
            language: لغة التقييم
            
        Returns:
            dict: نتائج التقييم
        """
        # تحويل الوسائط المتعددة إلى نص موحد
        combined_text = ""
        
        # إضافة النص المكتوب
        if 'text' in submission:
            combined_text += f"النص المكتوب:\n{submission['text']}\n\n"
        
        # تحليل الصور إذا كانت متوفرة
        if 'images' in submission and submission['images']:
            combined_text += "وصف الصور المرفقة:\n"
            
            for i, image_data in enumerate(submission['images']):
                if image_data:
                    try:
                        import pytesseract
                        from PIL import Image
                        import io
                        import base64
                        
                        # تحويل بيانات الصورة
                        if isinstance(image_data, str) and image_data.startswith('data:image'):
                            # إذا كانت الصورة بتنسيق base64
                            image_data = image_data.split(',')[1]
                            image = Image.open(io.BytesIO(base64.b64decode(image_data)))
                        elif isinstance(image_data, str) and os.path.exists(image_data):
                            # إذا كانت الصورة مسارًا لملف
                            image = Image.open(image_data)
                        elif isinstance(image_data, bytes):
                            # إذا كانت الصورة بيانات ثنائية
                            image = Image.open(io.BytesIO(image_data))
                        else:
                            logger.error(f"Unsupported image data format for image {i+1}")
                            combined_text += f"[الصورة {i+1}: تنسيق غير مدعوم]\n"
                            continue
                        
                        # استخراج النص من الصورة
                        image_text = pytesseract.image_to_string(image, lang='ara+eng')
                        if image_text.strip():
                            combined_text += f"[الصورة {i+1}] النص المستخرج:\n{image_text.strip()}\n"
                        else:
                            combined_text += f"[الصورة {i+1}] لا يوجد نص مرئي في الصورة.\n"
                    
                    except Exception as e:
                        logger.error(f"Error processing image {i+1}: {e}")
                        combined_text += f"[الصورة {i+1}: خطأ في المعالجة]\n"
            
            combined_text += "\n"
        
        # تحليل المقاطع الصوتية إذا كانت متوفرة
        if 'audio' in submission and submission['audio']:
            combined_text += "محتوى المقاطع الصوتية المرفقة:\n"
            
            for i, audio_data in enumerate(submission['audio']):
                if audio_data:
                    try:
                        import speech_recognition as sr
                        from pydub import AudioSegment
                        import io
                        import base64
                        
                        # تحويل بيانات الصوت
                        if isinstance(audio_data, str) and audio_data.startswith('data:audio'):
                            # إذا كان الصوت بتنسيق base64
                            audio_data = audio_data.split(',')[1]
                            audio = AudioSegment.from_file(io.BytesIO(base64.b64decode(audio_data)))
                        elif isinstance(audio_data, str) and os.path.exists(audio_data):
                            # إذا كان الصوت مسارًا لملف
                            audio = AudioSegment.from_file(audio_data)
                        elif isinstance(audio_data, bytes):
                            # إذا كان الصوت بيانات ثنائية
                            audio = AudioSegment.from_file(io.BytesIO(audio_data))
                        else:
                            logger.error(f"Unsupported audio data format for audio {i+1}")
                            combined_text += f"[المقطع الصوتي {i+1}: تنسيق غير مدعوم]\n"
                            continue
                        
                        # تحويل الصوت إلى WAV للتعرف عليه
                        with io.BytesIO() as wav_io:
                            audio.export(wav_io, format="wav")
                            wav_io.seek(0)
                            
                            # التعرف على الكلام
                            recognizer = sr.Recognizer()
                            with sr.AudioFile(wav_io) as source:
                                audio_data = recognizer.record(source)
                                
                                # محاولة التعرف على الكلام العربي أو الإنجليزي
                                try:
                                    if language == 'ar':
                                        text = recognizer.recognize_google(audio_data, language="ar-SA")
                                    else:
                                        text = recognizer.recognize_google(audio_data, language="en-US")
                                        
                                    if text.strip():
                                        combined_text += f"[المقطع الصوتي {i+1}] النص المستخرج:\n{text.strip()}\n"
                                    else:
                                        combined_text += f"[المقطع الصوتي {i+1}] لم يتم التعرف على كلام واضح.\n"
                                
                                except sr.UnknownValueError:
                                    combined_text += f"[المقطع الصوتي {i+1}] لم يتم التعرف على الكلام.\n"
                                except sr.RequestError:
                                    combined_text += f"[المقطع الصوتي {i+1}] خطأ في خدمة التعرف على الكلام.\n"
                    
                    except Exception as e:
                        logger.error(f"Error processing audio {i+1}: {e}")
                        combined_text += f"[المقطع الصوتي {i+1}: خطأ في المعالجة]\n"
            
            combined_text += "\n"
        
        # استخدام النص الموحد للتقييم
        return self.evaluate(
            submission=combined_text,
            task_description=task_description,
            language=language,
            template_type='advanced',
            output_format='json'
        )