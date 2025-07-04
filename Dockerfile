# 1. الأساس من Python
FROM python:3.11-slim

# 2. تحديد مجلد العمل
WORKDIR /app

# 3. نسخ الملفات إلى الحاوية
COPY . .

# 4. تثبيت التبعيات
RUN pip install --upgrade pip && pip install -r requirements.txt

# 5. تعيين المنفذ الافتراضي
EXPOSE 8000

# 6. أمر التشغيل الأساسي
CMD ["python", "main.py"]