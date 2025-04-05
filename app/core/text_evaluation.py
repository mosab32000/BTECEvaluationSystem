
"""
وحدة تقييم النصوص في نظام تقييم BTEC
"""
import logging
import random  # للنموذج البسيط

logger = logging.getLogger(__name__)

def evaluate_text_quality(text):
    """
    تقييم جودة النص المدخل باستخدام نموذج بسيط.
    يعيد قاموسًا يحتوي على 'score'، 'label'، وربما 'error'.
    """
    if not text or not isinstance(text, str) or not text.strip():
        logger.warning("تمت محاولة تقييم نص فارغ أو غير صالح.")
        return {"score": None, "label": "N/A", "error": "لا يوجد نص صالح مقدم للتقييم."}

    logger.debug(f"تقييم جودة النص (الطول: {len(text)})...")
    try:
        # تقييم بسيط بناءً على طول النص (هذا مجرد مثال)
        # في التطبيق الحقيقي، يمكن استخدام نموذج تعلم آلي متقدم
        
        word_count = len(text.split())
        char_count = len(text)
        
        # معايير تقييم بسيطة
        # 1. طول النص
        if word_count < 10:
            score = 0.3  # نص قصير جدًا
        elif word_count < 50:
            score = 0.5  # نص قصير
        elif word_count < 200:
            score = 0.7  # نص متوسط
        else:
            score = 0.9  # نص طويل
            
        # 2. تنوع الكلمات (بسيط)
        unique_words = len(set(text.lower().split()))
        word_diversity = unique_words / word_count if word_count > 0 else 0
        
        # ضبط الدرجة بناءً على التنوع
        score = score * (0.5 + 0.5 * min(1.0, word_diversity))
        
        # 3. إضافة عشوائية صغيرة للتنوع (للعرض فقط)
        score = min(1.0, max(0.0, score + random.uniform(-0.05, 0.05)))
        
        # تحديد التصنيف
        if score < 0.4:
            label = "Poor"
        elif score < 0.7:
            label = "Average"
        else:
            label = "Good"

        logger.info(f"نتيجة تقييم النص: Label='{label}', Score={score:.4f}")
        return {"score": float(score), "label": label}

    except Exception as e:
        logger.error(f"خطأ أثناء تقييم النص: {e}", exc_info=True)
        return {"score": None, "label": "Error", "error": f"حدث خطأ داخلي أثناء التقييم: {e}"}
