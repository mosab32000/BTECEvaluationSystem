"""
نموذج التقييم في نظام تقييم BTEC
"""
import logging
import json
from datetime import datetime

from app.database import get_db_conn, get_db_cursor

# تهيئة السجل
logger = logging.getLogger(__name__)

class Evaluation:
    """نموذج التقييم في نظام تقييم BTEC"""
    
    def __init__(self, **kwargs):
        """
        تهيئة كائن التقييم
        
        Args:
            id (int, optional): معرف التقييم
            student_id (int, optional): معرف الطالب
            assignment_id (str, optional): معرف المهمة
            rubric_id (int, optional): معرف معيار التقييم
            submission_text (str, optional): نص المهمة المرسلة
            evaluation_result (dict, optional): نتيجة التقييم
            score (float, optional): الدرجة
            ai_score (float, optional): درجة الذكاء الاصطناعي
            evaluator_id (int, optional): معرف المقيم
            evaluator_comments (str, optional): تعليقات المقيم
            status (str, optional): حالة التقييم
            created_at (datetime, optional): تاريخ إنشاء التقييم
            updated_at (datetime, optional): تاريخ آخر تحديث
        """
        self.id = kwargs.get('id')
        self.student_id = kwargs.get('student_id')
        self.assignment_id = kwargs.get('assignment_id')
        self.rubric_id = kwargs.get('rubric_id')
        self.submission_text = kwargs.get('submission_text')
        
        # معالجة نتيجة التقييم كقاموس
        evaluation_result = kwargs.get('evaluation_result')
        if isinstance(evaluation_result, str):
            try:
                self.evaluation_result = json.loads(evaluation_result)
            except json.JSONDecodeError:
                self.evaluation_result = {}
        else:
            self.evaluation_result = evaluation_result or {}
        
        self.score = kwargs.get('score')
        self.ai_score = kwargs.get('ai_score')
        self.evaluator_id = kwargs.get('evaluator_id')
        self.evaluator_comments = kwargs.get('evaluator_comments')
        self.status = kwargs.get('status', 'pending')  # القيمة الافتراضية: pending
        self.created_at = kwargs.get('created_at')
        self.updated_at = kwargs.get('updated_at')
    
    @staticmethod
    def get_by_id(evaluation_id):
        """
        الحصول على التقييم بواسطة المعرف
        
        Args:
            evaluation_id (int): معرف التقييم
            
        Returns:
            Evaluation: كائن التقييم أو None إذا لم يتم العثور عليه
        """
        try:
            query = "SELECT * FROM evaluations WHERE id = %s"
            with get_db_cursor() as cursor:
                cursor.execute(query, (evaluation_id,))
                evaluation_data = cursor.fetchone()
                
                if evaluation_data:
                    evaluation_dict = dict(evaluation_data)
                    return Evaluation(**evaluation_dict)
                
            return None
        
        except Exception as e:
            logger.error(f"خطأ في الحصول على التقييم بواسطة المعرف: {e}")
            return None
    
    @staticmethod
    def get_all(limit=100, offset=0):
        """
        الحصول على قائمة التقييمات
        
        Args:
            limit (int, optional): الحد الأقصى للنتائج. الافتراضي هو 100.
            offset (int, optional): بداية النتائج. الافتراضي هو 0.
            
        Returns:
            list: قائمة كائنات التقييم
        """
        try:
            query = "SELECT * FROM evaluations ORDER BY id LIMIT %s OFFSET %s"
            with get_db_cursor() as cursor:
                cursor.execute(query, (limit, offset))
                evaluations_data = cursor.fetchall()
                
                evaluations = []
                for evaluation_data in evaluations_data:
                    evaluation_dict = dict(evaluation_data)
                    evaluations.append(Evaluation(**evaluation_dict))
                
                return evaluations
        
        except Exception as e:
            logger.error(f"خطأ في الحصول على قائمة التقييمات: {e}")
            return []
    
    @staticmethod
    def get_by_student_id(student_id, limit=100, offset=0):
        """
        الحصول على قائمة التقييمات حسب معرف الطالب
        
        Args:
            student_id (int): معرف الطالب
            limit (int, optional): الحد الأقصى للنتائج. الافتراضي هو 100.
            offset (int, optional): بداية النتائج. الافتراضي هو 0.
            
        Returns:
            list: قائمة كائنات التقييم
        """
        try:
            query = "SELECT * FROM evaluations WHERE student_id = %s ORDER BY id LIMIT %s OFFSET %s"
            with get_db_cursor() as cursor:
                cursor.execute(query, (student_id, limit, offset))
                evaluations_data = cursor.fetchall()
                
                evaluations = []
                for evaluation_data in evaluations_data:
                    evaluation_dict = dict(evaluation_data)
                    evaluations.append(Evaluation(**evaluation_dict))
                
                return evaluations
        
        except Exception as e:
            logger.error(f"خطأ في الحصول على قائمة التقييمات حسب معرف الطالب: {e}")
            return []
    
    @staticmethod
    def get_by_evaluator_id(evaluator_id, limit=100, offset=0):
        """
        الحصول على قائمة التقييمات حسب معرف المقيم
        
        Args:
            evaluator_id (int): معرف المقيم
            limit (int, optional): الحد الأقصى للنتائج. الافتراضي هو 100.
            offset (int, optional): بداية النتائج. الافتراضي هو 0.
            
        Returns:
            list: قائمة كائنات التقييم
        """
        try:
            query = "SELECT * FROM evaluations WHERE evaluator_id = %s ORDER BY id LIMIT %s OFFSET %s"
            with get_db_cursor() as cursor:
                cursor.execute(query, (evaluator_id, limit, offset))
                evaluations_data = cursor.fetchall()
                
                evaluations = []
                for evaluation_data in evaluations_data:
                    evaluation_dict = dict(evaluation_data)
                    evaluations.append(Evaluation(**evaluation_dict))
                
                return evaluations
        
        except Exception as e:
            logger.error(f"خطأ في الحصول على قائمة التقييمات حسب معرف المقيم: {e}")
            return []
    
    @staticmethod
    def get_by_status(status, limit=100, offset=0):
        """
        الحصول على قائمة التقييمات حسب الحالة
        
        Args:
            status (str): حالة التقييم (pending, completed, etc.)
            limit (int, optional): الحد الأقصى للنتائج. الافتراضي هو 100.
            offset (int, optional): بداية النتائج. الافتراضي هو 0.
            
        Returns:
            list: قائمة كائنات التقييم
        """
        try:
            query = "SELECT * FROM evaluations WHERE status = %s ORDER BY id LIMIT %s OFFSET %s"
            with get_db_cursor() as cursor:
                cursor.execute(query, (status, limit, offset))
                evaluations_data = cursor.fetchall()
                
                evaluations = []
                for evaluation_data in evaluations_data:
                    evaluation_dict = dict(evaluation_data)
                    evaluations.append(Evaluation(**evaluation_dict))
                
                return evaluations
        
        except Exception as e:
            logger.error(f"خطأ في الحصول على قائمة التقييمات حسب الحالة: {e}")
            return []
    
    @staticmethod
    def get_by_assignment_id(assignment_id, limit=100, offset=0):
        """
        الحصول على قائمة التقييمات حسب معرف المهمة
        
        Args:
            assignment_id (str): معرف المهمة
            limit (int, optional): الحد الأقصى للنتائج. الافتراضي هو 100.
            offset (int, optional): بداية النتائج. الافتراضي هو 0.
            
        Returns:
            list: قائمة كائنات التقييم
        """
        try:
            query = "SELECT * FROM evaluations WHERE assignment_id = %s ORDER BY id LIMIT %s OFFSET %s"
            with get_db_cursor() as cursor:
                cursor.execute(query, (assignment_id, limit, offset))
                evaluations_data = cursor.fetchall()
                
                evaluations = []
                for evaluation_data in evaluations_data:
                    evaluation_dict = dict(evaluation_data)
                    evaluations.append(Evaluation(**evaluation_dict))
                
                return evaluations
        
        except Exception as e:
            logger.error(f"خطأ في الحصول على قائمة التقييمات حسب معرف المهمة: {e}")
            return []
    
    def save(self):
        """
        حفظ التقييم في قاعدة البيانات (إنشاء أو تحديث)
        
        Returns:
            bool: ما إذا تم الحفظ بنجاح
        """
        try:
            conn = get_db_conn()
            cursor = conn.cursor()
            
            # الحصول على التاريخ الحالي للتحديث
            current_time = datetime.now()
            
            # تحويل نتيجة التقييم إلى JSON
            evaluation_result_json = json.dumps(self.evaluation_result)
            
            # تحديث تقييم موجود
            if self.id:
                query = """
                    UPDATE evaluations SET 
                        student_id = %s,
                        assignment_id = %s,
                        rubric_id = %s,
                        submission_text = %s,
                        evaluation_result = %s,
                        score = %s,
                        ai_score = %s,
                        evaluator_id = %s,
                        evaluator_comments = %s,
                        status = %s,
                        updated_at = %s
                    WHERE id = %s
                """
                cursor.execute(query, (
                    self.student_id,
                    self.assignment_id,
                    self.rubric_id,
                    self.submission_text,
                    evaluation_result_json,
                    self.score,
                    self.ai_score,
                    self.evaluator_id,
                    self.evaluator_comments,
                    self.status,
                    current_time,
                    self.id
                ))
            
            # إنشاء تقييم جديد
            else:
                query = """
                    INSERT INTO evaluations (
                        student_id, assignment_id, rubric_id, submission_text, evaluation_result, 
                        score, ai_score, evaluator_id, evaluator_comments, status, created_at, updated_at
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    RETURNING id
                """
                cursor.execute(query, (
                    self.student_id,
                    self.assignment_id,
                    self.rubric_id,
                    self.submission_text,
                    evaluation_result_json,
                    self.score,
                    self.ai_score,
                    self.evaluator_id,
                    self.evaluator_comments,
                    self.status,
                    current_time,
                    current_time
                ))
                
                # الحصول على معرف التقييم الجديد
                self.id = cursor.fetchone()[0]
                self.created_at = current_time
            
            self.updated_at = current_time
            conn.commit()
            return True
        
        except Exception as e:
            if conn:
                conn.rollback()
            logger.error(f"خطأ في حفظ التقييم: {e}")
            return False
        
        finally:
            if cursor:
                cursor.close()
    
    def delete(self):
        """
        حذف التقييم من قاعدة البيانات
        
        Returns:
            bool: ما إذا تم الحذف بنجاح
        """
        if not self.id:
            return False
        
        try:
            conn = get_db_conn()
            cursor = conn.cursor()
            
            # حذف التحققات من البلوكتشين المرتبطة بهذا التقييم
            blockchain_query = "DELETE FROM blockchain_verifications WHERE evaluation_id = %s"
            cursor.execute(blockchain_query, (self.id,))
            
            # حذف التقييم
            query = "DELETE FROM evaluations WHERE id = %s"
            cursor.execute(query, (self.id,))
            
            conn.commit()
            return True
        
        except Exception as e:
            if conn:
                conn.rollback()
            logger.error(f"خطأ في حذف التقييم: {e}")
            return False
        
        finally:
            if cursor:
                cursor.close()
    
    def to_dict(self):
        """
        تحويل التقييم إلى قاموس
        
        Returns:
            dict: بيانات التقييم كقاموس
        """
        return {
            'id': self.id,
            'student_id': self.student_id,
            'assignment_id': self.assignment_id,
            'rubric_id': self.rubric_id,
            'submission_text': self.submission_text,
            'evaluation_result': self.evaluation_result,
            'score': self.score,
            'ai_score': self.ai_score,
            'evaluator_id': self.evaluator_id,
            'evaluator_comments': self.evaluator_comments,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        """
        تمثيل التقييم كسلسلة نصية
        
        Returns:
            str: تمثيل التقييم
        """
        return f'<Evaluation {self.id}: {self.student_id}/{self.assignment_id}>'