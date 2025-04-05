"""
نموذج معيار التقييم في نظام تقييم BTEC
"""
import json
import logging
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
            created_by (int, optional): معرف المستخدم الذي أنشأ معيار التقييم
            created_at (datetime, optional): تاريخ إنشاء معيار التقييم
        """
        self.id = kwargs.get('id')
        self.name = kwargs.get('name')
        self.description = kwargs.get('description')
        self.criteria = kwargs.get('criteria', {})
        
        # إذا كانت المعايير عبارة عن سلسلة نصية، نحاول تحويلها إلى كائن JSON
        if isinstance(self.criteria, str):
            try:
                self.criteria = json.loads(self.criteria)
            except json.JSONDecodeError:
                self.criteria = {}
        
        self.max_score = kwargs.get('max_score', 100)
        self.created_by = kwargs.get('created_by')
        self.created_at = kwargs.get('created_at')
    
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
    def get_by_creator(creator_id, limit=100, offset=0):
        """
        الحصول على قائمة معايير التقييم حسب المنشئ
        
        Args:
            creator_id (int): معرف المستخدم المنشئ
            limit (int, optional): الحد الأقصى للنتائج. الافتراضي هو 100.
            offset (int, optional): بداية النتائج. الافتراضي هو 0.
            
        Returns:
            list: قائمة كائنات معايير التقييم
        """
        try:
            query = "SELECT * FROM rubrics WHERE created_by = %s ORDER BY id LIMIT %s OFFSET %s"
            with get_db_cursor() as cursor:
                cursor.execute(query, (creator_id, limit, offset))
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
            
            # تحويل المعايير إلى تنسيق JSON للتخزين
            criteria_json = json.dumps(self.criteria) if self.criteria else '{}'
            
            # تحديث معيار التقييم الموجود
            if self.id:
                query = """
                    UPDATE rubrics SET 
                        name = %s,
                        description = %s,
                        criteria = %s,
                        max_score = %s
                    WHERE id = %s
                """
                cursor.execute(query, (
                    self.name,
                    self.description,
                    criteria_json,
                    self.max_score,
                    self.id
                ))
            
            # إنشاء معيار تقييم جديد
            else:
                query = """
                    INSERT INTO rubrics (name, description, criteria, max_score, created_by)
                    VALUES (%s, %s, %s, %s, %s)
                    RETURNING id
                """
                cursor.execute(query, (
                    self.name,
                    self.description,
                    criteria_json,
                    self.max_score,
                    self.created_by
                ))
                
                # الحصول على معرف معيار التقييم الجديد
                self.id = cursor.fetchone()[0]
            
            conn.commit()
            return True
        
        except Exception as e:
            conn.rollback()
            logger.error(f"خطأ في حفظ معيار التقييم: {e}")
            return False
        
        finally:
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
            
            query = "DELETE FROM rubrics WHERE id = %s"
            cursor.execute(query, (self.id,))
            
            conn.commit()
            return True
        
        except Exception as e:
            conn.rollback()
            logger.error(f"خطأ في حذف معيار التقييم: {e}")
            return False
        
        finally:
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
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    @staticmethod
    def create_default_rubric():
        """
        إنشاء معيار تقييم افتراضي
        
        Returns:
            Rubric: كائن معيار التقييم الافتراضي
        """
        default_criteria = {
            "content": {
                "title": "المحتوى",
                "description": "جودة وشمولية المحتوى المقدم",
                "levels": {
                    "1": "المحتوى غير كافٍ ولا يلبي الحد الأدنى من المتطلبات",
                    "2": "المحتوى أساسي ويلبي بعض المتطلبات",
                    "3": "المحتوى جيد ويلبي معظم المتطلبات",
                    "4": "المحتوى ممتاز وشامل ويلبي جميع المتطلبات"
                },
                "weight": 3
            },
            "organization": {
                "title": "التنظيم",
                "description": "تنظيم وهيكلة المحتوى",
                "levels": {
                    "1": "تنظيم ضعيف وصعب الفهم",
                    "2": "تنظيم مقبول ولكن يحتاج إلى تحسين",
                    "3": "تنظيم جيد ومنطقي",
                    "4": "تنظيم ممتاز ومتماسك ومنطقي"
                },
                "weight": 2
            },
            "analysis": {
                "title": "التحليل",
                "description": "عمق التحليل والتفكير النقدي",
                "levels": {
                    "1": "تحليل سطحي أو غائب",
                    "2": "بعض التحليل ولكن محدود",
                    "3": "تحليل جيد مع بعض الأفكار الأصلية",
                    "4": "تحليل عميق وأصلي مع تفكير نقدي ممتاز"
                },
                "weight": 3
            },
            "communication": {
                "title": "التواصل",
                "description": "وضوح وفعالية التواصل",
                "levels": {
                    "1": "صعوبة في فهم الرسالة بسبب أخطاء لغوية أو عرض ضعيف",
                    "2": "تواصل مقبول مع بعض الأخطاء",
                    "3": "تواصل جيد وواضح",
                    "4": "تواصل ممتاز وفعال ومقنع"
                },
                "weight": 2
            }
        }
        
        default_rubric = Rubric(
            name="معيار التقييم الافتراضي",
            description="معيار تقييم افتراضي للمهام العامة",
            criteria=default_criteria,
            max_score=100
        )
        
        return default_rubric
    
    def __repr__(self):
        """
        تمثيل معيار التقييم كسلسلة نصية
        
        Returns:
            str: تمثيل معيار التقييم
        """
        return f'<Rubric {self.name}>'