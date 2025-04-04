"""
وحدة واجهة برمجة التطبيقات الإدارية لنظام تقييم BTEC
"""

from flask import request, jsonify
from ..database import db
# استيراد النماذج من المجلد الرئيسي
from ..models import User, Evaluation
from ..security.token_utils import token_required
from datetime import datetime, timedelta
import json
from sqlalchemy import func
from . import admin_bp

@admin_bp.route('/stats', methods=['GET'])
@token_required
def get_dashboard_stats(user_id):
    """
    الحصول على إحصائيات لوحة التحكم الإدارية
    يتطلب مستخدمًا ذو صلاحيات إدارية (سيتم التحقق في الإصدار النهائي)
    """
    # في الإصدار النهائي، يجب التحقق من صلاحيات المستخدم الإدارية
    # مثال: 
    # user = User.query.get(user_id)
    # if not user.is_admin:
    #     return jsonify({'message': 'غير مصرح لك بالوصول إلى هذه البيانات'}), 403
    
    try:
        # إجمالي المستخدمين
        total_users = User.query.count()
        
        # إجمالي التقييمات
        total_evaluations = Evaluation.query.count()
        
        # التقييمات في اليوم الحالي
        today = datetime.utcnow().date()
        today_start = datetime.combine(today, datetime.min.time())
        today_end = datetime.combine(today, datetime.max.time())
        today_evaluations = Evaluation.query.filter(
            Evaluation.submitted_at.between(today_start, today_end)
        ).count()
        
        # حساب نسبة النجاح (افتراضياً 95%)
        # يمكن تعديل المنطق لحساب نسبة النجاح بناءً على معايير محددة
        success_rate = "95%"
        
        return jsonify({
            'total_users': total_users,
            'total_evaluations': total_evaluations,
            'today_evaluations': today_evaluations,
            'success_rate': success_rate
        }), 200
        
    except Exception as e:
        return jsonify({'message': f'حدث خطأ: {str(e)}'}), 500

@admin_bp.route('/evaluations/activity', methods=['GET'])
@token_required
def get_evaluation_activity(user_id):
    """
    الحصول على بيانات نشاط التقييم خلال فترة زمنية
    يدعم: أسبوع، شهر، سنة
    """
    period = request.args.get('period', 'month')
    
    try:
        today = datetime.utcnow().date()
        
        if period == 'week':
            start_date = today - timedelta(days=7)
            date_format = '%Y-%m-%d'
        elif period == 'month':
            start_date = today - timedelta(days=30)
            date_format = '%Y-%m-%d'
        elif period == 'year':
            start_date = today - timedelta(days=365)
            date_format = '%Y-%m'
        else:
            return jsonify({'message': 'فترة غير صالحة'}), 400
        
        start_datetime = datetime.combine(start_date, datetime.min.time())
        
        # الاستعلام عن عدد التقييمات لكل يوم/شهر
        if period == 'year':
            # تجميع حسب الشهر للسنة
            query_result = db.session.query(
                func.date_format(Evaluation.submitted_at, '%Y-%m').label('date'),
                func.count(Evaluation.id).label('count')
            ).filter(
                Evaluation.submitted_at >= start_datetime
            ).group_by(
                func.date_format(Evaluation.submitted_at, '%Y-%m')
            ).all()
        else:
            # تجميع حسب اليوم للأسبوع والشهر
            query_result = db.session.query(
                func.date_format(Evaluation.submitted_at, '%Y-%m-%d').label('date'),
                func.count(Evaluation.id).label('count')
            ).filter(
                Evaluation.submitted_at >= start_datetime
            ).group_by(
                func.date_format(Evaluation.submitted_at, '%Y-%m-%d')
            ).all()
        
        # تحويل النتائج إلى قاموس
        activity_data = {item.date: item.count for item in query_result}
        
        # إنشاء قائمة كاملة من التواريخ
        date_list = []
        counts = []
        
        current_date = start_date
        while current_date <= today:
            if period == 'year':
                date_str = current_date.strftime('%Y-%m')
                current_date = (current_date.replace(day=1) + timedelta(days=32)).replace(day=1)
            else:
                date_str = current_date.strftime('%Y-%m-%d')
                current_date += timedelta(days=1)
            
            date_list.append(date_str)
            counts.append(activity_data.get(date_str, 0))
        
        return jsonify({
            'labels': date_list,
            'data': counts
        }), 200
        
    except Exception as e:
        return jsonify({'message': f'حدث خطأ: {str(e)}'}), 500

@admin_bp.route('/grades/distribution', methods=['GET'])
@token_required
def get_grades_distribution(user_id):
    """
    الحصول على توزيع التقديرات
    """
    try:
        # في تطبيق حقيقي، نحتاج إلى تحليل حقول الدرجات وتصنيفها
        # هنا نعود ببيانات افتراضية مبسطة
        return jsonify({
            'labels': ['ممتاز', 'جيد جداً', 'جيد', 'مقبول', 'ضعيف'],
            'data': [42, 25, 18, 10, 5]
        }), 200
        
    except Exception as e:
        return jsonify({'message': f'حدث خطأ: {str(e)}'}), 500

@admin_bp.route('/recent/users', methods=['GET'])
@token_required
def get_recent_users(user_id):
    """
    الحصول على قائمة بأحدث المستخدمين
    """
    try:
        # جلب أحدث 5 مستخدمين
        recent_users = User.query.order_by(User.created_at.desc()).limit(5).all()
        
        users_list = []
        for user in recent_users:
            # عدد التقييمات لكل مستخدم
            eval_count = Evaluation.query.filter_by(user_id=user.id).count()
            
            users_list.append({
                'id': user.id,
                'email': user.email,
                'registered': user.created_at.strftime('%Y-%m-%d'),
                'evaluations': eval_count
            })
        
        return jsonify(users_list), 200
        
    except Exception as e:
        return jsonify({'message': f'حدث خطأ: {str(e)}'}), 500

@admin_bp.route('/recent/evaluations', methods=['GET'])
@token_required
def get_recent_evaluations(user_id):
    """
    الحصول على قائمة بأحدث التقييمات
    """
    try:
        # جلب أحدث 5 تقييمات مع بيانات المستخدم
        recent_evals = db.session.query(
            Evaluation, User.email
        ).join(
            User, Evaluation.user_id == User.id
        ).order_by(
            Evaluation.submitted_at.desc()
        ).limit(5).all()
        
        evals_list = []
        for eval_data, user_email in recent_evals:
            # استخراج الدرجة من حقل grade
            # هذا منطق مبسط؛ قد تحتاج إلى تعديله بناءً على تنسيق حقل grade
            grade = eval_data.grade.split(' ')[0] if eval_data.grade else 'غير محدد'
            
            evals_list.append({
                'id': eval_data.id,
                'user': user_email,
                'grade': grade,
                'date': eval_data.submitted_at.strftime('%Y-%m-%d %H:%M'),
                'verified': bool(eval_data.audit_hash)
            })
        
        return jsonify(evals_list), 200
        
    except Exception as e:
        return jsonify({'message': f'حدث خطأ: {str(e)}'}), 500

@admin_bp.route('/system/metrics', methods=['GET'])
@token_required
def get_system_metrics(user_id):
    """
    الحصول على مؤشرات أداء النظام
    """
    try:
        # في تطبيق حقيقي، هذه المعلومات ستأتي من مراقبة النظام
        return jsonify({
            'avg_evaluation_time': '2.7 ثانية',
            'avg_time_percentage': 65,
            'api_status': 'متاح',
            'api_status_percentage': 100,
            'resource_usage': '45%',
            'resource_usage_percentage': 45
        }), 200
        
    except Exception as e:
        return jsonify({'message': f'حدث خطأ: {str(e)}'}), 500