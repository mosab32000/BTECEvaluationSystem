# استخدام خدمات الذكاء الاصطناعي في نظام تقييم BTEC

## مقدمة

يوفر نظام تقييم BTEC عدة طرق للتفاعل مع خدمات الذكاء الاصطناعي لتقييم مهام الطلاب. هذا المستند يشرح كيفية استخدام هذه الخدمات.

## الخدمات المتاحة

- **AIEvaluator**: الخدمة الأساسية التي تتطلب سياق تطبيق Flask
- **AIEvaluatorDirect**: نسخة مباشرة من المقيم لا تتطلب سياق Flask
- **AIEvaluatorArabic**: نسخة متخصصة بتقييم المهام باللغة العربية
- **AIEvaluatorMultimodal**: نسخة متقدمة تدعم تقييم النصوص والصور
- **AIEvaluatorAdvanced**: نسخة متقدمة مع ميزات إضافية للتحليل المعمق
- **AIEvaluatorREST**: نسخة مستقرة تستخدم REST API مباشرة (موصى بها للإنتاج)

## مثال على استخدام AIEvaluatorREST

`AIEvaluatorREST` هي الطريقة الموصى بها لتقييم المهام، حيث تتجاوز بعض مشكلات مكتبة OpenAI SDK:

```python
from backend.app.services import AIEvaluatorREST

# إنشاء مثيل من المقيم (يمكن توفير مفتاح API صراحةً أو استخدام المتغيرات البيئية)
evaluator = AIEvaluatorREST()

# تقييم مهمة بسيطة
task_text = """
BTEC Level 3 Business Assignment: Market Research Plan
Introduction:
This report presents a comprehensive market research plan for launching a new eco-friendly water bottle.
...
"""
result = evaluator.evaluate(task_text)
print(result)

# تقييم بتنسيق JSON
json_result = evaluator.evaluate_with_json(task_text)
print(f"Grade: {json_result['grade']}")
print(f"Feedback: {json_result['feedback']}")

# تقييم باستخدام معيار تقييم مخصص
custom_rubric = {
    "sections": [
        {
            "name": "Research Design",
            "weight": 30,
            "criteria": ["Appropriateness of methods", "Sample size", "Data collection approach"]
        },
        {
            "name": "Budget Planning",
            "weight": 20,
            "criteria": ["Cost breakdown", "Reasonableness", "Completeness"]
        },
        # ... المزيد من الأقسام ...
    ]
}
rubric_result = evaluator.evaluate_with_rubric(task_text, custom_rubric)
print(f"Overall score: {rubric_result['total_score']}")
```

## معالجة الأخطاء

تحتوي جميع خدمات التقييم على تعامل آمن مع الأخطاء وستعود بقيم خطأ بدلاً من رفع استثناءات غير معالجة:

```python
try:
    result = evaluator.evaluate(task_text)
    if result.startswith("Error"):
        # معالجة الخطأ
        print(f"حدث خطأ: {result}")
    else:
        # معالجة النتيجة
        print(f"التقييم: {result}")
except Exception as e:
    print(f"خطأ غير متوقع: {e}")
```

## استخدام المحاكاة عند عدم توفر مفتاح API

ستقوم جميع خدمات التقييم تلقائيًا بالتبديل إلى وضع المحاكاة إذا لم يكن مفتاح API متاحًا:

```python
# هذا سيعمل حتى بدون مفتاح API، ولكن سيعيد تقييمًا محاكى
evaluator = AIEvaluatorREST(api_key=None)
result = evaluator.evaluate(task_text)
print(result)  # سيبدأ بـ "This is a simulated evaluation"
```

## نصائح للاستخدام الأمثل

1. استخدم `AIEvaluatorREST` للحصول على أفضل توافق واستقرار
2. تأكد من وجود مفتاح OpenAI API صالح مع رصيد كافٍ
3. للبيئات الإنتاجية، ضع آلية للتعامل مع حالات تجاوز الحصة اليومية
4. استخدم التقييم بتنسيق JSON للتكامل مع واجهات المستخدم الديناميكية
5. قم بتخزين نتائج التقييم في قاعدة البيانات لتجنب إعادة التقييم غير الضرورية