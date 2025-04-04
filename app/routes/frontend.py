"""
مسارات الواجهة الأمامية لنظام تقييم BTEC
"""
import os
from pathlib import Path

from flask import Blueprint, render_template, send_from_directory, redirect, url_for
from flask_jwt_extended import jwt_required, get_jwt_identity

# إنشاء Blueprint للواجهة الأمامية
frontend_bp = Blueprint('frontend', __name__)

@frontend_bp.route('/')
def index():
    """
    الصفحة الرئيسية
    """
    return render_template('index.html')

@frontend_bp.route('/login')
def login():
    """
    صفحة تسجيل الدخول
    """
    return render_template('index.html')

@frontend_bp.route('/register')
def register():
    """
    صفحة التسجيل
    """
    return render_template('index.html')

@frontend_bp.route('/dashboard')
def dashboard():
    """
    صفحة لوحة التحكم
    """
    return render_template('index.html')

@frontend_bp.route('/evaluation/new')
def new_evaluation():
    """
    صفحة إنشاء تقييم جديد
    """
    return render_template('index.html')

@frontend_bp.route('/evaluation/<int:evaluation_id>')
def evaluation_details(evaluation_id):
    """
    صفحة تفاصيل التقييم
    """
    return render_template('index.html')

@frontend_bp.route('/evaluations')
def evaluations_list():
    """
    صفحة قائمة التقييمات
    """
    return render_template('index.html')

@frontend_bp.route('/verify')
def verify_evaluation():
    """
    صفحة التحقق من صحة التقييم
    """
    return render_template('index.html')

@frontend_bp.route('/profile')
def user_profile():
    """
    صفحة الملف الشخصي للمستخدم
    """
    return render_template('index.html')

@frontend_bp.route('/admin')
def admin_dashboard():
    """
    لوحة تحكم المسؤول
    """
    return render_template('index.html')

@frontend_bp.route('/rubrics')
def rubrics_list():
    """
    صفحة قائمة معايير التقييم
    """
    return render_template('index.html')

@frontend_bp.route('/rubric/<int:rubric_id>')
def rubric_details(rubric_id):
    """
    صفحة تفاصيل معيار التقييم
    """
    return render_template('index.html')

@frontend_bp.route('/analytics')
def analytics():
    """
    صفحة تحليلات النظام
    """
    return render_template('index.html')

@frontend_bp.route('/help')
def help_page():
    """
    صفحة المساعدة
    """
    return render_template('index.html')

@frontend_bp.route('/about')
def about():
    """
    صفحة حول النظام
    """
    return render_template('index.html')

# عناصر الواجهة المشتركة
@frontend_bp.route('/components/sidebar')
def sidebar():
    """
    جزء الشريط الجانبي (للتحميل الديناميكي)
    """
    return render_template('components/sidebar.html')

@frontend_bp.route('/components/navbar')
def navbar():
    """
    جزء شريط التنقل (للتحميل الديناميكي)
    """
    return render_template('components/navbar.html')

@frontend_bp.route('/components/footer')
def footer():
    """
    جزء التذييل (للتحميل الديناميكي)
    """
    return render_template('components/footer.html')
