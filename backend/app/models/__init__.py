"""
نماذج قاعدة البيانات لنظام تقييم BTEC
"""

# استيراد نماذج الحضور
from .attendance import Student, Session, Attendance

# تصدير النماذج للوحدات الأخرى
__all__ = ['Student', 'Session', 'Attendance']