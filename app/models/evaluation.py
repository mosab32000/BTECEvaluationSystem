"""
نموذج التقييم في نظام تقييم BTEC
"""
import json
import logging
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
            submission_text (str, optional): نص التقديم
            evaluation_result (dict, optional): نتيجة التقييم
            score (float, optional): الدرجة
            ai_score (float, optional): درجة الذكاء الاصطناعي
            evaluator_id (int, optional): معرف المقيم
            evaluator_comments (str, optional): تعليقات المقيم
            status (str, optional): حالة التقييم
            created_at (datetime, optional): تاريخ إنشاء التقييم
            updated_at (datetime, optional): تاريخ تحديث التقييم
        """
        self.id = kwargs.get('id')
        self.student_id = kwargs.get('student_id')
        self.assignment_id = kwargs.get('assignment_id')
        self.rubric_id = kwargs.get('rubric_id')
        self.submission_text = kwargs.get('submission_text')
        self.evaluation_result = kwargs.get('evaluation_result', {})
        
        # إذا كانت نتيجة التقييم عبارة عن سلسلة نصية، نحاول تحويلها إلى كائن JSON
        if isinstance(self.evaluation_result, str):
            try:
                self.evaluation_result = json.loads(self.evaluation_result)
            except json.JSONDecodeError:
                self.evaluation_result = {}
        
        self.score = kwargs.get('score')
        self.ai_score = kwargs.get('ai_score')
        self.evaluator_id = kwargs.get('evaluator_id')
        self.evaluator_comments = kwargs.get('evaluator_comments')
        self.status = kwargs.get('status', 'pending')
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
            list: قائمة كائنات التقييمات
        """
        try:
            query = "SELECT * FROM evaluations ORDER BY id DESC LIMIT %s OFFSET %s"
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
    def get_by_student(student_id, limit=100, offset=0):
        """
        الحصول على قائمة التقييمات حسب الطالب
        
        Args:
            student_id (int): معرف الطالب
            limit (int, optional): الحد الأقصى للنتائج. الافتراضي هو 100.
            offset (int, optional): بداية النتائج. الافتراضي هو 0.
            
        Returns:
            list: قائمة كائنات التقييمات
        """
        try:
            query = "SELECT * FROM evaluations WHERE student_id = %s ORDER BY id DESC LIMIT %s OFFSET %s"
            with get_db_cursor() as cursor:
                cursor.execute(query, (student_id, limit, offset))
                evaluations_data = cursor.fetchall()
                
                evaluations = []
                for evaluation_data in evaluations_data:
                    evaluation_dict = dict(evaluation_data)
                    evaluations.append(Evaluation(**evaluation_dict))
                
                return evaluations
        
        except Exception as e:
            logger.error(f"خطأ في الحصول على قائمة التقييمات حسب الطالب: {e}")
            return []
    
    @staticmethod
    def get_by_user(evaluator_id, limit=100, offset=0):
        """
        الحصول على قائمة التقييمات حسب المقيم
        
        Args:
            evaluator_id (int): معرف المقيم
            limit (int, optional): الحد الأقصى للنتائج. الافتراضي هو 100.
            offset (int, optional): بداية النتائج. الافتراضي هو 0.
            
        Returns:
            list: قائمة كائنات التقييمات
        """
        try:
            query = "SELECT * FROM evaluations WHERE evaluator_id = %s ORDER BY id DESC LIMIT %s OFFSET %s"
            with get_db_cursor() as cursor:
                cursor.execute(query, (evaluator_id, limit, offset))
                evaluations_data = cursor.fetchall()
                
                evaluations = []
                for evaluation_data in evaluations_data:
                    evaluation_dict = dict(evaluation_data)
                    evaluations.append(Evaluation(**evaluation_dict))
                
                return evaluations
        
        except Exception as e:
            logger.error(f"خطأ في الحصول على قائمة التقييمات حسب المقيم: {e}")
            return []
    
    @staticmethod
    def get_by_status(status, limit=100, offset=0):
        """
        الحصول على قائمة التقييمات حسب الحالة
        
        Args:
            status (str): حالة التقييم
            limit (int, optional): الحد الأقصى للنتائج. الافتراضي هو 100.
            offset (int, optional): بداية النتائج. الافتراضي هو 0.
            
        Returns:
            list: قائمة كائنات التقييمات
        """
        try:
            query = "SELECT * FROM evaluations WHERE status = %s ORDER BY id DESC LIMIT %s OFFSET %s"
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
    
    def save(self):
        """
        حفظ التقييم في قاعدة البيانات (إنشاء أو تحديث)
        
        Returns:
            bool: ما إذا تم الحفظ بنجاح
        """
        try:
            conn = get_db_conn()
            cursor = conn.cursor()
            
            # تحويل نتيجة التقييم إلى تنسيق JSON للتخزين
            evaluation_result_json = json.dumps(self.evaluation_result) if self.evaluation_result else '{}'
            
            # الحصول على التاريخ الحالي للتحديث
            current_time = datetime.now()
            
            # تحديث التقييم الموجود
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
                        student_id, assignment_id, rubric_id, submission_text, 
                        evaluation_result, score, ai_score, evaluator_id, 
                        evaluator_comments, status, created_at, updated_at
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
            conn.rollback()
            logger.error(f"خطأ في حفظ التقييم: {e}")
            return False
        
        finally:
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
            
            # حذف أي سجلات تحقق مرتبطة بهذا التقييم أولاً
            verification_query = "DELETE FROM blockchain_verifications WHERE evaluation_id = %s"
            cursor.execute(verification_query, (self.id,))
            
            # ثم حذف التقييم نفسه
            query = "DELETE FROM evaluations WHERE id = %s"
            cursor.execute(query, (self.id,))
            
            conn.commit()
            return True
        
        except Exception as e:
            conn.rollback()
            logger.error(f"خطأ في حذف التقييم: {e}")
            return False
        
        finally:
            cursor.close()
    
    def get_verification(self):
        """
        الحصول على سجل التحقق من صحة التقييم
        
        Returns:
            dict: بيانات التحقق أو None إذا لم يتم العثور عليه
        """
        if not self.id:
            return None
        
        try:
            query = """
                SELECT * FROM blockchain_verifications 
                WHERE evaluation_id = %s 
                ORDER BY created_at DESC 
                LIMIT 1
            """
            with get_db_cursor() as cursor:
                cursor.execute(query, (self.id,))
                verification_data = cursor.fetchone()
                
                if verification_data:
                    return dict(verification_data)
                
            return None
        
        except Exception as e:
            logger.error(f"خطأ في الحصول على سجل التحقق من صحة التقييم: {e}")
            return None
    
    def add_verification(self, hash_value, transaction_id, verified=False):
        """
        إضافة سجل تحقق من صحة التقييم
        
        Args:
            hash_value (str): قيمة التجزئة
            transaction_id (str): معرف المعاملة
            verified (bool, optional): حالة التحقق. الافتراضي هو False.
            
        Returns:
            bool: ما إذا تمت الإضافة بنجاح
        """
        if not self.id:
            return False
        
        try:
            conn = get_db_conn()
            cursor = conn.cursor()
            
            query = """
                INSERT INTO blockchain_verifications (
                    evaluation_id, hash_value, transaction_id, verified
                )
                VALUES (%s, %s, %s, %s)
                RETURNING id
            """
            cursor.execute(query, (
                self.id,
                hash_value,
                transaction_id,
                verified
            ))
            
            verification_id = cursor.fetchone()[0]
            conn.commit()
            
            logger.info(f"تم إضافة سجل تحقق جديد: ID={verification_id}")
            return True
        
        except Exception as e:
            conn.rollback()
            logger.error(f"خطأ في إضافة سجل تحقق من صحة التقييم: {e}")
            return False
        
        finally:
            cursor.close()
    
    @staticmethod
    def get_statistics():
        """
        الحصول على إحصاءات التقييمات
        
        Returns:
            dict: إحصاءات التقييمات
        """
        try:
            stats = {
                'total': 0,
                'by_status': {},
                'avg_score': 0,
                'recent': []
            }
            
            # إجمالي التقييمات وتوزيعها حسب الحالة
            query_total = """
                SELECT status, COUNT(*) as count 
                FROM evaluations 
                GROUP BY status
            """
            with get_db_cursor() as cursor:
                cursor.execute(query_total)
                status_counts = cursor.fetchall()
                
                for status_data in status_counts:
                    status = status_data['status']
                    count = status_data['count']
                    stats['by_status'][status] = count
                    stats['total'] += count
            
            # متوسط الدرجات
            query_avg = """
                SELECT AVG(score) as avg_score 
                FROM evaluations 
                WHERE score IS NOT NULL
            """
            with get_db_cursor() as cursor:
                cursor.execute(query_avg)
                avg_data = cursor.fetchone()
                
                if avg_data and avg_data['avg_score']:
                    stats['avg_score'] = round(float(avg_data['avg_score']), 2)
            
            # التقييمات الأخيرة
            query_recent = """
                SELECT id, student_id, status, score, created_at 
                FROM evaluations 
                ORDER BY created_at DESC 
                LIMIT 5
            """
            with get_db_cursor() as cursor:
                cursor.execute(query_recent)
                recent_data = cursor.fetchall()
                
                for evaluation_data in recent_data:
                    stats['recent'].append(dict(evaluation_data))
            
            return stats
        
        except Exception as e:
            logger.error(f"خطأ في الحصول على إحصاءات التقييمات: {e}")
            return {
                'total': 0,
                'by_status': {},
                'avg_score': 0,
                'recent': []
            }
    
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
        return f'<Evaluation {self.id}: {self.status}>'