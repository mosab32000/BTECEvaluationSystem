import os

# تكوين خادم Gunicorn لبيئة الإنتاج

# عدد عمليات العمال
workers = int(os.environ.get('GUNICORN_WORKERS', 4))

# المنفذ المراد الاستماع عليه
bind = '0.0.0.0:5000'

# نوع العمال
worker_class = 'sync'

# وقت التوقف عن الاستجابة (بالثواني)
timeout = 120

# وقت معالجة الطلب (بالثواني)
graceful_timeout = 120

# تكرار العمال عند استهلاك الذاكرة
max_requests = 1000
max_requests_jitter = 50

# تسجيل الأحداث
loglevel = 'info'
accesslog = '-'
errorlog = '-'

# وضع المصادقة
preload_app = True

# السماح بإعادة استخدام الأدلة المحلية
reuse_port = True