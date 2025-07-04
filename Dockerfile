# صورة أساسية خفيفة
FROM python:3.11-slim

# مجلد العمل داخل الحاوية
WORKDIR /app

# نسخ جميع ملفات المشروع
COPY . .

# تحديث pip وتثبيت التبعيات
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# فتح المنفذ الذي يستخدمه التطبيق
EXPOSE 8000

# أمر التشغيل الافتراضي
# إذا كان المشروع يستخدم Flask:
# CMD ["flask", "run", "--host=0.0.0.0", "--port=8000"]

# إذا كان المشروع يستخدم FastAPI مع Uvicorn:
# CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

# أو الأمر العام (لتشغيل main.py مباشرة):
CMD ["python", "main.py"]