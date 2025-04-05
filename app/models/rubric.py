"""
نموذج معيار التقييم في نظام تقييم BTEC
"""
import logging
import json
from datetime import datetime

from app.database import get_db_conn, get_db_cursor

# تهيئة السجل
logger = logging.getLogger(__name__)

class Rubric:
    """نموذج معيار التقييم في نظام تقييم BTEC"""
    
    def __init__(self, **kwargs):
        """
        تهيئة كائن معيار التقييم
        
        Args:
            id (int, optional): معرف معيار التقييم
            name (str, optional): اسم معيار التقييم
            description (str, optional): وصف معيار التقييم
            criteria (dict, optional): معايير التقييم
            max_score (float, optional): الدرجة القصوى
            created_by (int, optional): معرف المستخدم الذي أنشأ المعيار
            created_at (datetime, optional): تاريخ إنشاء المعيار
            updated_at (datetime, optional): تاريخ آخر تحديث
        """
        self.id = kwargs.get('id')
        self.name = kwargs.get('name')
        self.description = kwargs.get('description')
        
        # معالجة معايير التقييم كقاموس
        criteria = kwargs.get('criteria')
        if isinstance(criteria, str):
            try:
                self.criteria = json.loads(criteria)
            except json.JSONDecodeError:
                self.criteria = {}
        else:
            self.criteria = criteria or {}
        
        self.max_score = kwargs.get('max_score', 100.0)
        self.created_by = kwargs.get('created_by')
        self.created_at = kwargs.get('created_at')
        self.updated_at = kwargs.get('updated_at')
    
    @staticmethod
    def get_by_id(rubric_id):
        """
        الحصول على معيار التقييم بواسطة المعرف
        
        Args:
            rubric_id (int): معرف معيار التقييم
            
        Returns:
            Rubric: كائن معيار التقييم أو None إذا لم يتم العثور عليه
        """
        try:
            query = "SELECT * FROM rubrics WHERE id = %s"
            with get_db_cursor() as cursor:
                cursor.execute(query, (rubric_id,))
                rubric_data = cursor.fetchone()
                
                if rubric_data:
                    rubric_dict = dict(rubric_data)
                    return Rubric(**rubric_dict)
                
            return None
        
        except Exception as e:
            logger.error(f"خطأ في الحصول على معيار التقييم بواسطة المعرف: {e}")
            return None
    
    @staticmethod
    def get_all(limit=100, offset=0):
        """
        الحصول على قائمة معايير التقييم
        
        Args:
            limit (int, optional): الحد الأقصى للنتائج. الافتراضي هو 100.
            offset (int, optional): بداية النتائج. الافتراضي هو 0.
            
        Returns:
            list: قائمة كائنات معايير التقييم
        """
        try:
            query = "SELECT * FROM rubrics ORDER BY id LIMIT %s OFFSET %s"
            with get_db_cursor() as cursor:
                cursor.execute(query, (limit, offset))
                rubrics_data = cursor.fetchall()
                
                rubrics = []
                for rubric_data in rubrics_data:
                    rubric_dict = dict(rubric_data)
                    rubrics.append(Rubric(**rubric_dict))
                
                return rubrics
        
        except Exception as e:
            logger.error(f"خطأ في الحصول على قائمة معايير التقييم: {e}")
            return []
    
    @staticmethod
    def get_by_created_by(user_id, limit=100, offset=0):
        """
        الحصول على قائمة معايير التقييم حسب المنشئ
        
        Args:
            user_id (int): معرف المستخدم
            limit (int, optional): الحد الأقصى للنتائج. الافتراضي هو 100.
            offset (int, optional): بداية النتائج. الافتراضي هو 0.
            
        Returns:
            list: قائمة كائنات معايير التقييم
        """
        try:
            query = "SELECT * FROM rubrics WHERE created_by = %s ORDER BY id LIMIT %s OFFSET %s"
            with get_db_cursor() as cursor:
                cursor.execute(query, (user_id, limit, offset))
                rubrics_data = cursor.fetchall()
                
                rubrics = []
                for rubric_data in rubrics_data:
                    rubric_dict = dict(rubric_data)
                    rubrics.append(Rubric(**rubric_dict))
                
                return rubrics
        
        except Exception as e:
            logger.error(f"خطأ في الحصول على قائمة معايير التقييم حسب المنشئ: {e}")
            return []
    
    def save(self):
        """
        حفظ معيار التقييم في قاعدة البيانات (إنشاء أو تحديث)
        
        Returns:
            bool: ما إذا تم الحفظ بنجاح
        """
        try:
            conn = get_db_conn()
            cursor = conn.cursor()
            
            # الحصول على التاريخ الحالي للتحديث
            current_time = datetime.now()
            
            # تحويل معايير التقييم إلى JSON
            criteria_json = json.dumps(self.criteria)
            
            # تحديث معيار تقييم موجود
            if self.id:
                query = """
                    UPDATE rubrics SET 
                        name = %s,
                        description = %s,
                        criteria = %s,
                        max_score = %s,
                        updated_at = %s
                    WHERE id = %s
                """
                cursor.execute(query, (
                    self.name,
                    self.description,
                    criteria_json,
                    self.max_score,
                    current_time,
                    self.id
                ))
            
            # إنشاء معيار تقييم جديد
            else:
                query = """
                    INSERT INTO rubrics (
                        name, description, criteria, max_score, created_by, created_at, updated_at
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    RETURNING id
                """
                cursor.execute(query, (
                    self.name,
                    self.description,
                    criteria_json,
                    self.max_score,
                    self.created_by,
                    current_time,
                    current_time
                ))
                
                # الحصول على معرف معيار التقييم الجديد
                self.id = cursor.fetchone()[0]
                self.created_at = current_time
            
            self.updated_at = current_time
            conn.commit()
            return True
        
        except Exception as e:
            if conn:
                conn.rollback()
            logger.error(f"خطأ في حفظ معيار التقييم: {e}")
            return False
        
        finally:
            if cursor:
                cursor.close()
    
    def delete(self):
        """
        حذف معيار التقييم من قاعدة البيانات
        
        Returns:
            bool: ما إذا تم الحذف بنجاح
        """
        if not self.id:
            return False
        
        try:
            conn = get_db_conn()
            cursor = conn.cursor()
            
            # التحقق من وجود تقييمات تستخدم هذا المعيار
            check_query = "SELECT COUNT(*) FROM evaluations WHERE rubric_id = %s"
            cursor.execute(check_query, (self.id,))
            count = cursor.fetchone()[0]
            
            if count > 0:
                logger.warning(f"لا يمكن حذف معيار التقييم {self.id} لأنه مستخدم في {count} تقييمات")
                return False
            
            # حذف معيار التقييم
            query = "DELETE FROM rubrics WHERE id = %s"
            cursor.execute(query, (self.id,))
            
            conn.commit()
            return True
        
        except Exception as e:
            if conn:
                conn.rollback()
            logger.error(f"خطأ في حذف معيار التقييم: {e}")
            return False
        
        finally:
            if cursor:
                cursor.close()
    
    def to_dict(self):
        """
        تحويل معيار التقييم إلى قاموس
        
        Returns:
            dict: بيانات معيار التقييم كقاموس
        """
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'criteria': self.criteria,
            'max_score': self.max_score,
            'created_by': self.created_by,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    @staticmethod
    def create_default_rubrics():
        """
        إنشاء معايير تقييم افتراضية
        
        Returns:
            bool: ما إذا تم إنشاء المعايير بنجاح
        """
        try:
            # معيار تقييم افتراضي للمهام العامة
            general_rubric = Rubric(
                name="معيار تقييم عام",
                description="معيار تقييم افتراضي للمهام العامة",
                criteria={
                    "المحتوى": {
                        "الوصف": "جودة المحتوى وملاءمته للموضوع",
                        "النقاط": 40
                    },
                    "التنظيم": {
                        "الوصف": "تنظيم وهيكلة المهمة",
                        "النقاط": 30
                    },
                    "اللغة": {
                        "الوصف": "سلامة اللغة والأسلوب",
                        "النقاط": 20
                    },
                    "التقديم": {
                        "الوصف": "جودة تقديم المهمة",
                        "النقاط": 10
                    }
                },
                max_score=100,
                created_by=1  # معرف المسؤول الافتراضي
            )
            
            # معيار تقييم افتراضي للمشاريع البرمجية
            programming_rubric = Rubric(
                name="معيار تقييم المشاريع البرمجية",
                description="معيار تقييم افتراضي للمشاريع والمهام البرمجية",
                criteria={
                    "الوظائف": {
                        "الوصف": "تنفيذ الوظائف المطلوبة",
                        "النقاط": 30
                    },
                    "جودة الكود": {
                        "الوصف": "جودة وتنظيم الشيفرة البرمجية",
                        "النقاط": 25
                    },
                    "الأداء": {
                        "الوصف": "أداء وكفاءة البرنامج",
                        "النقاط": 20
                    },
                    "واجهة المستخدم": {
                        "الوصف": "جودة وسهولة استخدام واجهة المستخدم",
                        "النقاط": 15
                    },
                    "التوثيق": {
                        "الوصف": "توثيق الشيفرة وكتابة التقرير",
                        "النقاط": 10
                    }
                },
                max_score=100,
                created_by=1  # معرف المسؤول الافتراضي
            )
            
            # حفظ المعايير
            general_rubric.save()
            programming_rubric.save()
            
            return True
        
        except Exception as e:
            logger.error(f"خطأ في إنشاء معايير التقييم الافتراضية: {e}")
            return False
    
    def __repr__(self):
        """
        تمثيل معيار التقييم كسلسلة نصية
        
        Returns:
            str: تمثيل معيار التقييم
        """
        return f'<Rubric {self.id}: {self.name}>'