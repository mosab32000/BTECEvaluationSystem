"""
نموذج معايير التقييم في نظام تقييم BTEC
"""
import uuid
import json
from datetime import datetime

from app import db

class Rubric(db.Model):
    """نموذج معايير التقييم في نظام تقييم BTEC."""
    __tablename__ = 'rubric'
    
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(36), default=lambda: str(uuid.uuid4()), unique=True)
    
    # معلومات معايير التقييم
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    criteria = db.Column(db.Text, nullable=False)  # JSON نصي يحتوي على معايير التقييم
    template_type = db.Column(db.String(50), default='general')  # general, programming, project, etc.
    
    # العلاقات
    evaluations = db.relationship('Evaluation', backref='rubric', lazy='dynamic')
    
    # التوقيت
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # خيارات إضافية
    is_default = db.Column(db.Boolean, default=False)
    language = db.Column(db.String(10), default='ar')  # ar, en
    
    def __repr__(self):
        return f'<Rubric {self.id} - {self.name}>'
    
    def get_criteria_dict(self):
        """الحصول على قاموس معايير التقييم"""
        try:
            return json.loads(self.criteria)
        except:
            return {}
    
    def to_dict(self):
        """تحويل معايير التقييم إلى قاموس للواجهة البرمجية"""
        return {
            'id': self.id,
            'uuid': self.uuid,
            'name': self.name,
            'description': self.description,
            'criteria': self.get_criteria_dict(),
            'template_type': self.template_type,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'is_default': self.is_default,
            'language': self.language
        }
    
    @staticmethod
    def create_default_rubric(name, description, template_type):
        """
        إنشاء معايير تقييم افتراضية
        
        Args:
            name: اسم معايير التقييم
            description: وصف معايير التقييم
            template_type: نوع القالب (general, programming, etc.)
            
        Returns:
            Rubric: كائن معايير التقييم الجديد
        """
        criteria = {}
        
        if template_type == 'general':
            criteria = {
                "content": {
                    "name": "المحتوى",
                    "description": "جودة المحتوى ومدى ارتباطه بالمهمة",
                    "weight": 30,
                    "levels": {
                        "5": "ممتاز - المحتوى متميز وشامل ويتجاوز متطلبات المهمة",
                        "4": "جيد جداً - المحتوى شامل ويلبي جميع متطلبات المهمة",
                        "3": "جيد - المحتوى يلبي معظم متطلبات المهمة",
                        "2": "مقبول - المحتوى يلبي الحد الأدنى من متطلبات المهمة",
                        "1": "ضعيف - المحتوى لا يلبي متطلبات المهمة"
                    }
                },
                "structure": {
                    "name": "البنية والتنظيم",
                    "description": "تنظيم المحتوى وتسلسله المنطقي",
                    "weight": 20,
                    "levels": {
                        "5": "ممتاز - تنظيم استثنائي مع تسلسل منطقي متميز",
                        "4": "جيد جداً - تنظيم جيد جداً مع تسلسل منطقي واضح",
                        "3": "جيد - تنظيم مقبول مع بعض الخلل في التسلسل المنطقي",
                        "2": "مقبول - تنظيم ضعيف مع خلل واضح في التسلسل المنطقي",
                        "1": "ضعيف - لا يوجد تنظيم واضح أو تسلسل منطقي"
                    }
                },
                "language": {
                    "name": "اللغة والأسلوب",
                    "description": "صحة اللغة وجودة الأسلوب الكتابي",
                    "weight": 15,
                    "levels": {
                        "5": "ممتاز - لغة متميزة وأسلوب كتابي متميز",
                        "4": "جيد جداً - لغة صحيحة وأسلوب كتابي جيد",
                        "3": "جيد - بعض الأخطاء اللغوية وأسلوب كتابي مقبول",
                        "2": "مقبول - أخطاء لغوية متكررة وأسلوب كتابي ضعيف",
                        "1": "ضعيف - أخطاء لغوية كثيرة وأسلوب كتابي ركيك"
                    }
                },
                "research": {
                    "name": "البحث والتحليل",
                    "description": "جودة البحث والتحليل والتفكير النقدي",
                    "weight": 25,
                    "levels": {
                        "5": "ممتاز - بحث وتحليل متميز مع تفكير نقدي عميق",
                        "4": "جيد جداً - بحث وتحليل جيد مع تفكير نقدي واضح",
                        "3": "جيد - بحث وتحليل مقبول مع بعض التفكير النقدي",
                        "2": "مقبول - بحث وتحليل ضعيف مع قليل من التفكير النقدي",
                        "1": "ضعيف - لا يوجد بحث أو تحليل أو تفكير نقدي واضح"
                    }
                },
                "presentation": {
                    "name": "العرض والتقديم",
                    "description": "جودة تقديم المهمة والالتزام بالتنسيق المطلوب",
                    "weight": 10,
                    "levels": {
                        "5": "ممتاز - عرض متميز مع التزام كامل بالتنسيق المطلوب",
                        "4": "جيد جداً - عرض جيد مع التزام بالتنسيق المطلوب",
                        "3": "جيد - عرض مقبول مع بعض الخلل في التنسيق",
                        "2": "مقبول - عرض ضعيف مع خلل واضح في التنسيق",
                        "1": "ضعيف - عرض سيء مع عدم الالتزام بالتنسيق المطلوب"
                    }
                }
            }
        elif template_type == 'programming':
            criteria = {
                "functionality": {
                    "name": "الوظائف والمتطلبات",
                    "description": "مدى تحقيق البرنامج للوظائف والمتطلبات المطلوبة",
                    "weight": 30,
                    "levels": {
                        "5": "ممتاز - البرنامج يحقق جميع المتطلبات بتميز ويتجاوز التوقعات",
                        "4": "جيد جداً - البرنامج يحقق جميع المتطلبات بشكل كامل",
                        "3": "جيد - البرنامج يحقق معظم المتطلبات مع بعض القصور",
                        "2": "مقبول - البرنامج يحقق الحد الأدنى من المتطلبات",
                        "1": "ضعيف - البرنامج لا يحقق المتطلبات الأساسية"
                    }
                },
                "code_quality": {
                    "name": "جودة الكود",
                    "description": "جودة الكود من حيث التنظيم والأسلوب والأداء",
                    "weight": 25,
                    "levels": {
                        "5": "ممتاز - كود منظم بشكل استثنائي وأسلوب متميز وأداء عالي",
                        "4": "جيد جداً - كود منظم جيداً وأسلوب جيد وأداء مناسب",
                        "3": "جيد - كود منظم بشكل مقبول وأسلوب معقول وأداء مقبول",
                        "2": "مقبول - كود غير منظم بشكل جيد وأسلوب ضعيف وأداء ضعيف",
                        "1": "ضعيف - كود غير منظم وأسلوب سيء وأداء سيء"
                    }
                },
                "design": {
                    "name": "التصميم والبنية",
                    "description": "جودة تصميم البرنامج وبنيته الهيكلية",
                    "weight": 20,
                    "levels": {
                        "5": "ممتاز - تصميم متميز وبنية هيكلية متميزة",
                        "4": "جيد جداً - تصميم جيد وبنية هيكلية جيدة",
                        "3": "جيد - تصميم مقبول وبنية هيكلية مقبولة",
                        "2": "مقبول - تصميم ضعيف وبنية هيكلية ضعيفة",
                        "1": "ضعيف - تصميم سيء وبنية هيكلية سيئة"
                    }
                },
                "testing": {
                    "name": "الاختبار والتوثيق",
                    "description": "جودة اختبار البرنامج وتوثيقه",
                    "weight": 15,
                    "levels": {
                        "5": "ممتاز - اختبار شامل وتوثيق متميز",
                        "4": "جيد جداً - اختبار جيد وتوثيق جيد",
                        "3": "جيد - اختبار مقبول وتوثيق مقبول",
                        "2": "مقبول - اختبار ضعيف وتوثيق ضعيف",
                        "1": "ضعيف - لا يوجد اختبار أو توثيق"
                    }
                },
                "innovation": {
                    "name": "الابتكار والإبداع",
                    "description": "مستوى الابتكار والإبداع في حل المشكلة",
                    "weight": 10,
                    "levels": {
                        "5": "ممتاز - حل مبتكر وإبداعي بشكل استثنائي",
                        "4": "جيد جداً - حل مبتكر وإبداعي بشكل جيد",
                        "3": "جيد - حل يظهر بعض الابتكار والإبداع",
                        "2": "مقبول - حل تقليدي مع القليل من الابتكار",
                        "1": "ضعيف - حل تقليدي بدون أي ابتكار"
                    }
                }
            }
        
        # إنشاء كائن معايير التقييم
        return Rubric(
            name=name,
            description=description,
            criteria=json.dumps(criteria),
            template_type=template_type,
            is_default=True
        )