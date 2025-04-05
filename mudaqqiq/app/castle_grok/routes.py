"""
مسارات قلعة Grok الأسطورية
"""
from flask import render_template, redirect, url_for, request, jsonify, flash, current_app
from . import castle_grok

@castle_grok.route('/')
def index():
    """الصفحة الرئيسية لقلعة Grok"""
    return render_template('castle_grok/index.html')

@castle_grok.route('/api/tasks', methods=['GET', 'POST'])
def tasks_api():
    """واجهة برمجة التطبيقات للمهام"""
    if request.method == 'POST':
        # في التطبيق الفعلي، سيتم حفظ المهمة في قاعدة البيانات
        return jsonify({'status': 'success', 'message': 'تم استلام المهمة بنجاح'})
    else:
        # هنا سيتم استرجاع المهام من قاعدة البيانات
        return jsonify({'status': 'success', 'tasks': []})

@castle_grok.route('/api/chat', methods=['POST'])
def chat_api():
    """واجهة برمجة التطبيقات للدردشة"""
    message = request.json.get('message', '')
    if not message:
        return jsonify({'status': 'error', 'message': 'الرسالة فارغة'})
    
    # في التطبيق الفعلي، سيتم معالجة الرسالة وإرسالها إلى نموذج الذكاء الاصطناعي
    # هنا نحن نعيد رسالة بسيطة للتوضيح
    response = {
        'status': 'success',
        'reply': 'هذا رد من الخادم على رسالتك: ' + message
    }
    return jsonify(response)

@castle_grok.route('/api/attendance', methods=['POST'])
def attendance_api():
    """واجهة برمجة التطبيقات لتسجيل الحضور"""
    action = request.json.get('action', '')
    if action not in ['check_in', 'check_out']:
        return jsonify({'status': 'error', 'message': 'إجراء غير صالح'})
    
    # في التطبيق الفعلي، سيتم تسجيل الحضور في قاعدة البيانات
    return jsonify({'status': 'success', 'message': 'تم تسجيل ' + ('الحضور' if action == 'check_in' else 'الانصراف') + ' بنجاح'})

@castle_grok.route('/api/books', methods=['GET'])
def books_api():
    """واجهة برمجة التطبيقات للكتب والمصادر"""
    category = request.args.get('category', 'all')
    search = request.args.get('search', '')
    
    # في التطبيق الفعلي، سيتم استرجاع الكتب من قاعدة البيانات
    # هنا نعيد قائمة فارغة للتوضيح
    return jsonify({'status': 'success', 'books': []})

@castle_grok.route('/dashboard')
def dashboard():
    """لوحة تحكم قلعة Grok"""
    # هذا المسار يمكن استخدامه لإضافة لوحة تحكم منفصلة للمدرسين أو المشرفين
    return render_template('castle_grok/dashboard.html')