
"""
وحدة تحليل النصوص في نظام تقييم BTEC
"""
import os
import logging

logger = logging.getLogger(__name__)

def read_text_from_file(file_path):
    """
    قراءة محتوى النص من ملفات مختلفة (txt, docx, pdf).
    يرجع (رسالة_خطأ، محتوى_النص).
    """
    if not os.path.exists(file_path):
        return f"الملف غير موجود: {file_path}", None

    _, file_extension = os.path.splitext(file_path)
    file_extension = file_extension.lower()
    text_content = ""
    error_message = None

    logger.debug(f"محاولة قراءة الملف: {file_path} (امتداد: {file_extension})")

    try:
        if file_extension == '.txt':
            # محاولة الترميزات الشائعة
            encodings_to_try = ['utf-8', 'latin-1', 'windows-1252']
            for encoding in encodings_to_try:
                try:
                    with open(file_path, 'r', encoding=encoding) as f:
                        text_content = f.read()
                    logger.info(f"تمت قراءة ملف .txt '{os.path.basename(file_path)}' بترميز '{encoding}'.")
                    break
                except UnicodeDecodeError:
                    logger.debug(f"فشل في فك ترميز .txt باستخدام {encoding}، جارٍ تجربة التالي...")
                    continue
            else:
                error_message = f"تعذر فك ترميز ملف .txt باستخدام الترميزات المحاولة: {encodings_to_try}."
                logger.error(error_message)
        else:
            error_message = f"نوع الملف غير مدعوم للاستخراج المباشر للنص: '{file_extension}'"
            logger.warning(error_message)

        # فحص نهائي وإرجاع
        if error_message:
            return error_message, None
        else:
            return None, text_content.strip()

    except Exception as e:
        logger.error(f"خطأ في قراءة الملف {os.path.basename(file_path)}: {e}", exc_info=True)
        return f"خطأ غير متوقع في معالجة الملف: {e}", None

def analyze_text_content(text):
    """
    تحليل محتوى النص باستخدام تقنيات NLP أساسية.
    يعيد قاموسًا يحتوي على نتائج التحليل أو خطأ.
    """
    if not text or not isinstance(text, str) or not text.strip():
        logger.warning("تمت محاولة تحليل مدخل نصي فارغ أو غير صالح.")
        return {"errors": [], "entities": [], "warning": "لم يتم توفير محتوى نصي صالح للتحليل."}

    logger.info(f"تحليل محتوى النص (الطول: {len(text)})...")
    try:
        # معالجة النص
        words = text.split()
        sentences = text.split('.')
        
        # تحليل أساسي بسيط
        analysis_results = {
            "word_count": len(words),
            "sentence_count": max(1, len(sentences) - 1),  # تعديل بسيط لحساب الجمل
            "potential_spelling_errors": [],
            "entities": []
        }
        
        logger.info(f"اكتمل التحليل. تم العثور على {len(analysis_results['entities'])} كيانات.")
        return analysis_results

    except Exception as e:
        logger.error(f"خطأ أثناء تحليل النص: {e}", exc_info=True)
        return {"error": f"حدث خطأ داخلي أثناء تحليل النص: {e}"}
