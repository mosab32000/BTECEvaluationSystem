"""
ملف تكوين Gunicorn لنظام تقييم BTEC
"""

import multiprocessing
import os

# تعيين عدد العمليات (workers)
workers = int(os.getenv('GUNICORN_WORKERS', multiprocessing.cpu_count() * 2 + 1))

# تعيين عدد المواصفات (threads) لكل عملية
threads = int(os.getenv('GUNICORN_THREADS', 2))

# تعيين المنفذ
bind = '0.0.0.0:' + os.getenv('PORT', '5000')

# وقت انتهاء المهلة (بالثواني)
timeout = 120

# السجلات
accesslog = '-'
errorlog = '-'
loglevel = os.getenv('GUNICORN_LOG_LEVEL', 'info')

# تمكين إعادة التحميل في بيئة التطوير
reload = os.getenv('FLASK_ENV', 'production') == 'development'

# خيارات أخرى
worker_class = 'sync'
proc_name = 'btec_server'
keepalive = 5
max_requests = 1000
max_requests_jitter = 50
graceful_timeout = 60