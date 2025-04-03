"""
خدمة الذكاء الاصطناعي المتقدمة لتقييم BTEC
توفر قدرات متقدمة للتحليل والتقييم
"""

import os
import json
import logging
import openai
from flask import current_app
from typing import Dict, Any, Optional, List, Union

# إعداد السجل
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AIEvaluatorAdvanced:
    """صنف متقدم لتقييم مهام BTEC باستخدام الذكاء الاصطناعي"""

    def __init__(self, api_key: Optional[str] = None, use_context: bool = False):
        """
        تهيئة مقيم الذكاء الاصطناعي المتقدم
        
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
            logger.info("تم تهيئة AIEvaluatorAdvanced بمفتاح API صالح")
            openai.api_key = self.api_key
            self.simulation_mode = False
        else:
            logger.warning("تحذير: لم يتم توفير مفتاح OpenAI API. سيتم استخدام وضع المحاكاة.")
            self.simulation_mode = True
        
        # ضبط نموذج OpenAI المستخدم
        self.model = "gpt-4o"  # استخدام نموذج GPT-4o الأحدث
    
    def evaluate_with_detailed_feedback(self, task: str, criteria: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        تقييم مهمة BTEC مع تعليقات تفصيلية لكل معيار
        
        Args:
            task: نص المهمة للتقييم
            criteria: معايير التقييم المخصصة (اختياري)
            
        Returns:
            نتيجة التقييم مع تعليقات تفصيلية كقاموس
        """
        if self.simulation_mode:
            return {
                "grade": "محاكاة",
                "overall_feedback": "هذا تقييم محاكي. لم يتم إجراء استدعاء فعلي لـ OpenAI API.",
                "criteria_feedback": {
                    "المعرفة": "تقييم محاكي للمعرفة",
                    "التطبيق": "تقييم محاكي للتطبيق",
                    "التحليل": "تقييم محاكي للتحليل",
                    "التقييم": "تقييم محاكي للتقييم"
                },
                "strengths": ["نقطة قوة محاكية 1", "نقطة قوة محاكية 2"],
                "improvements": ["مجال تحسين محاكي 1", "مجال تحسين محاكي 2"],
                "total_score": 75
            }
        
        try:
            # تحضير معايير التقييم
            criteria_text = ""
            if criteria:
                criteria_text = f"\n\nمعايير التقييم المخصصة:\n```json\n{json.dumps(criteria, ensure_ascii=False)}\n```"
            else:
                criteria_text = """
                معايير التقييم القياسية لـ BTEC:
                1. المعرفة (Knowledge): فهم وتذكر المفاهيم والمصطلحات الأساسية
                2. التطبيق (Application): تطبيق المعرفة في سياقات عملية
                3. التحليل (Analysis): تحليل المعلومات وتفكيكها إلى أجزاء
                4. التقييم (Evaluation): تقييم الأفكار والحلول وإصدار أحكام مبررة
                """
            
            # إنشاء المطالبة (Prompt)
            prompt = f"""
            أنت مقيّم تعليمي متخصص في تقييم مهام BTEC. قم بتحليل المهمة التالية بدقة وموضوعية وقدم تعليقات تفصيلية لكل معيار:
            
            المهمة:
            ```
            {task}
            ```
            {criteria_text}
            
            قم بتقديم تقييم شامل بتنسيق JSON يتضمن الحقول التالية:
            1. grade: الدرجة النهائية حسب معايير BTEC (P, M, D)
            2. overall_feedback: تعليق عام شامل عن المهمة
            3. criteria_feedback: كائن يحتوي على تعليقات تفصيلية لكل معيار (المعرفة، التطبيق، التحليل، التقييم)
            4. strengths: قائمة بنقاط القوة الرئيسية (3-5 نقاط)
            5. improvements: قائمة بمجالات التحسين (3-5 مجالات)
            6. total_score: درجة رقمية من 0 إلى 100
            
            كن دقيقًا وموضوعيًا وقدم تعليقات بناءة ومفيدة.
            """
            
            # إجراء استدعاء API
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "أنت مقيّم تعليمي متخصص في تقييم مهام BTEC. تقييماتك شاملة ودقيقة وموضوعية."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,  # درجة حرارة منخفضة للحصول على نتائج متسقة
                max_tokens=2500,   # زيادة الحد الأقصى للرموز للسماح بتقييمات مفصلة
                response_format={"type": "json_object"}  # طلب تنسيق JSON
            )
            
            # تحليل الاستجابة
            content = response.choices[0].message.content.strip()
            return json.loads(content)
            
        except Exception as e:
            logger.error(f"خطأ في تقييم المهمة: {e}")
            return {
                "grade": "خطأ",
                "overall_feedback": f"حدث خطأ أثناء التقييم: {str(e)}",
                "criteria_feedback": {
                    "المعرفة": "غير متوفر بسبب خطأ",
                    "التطبيق": "غير متوفر بسبب خطأ",
                    "التحليل": "غير متوفر بسبب خطأ",
                    "التقييم": "غير متوفر بسبب خطأ"
                },
                "strengths": [],
                "improvements": ["حاول مرة أخرى لاحقًا"],
                "total_score": 0
            }
    
    def analyze_group_work(self, task: str, member_contributions: Dict[str, str]) -> Dict[str, Any]:
        """
        تحليل عمل المجموعة وتقييم مساهمات كل عضو
        
        Args:
            task: نص المهمة الجماعية للتقييم
            member_contributions: قاموس يحتوي على اسم كل عضو ووصف مساهمته
            
        Returns:
            تقييم للعمل الجماعي وتقييم فردي لكل عضو
        """
        if self.simulation_mode:
            members = list(member_contributions.keys())
            return {
                "group_grade": "محاكاة",
                "group_feedback": "هذا تقييم محاكي للعمل الجماعي. لم يتم إجراء استدعاء فعلي لـ OpenAI API.",
                "individual_grades": {member: "محاكاة" for member in members},
                "individual_feedback": {member: f"تقييم محاكي لمساهمة {member}" for member in members},
                "collaboration_score": 75,
                "recommendations": ["توصية محاكية 1", "توصية محاكية 2"]
            }
        
        try:
            # تحويل مساهمات الأعضاء إلى نص
            contributions_text = "\n\n".join([f"### {member}:\n{contribution}" for member, contribution in member_contributions.items()])
            
            # إنشاء المطالبة (Prompt)
            prompt = f"""
            أنت محلل متخصص في تقييم العمل الجماعي لمهام BTEC. قم بتحليل المهمة الجماعية التالية ومساهمات كل عضو:
            
            المهمة الجماعية:
            ```
            {task}
            ```
            
            مساهمات الأعضاء:
            {contributions_text}
            
            قم بتقديم تحليل شامل بتنسيق JSON يتضمن الحقول التالية:
            1. group_grade: تقييم المجموعة ككل حسب معايير BTEC (P, M, D)
            2. group_feedback: تعليق عام على أداء المجموعة
            3. individual_grades: كائن يحتوي على تقييم كل عضو (P, M, D)
            4. individual_feedback: كائن يحتوي على تعليق مفصل لكل عضو
            5. collaboration_score: درجة التعاون بين أعضاء المجموعة (0-100)
            6. recommendations: قائمة بالتوصيات لتحسين العمل الجماعي (3-5 توصيات)
            
            ركز على:
            - توازن المساهمات بين أعضاء المجموعة
            - جودة مساهمة كل عضو
            - التكامل بين المساهمات المختلفة
            - فعالية العمل الجماعي ككل
            """
            
            # إجراء استدعاء API
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "أنت محلل متخصص في تقييم العمل الجماعي لمهام BTEC. تحليلاتك شاملة وموضوعية وعادلة."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=3000,
                response_format={"type": "json_object"}
            )
            
            # تحليل الاستجابة
            content = response.choices[0].message.content.strip()
            return json.loads(content)
            
        except Exception as e:
            logger.error(f"خطأ في تحليل العمل الجماعي: {e}")
            members = list(member_contributions.keys())
            return {
                "group_grade": "خطأ",
                "group_feedback": f"حدث خطأ أثناء التحليل: {str(e)}",
                "individual_grades": {member: "خطأ" for member in members},
                "individual_feedback": {member: "غير متوفر بسبب خطأ" for member in members},
                "collaboration_score": 0,
                "recommendations": ["حاول مرة أخرى لاحقًا"]
            }
    
    def compare_submissions(self, submissions: List[Dict[str, str]], criteria: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        مقارنة عدة مهام وترتيبها حسب الجودة
        
        Args:
            submissions: قائمة من المهام (كل مهمة هي قاموس يحتوي على 'id' و 'content')
            criteria: معايير التقييم المخصصة (اختياري)
            
        Returns:
            مقارنة وترتيب للمهام المقدمة
        """
        if self.simulation_mode:
            submission_ids = [sub["id"] for sub in submissions]
            return {
                "rankings": [{
                    "id": sub_id,
                    "rank": i+1,
                    "grade": "محاكاة",
                    "score": 100 - (i * 10),
                    "feedback": f"تقييم محاكي للمهمة {sub_id}"
                } for i, sub_id in enumerate(submission_ids)],
                "comparison_notes": "هذه مقارنة محاكية. لم يتم إجراء استدعاء فعلي لـ OpenAI API.",
                "criteria_weights": {"المعرفة": 25, "التطبيق": 25, "التحليل": 25, "التقييم": 25}
            }
        
        try:
            # تجميع المهام في نص واحد
            submissions_text = "\n\n".join([f"### المهمة {sub['id']}:\n```\n{sub['content']}\n```" for sub in submissions])
            
            # تحضير معايير التقييم
            criteria_text = ""
            if criteria:
                criteria_text = f"\n\nمعايير التقييم المخصصة:\n```json\n{json.dumps(criteria, ensure_ascii=False)}\n```"
            
            # إنشاء المطالبة (Prompt)
            prompt = f"""
            أنت مقيّم متخصص في مقارنة وترتيب مهام BTEC. قم بتحليل ومقارنة المهام التالية:
            
            {submissions_text}
            {criteria_text}
            
            قم بمقارنة المهام باستخدام معايير BTEC:
            1. المعرفة (Knowledge): فهم وتذكر المفاهيم والمصطلحات الأساسية
            2. التطبيق (Application): تطبيق المعرفة في سياقات عملية
            3. التحليل (Analysis): تحليل المعلومات وتفكيكها إلى أجزاء
            4. التقييم (Evaluation): تقييم الأفكار والحلول وإصدار أحكام مبررة
            
            قم بتقديم مقارنة شاملة بتنسيق JSON يتضمن الحقول التالية:
            1. rankings: قائمة بترتيب المهام حسب الجودة، كل عنصر يتضمن (id, rank, grade, score, feedback)
            2. comparison_notes: ملاحظات عامة حول المقارنة وأسباب الترتيب
            3. criteria_weights: الأوزان المستخدمة لكل معيار من معايير التقييم
            
            كن موضوعيًا وعادلًا في المقارنة، وقدم أسبابًا واضحة لترتيب المهام.
            """
            
            # إجراء استدعاء API
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "أنت مقيّم متخصص في مقارنة وترتيب مهام BTEC. مقارناتك موضوعية وعادلة ومبنية على معايير واضحة."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2,  # درجة حرارة منخفضة جدًا للحصول على تقييم متسق
                max_tokens=4000,
                response_format={"type": "json_object"}
            )
            
            # تحليل الاستجابة
            content = response.choices[0].message.content.strip()
            return json.loads(content)
            
        except Exception as e:
            logger.error(f"خطأ في مقارنة المهام: {e}")
            submission_ids = [sub["id"] for sub in submissions]
            return {
                "rankings": [{
                    "id": sub_id,
                    "rank": i+1,
                    "grade": "خطأ",
                    "score": 0,
                    "feedback": "غير متوفر بسبب خطأ"
                } for i, sub_id in enumerate(submission_ids)],
                "comparison_notes": f"حدث خطأ أثناء المقارنة: {str(e)}",
                "criteria_weights": {"المعرفة": 0, "التطبيق": 0, "التحليل": 0, "التقييم": 0}
            }
    
    def generate_custom_feedback(self, task: str, evaluation_result: Dict[str, Any], feedback_style: str = "مفصل") -> str:
        """
        إنشاء تعليقات مخصصة بناءً على نتيجة التقييم وأسلوب التعليق المطلوب
        
        Args:
            task: نص المهمة المقيمة
            evaluation_result: نتيجة التقييم السابق للمهمة
            feedback_style: أسلوب التعليق ('موجز'، 'مفصل'، 'إيجابي'، 'بناء')
            
        Returns:
            نص التعليق المخصص
        """
        if self.simulation_mode:
            return f"هذا تعليق محاكي بأسلوب {feedback_style}. لم يتم إجراء استدعاء فعلي لـ OpenAI API."
        
        try:
            # تحويل نتيجة التقييم إلى نص
            evaluation_text = json.dumps(evaluation_result, ensure_ascii=False, indent=2)
            
            # إنشاء المطالبة (Prompt)
            prompt = f"""
            أنت متخصص في كتابة تعليقات تعليمية. قم بإنشاء تعليق مخصص على المهمة التالية بناءً على نتيجة التقييم وبأسلوب {feedback_style}:
            
            المهمة:
            ```
            {task[:500]}...  # استخدام جزء من المهمة فقط للتوفير
            ```
            
            نتيجة التقييم:
            ```json
            {evaluation_text}
            ```
            
            أسلوب التعليق المطلوب: {feedback_style}
            
            إرشادات حسب الأسلوب:
            - موجز: تعليق قصير ومباشر يلخص النقاط الرئيسية (100-150 كلمة)
            - مفصل: تعليق شامل يتناول جميع جوانب المهمة بالتفصيل (300-500 كلمة)
            - إيجابي: التركيز على نقاط القوة والجوانب الإيجابية مع تشجيع الطالب
            - بناء: تقديم نقد بناء مع اقتراحات عملية للتحسين
            
            قدم تعليقًا مفيدًا يساعد الطالب على فهم تقييمه والتحسن في المستقبل.
            """
            
            # إجراء استدعاء API
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": f"أنت متخصص في كتابة تعليقات تعليمية بأسلوب {feedback_style}. تعليقاتك مفيدة وتحفيزية وتساعد الطلاب على التحسن."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.6,  # درجة حرارة متوسطة للسماح بإبداع أكبر في الصياغة
                max_tokens=1500
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"خطأ في إنشاء تعليق مخصص: {e}")
            return f"حدث خطأ أثناء إنشاء التعليق المخصص: {str(e)}"
    
    def check_plagiarism(self, main_text: str, references: List[str]) -> Dict[str, Any]:
        """
        التحقق من الانتحال الأكاديمي بمقارنة النص الرئيسي مع مراجع
        
        Args:
            main_text: النص الرئيسي للتحقق منه
            references: قائمة بالنصوص المرجعية للمقارنة
            
        Returns:
            نتيجة التحقق من الانتحال
        """
        if self.simulation_mode:
            return {
                "plagiarism_detected": False,
                "similarity_score": 0.15,
                "similar_passages": [],
                "originality_score": 0.85,
                "recommendation": "هذا تحليل محاكي للانتحال. لم يتم إجراء استدعاء فعلي لـ OpenAI API."
            }
        
        try:
            # تجميع النصوص المرجعية في نص واحد
            references_text = "\n\n".join([f"### المرجع {i+1}:\n```\n{ref[:300]}...\n```" for i, ref in enumerate(references)])
            
            # إنشاء المطالبة (Prompt)
            prompt = f"""
            أنت محلل متخصص في كشف الانتحال الأكاديمي. قم بفحص النص التالي ومقارنته بالمراجع المقدمة للكشف عن أي انتحال:
            
            النص الرئيسي:
            ```
            {main_text[:1000]}...  # استخدام جزء من النص فقط للتوفير
            ```
            
            النصوص المرجعية:
            {references_text}
            
            قم بتقديم تحليل شامل للانتحال بتنسيق JSON يتضمن الحقول التالية:
            1. plagiarism_detected: (boolean) هل تم اكتشاف انتحال واضح
            2. similarity_score: (float 0-1) درجة التشابه الإجمالي
            3. similar_passages: قائمة بالمقاطع المتشابهة، كل مقطع يتضمن (النص المنتحل، المرجع المطابق، رقم المرجع، درجة التشابه)
            4. originality_score: (float 0-1) درجة الأصالة
            5. recommendation: توصية حول كيفية التعامل مع هذه الحالة
            
            كن دقيقًا وموضوعيًا في تحليلك، وتجنب الاتهامات غير المبررة.
            """
            
            # إجراء استدعاء API
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "أنت محلل متخصص في كشف الانتحال الأكاديمي. تحليلاتك دقيقة وموضوعية ومبنية على أدلة واضحة."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2,
                max_tokens=2500,
                response_format={"type": "json_object"}
            )
            
            # تحليل الاستجابة
            content = response.choices[0].message.content.strip()
            return json.loads(content)
            
        except Exception as e:
            logger.error(f"خطأ في التحقق من الانتحال: {e}")
            return {
                "plagiarism_detected": False,
                "similarity_score": 0,
                "similar_passages": [],
                "originality_score": 0,
                "recommendation": f"حدث خطأ أثناء تحليل الانتحال: {str(e)}"
            }