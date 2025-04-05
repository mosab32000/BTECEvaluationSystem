import os
import secrets
import jwt
from datetime import datetime
from PIL import Image
from flask import current_app, url_for
from flask_mail import Message
from app import db, mail
from app.models import Notification, ActivityLog

def save_profile_image(form_picture):
    """
    حفظ وتعديل حجم صورة الملف الشخصي
    
    Args:
        form_picture: الصورة المرفوعة من النموذج
    
    Returns:
        str: اسم الملف بعد الحفظ
    """
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(current_app.root_path, 'static/uploads/profile_pics', picture_fn)
    
    # تعديل حجم الصورة
    output_size = (150, 150)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)
    
    return picture_fn

def save_project_file(form_file, project):
    """
    حفظ ملف المشروع
    
    Args:
        form_file: الملف المرفوع من النموذج
        project: كائن المشروع
    
    Returns:
        str: المسار النسبي للملف بعد الحفظ
    """
    filename = project.generate_unique_filename(form_file.filename)
    project_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], 'projects', str(project.id))
    os.makedirs(project_dir, exist_ok=True)
    
    file_path = os.path.join(project_dir, filename)
    form_file.save(file_path)
    
    return os.path.join('uploads/projects', str(project.id), filename)

def send_email(subject, recipients, html_body, sender=None):
    """
    إرسال بريد إلكتروني
    
    Args:
        subject: موضوع البريد الإلكتروني
        recipients: قائمة المستلمين
        html_body: محتوى البريد الإلكتروني بتنسيق HTML
        sender: المرسل (اختياري)
    
    Returns:
        bool: نجاح الإرسال
    """
    if not sender:
        sender = current_app.config['MAIL_DEFAULT_SENDER']
        
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.html = html_body
    
    try:
        mail.send(msg)
        return True
    except Exception as e:
        print(f"خطأ في إرسال البريد الإلكتروني: {e}")
        return False

def send_password_reset_email(user):
    """
    إرسال بريد إعادة تعيين كلمة المرور
    
    Args:
        user: كائن المستخدم
    
    Returns:
        bool: نجاح الإرسال
    """
    token = user.get_reset_password_token()
    return send_email(
        'إعادة تعيين كلمة المرور في منصة مُدقِّق',
        [user.email],
        render_template('email/reset_password.html', user=user, token=token)
    )

def create_notification(user_id, message, category='info'):
    """
    إنشاء إشعار جديد
    
    Args:
        user_id: معرف المستخدم
        message: نص الإشعار
        category: فئة الإشعار (اختياري)
    
    Returns:
        Notification: كائن الإشعار
    """
    notification = Notification(
        user_id=user_id,
        message=message,
        category=category
    )
    db.session.add(notification)
    db.session.commit()
    return notification

def log_activity(user, action, details=None, ip_address=None):
    """
    تسجيل نشاط المستخدم
    
    Args:
        user: كائن المستخدم
        action: الإجراء المتخذ
        details: تفاصيل إضافية (اختياري)
        ip_address: عنوان IP (اختياري)
    
    Returns:
        ActivityLog: كائن سجل النشاط
    """
    activity = ActivityLog(
        user_id=user.id if hasattr(user, 'id') else None,
        action=action,
        details=details,
        ip_address=ip_address
    )
    db.session.add(activity)
    db.session.commit()
    return activity

from flask import render_template
