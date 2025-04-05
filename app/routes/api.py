"""
مسارات واجهة برمجة التطبيقات API في نظام تقييم BTEC
"""
import logging
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.models.user import User
from app.models.evaluation import Evaluation
from app.models.rubric import Rubric
from app.database import get_metrics

logger = logging.getLogger(__name__)

# استخدام Blueprint المعرف في __init__.py
from app.routes import api_bp

@api_bp.route('/health', methods=['GET'])
def health():
    """نقطة نهاية للتحقق من صحة النظام"""
    try:
        # التحقق من صحة قاعدة البيانات
        metrics = get_metrics()
        
        return jsonify({
            'status': 'healthy',
            'version': '1.0.0',
            'database': {
                'connected': True,
                'metrics': metrics
            }
        }), 200
    except Exception as e:
        logger.error(f"خطأ في نقطة نهاية الصحة: {str(e)}")
        return jsonify({
            'status': 'unhealthy',
            'error': str(e)
        }), 500

@api_bp.route('/info', methods=['GET'])
def info():
    """معلومات عامة عن النظام"""
    try:
        # الحصول على إحصائيات النظام
        metrics = get_metrics()
        
        return jsonify({
            'name': 'نظام تقييم BTEC',
            'version': '1.0.0',
            'description': 'منصة متكاملة لتقييم مهام BTEC باستخدام الذكاء الاصطناعي وتقنيات البلوكتشين',
            'features': [
                'تقييم ذكي بالذكاء الاصطناعي',
                'توثيق آمن بالبلوكتشين',
                'تحليلات وإحصائيات متقدمة',
                'تكامل مع أنظمة LMS',
                'نظام الشارات والتحفيز',
                'دعم كامل للغة العربية'
            ],
            'metrics': metrics
        }), 200
    except Exception as e:
        logger.error(f"خطأ في نقطة نهاية المعلومات: {str(e)}")
        return jsonify({
            'error': 'حدث خطأ أثناء الحصول على معلومات النظام',
            'details': str(e)
        }), 500

@api_bp.route('/rubrics', methods=['GET'])
@jwt_required()
def get_rubrics():
    """الحصول على قائمة معايير التقييم"""
    try:
        # الحصول على معايير التقييم
        rubrics = Rubric.get_all()
        
        return jsonify({
            'rubrics': [rubric.to_dict() for rubric in rubrics]
        }), 200
    except Exception as e:
        logger.error(f"خطأ في الحصول على معايير التقييم: {str(e)}")
        return jsonify({
            'error': 'حدث خطأ أثناء الحصول على معايير التقييم',
            'details': str(e)
        }), 500

@api_bp.route('/rubrics/<int:rubric_id>', methods=['GET'])
@jwt_required()
def get_rubric(rubric_id):
    """الحصول على معيار تقييم محدد"""
    try:
        # الحصول على معيار التقييم
        rubric = Rubric.get_by_id(rubric_id)
        
        if not rubric:
            return jsonify({
                'error': 'معيار التقييم غير موجود'
            }), 404
        
        return jsonify(rubric.to_dict()), 200
    except Exception as e:
        logger.error(f"خطأ في الحصول على معيار التقييم {rubric_id}: {str(e)}")
        return jsonify({
            'error': 'حدث خطأ أثناء الحصول على معيار التقييم',
            'details': str(e)
        }), 500

@api_bp.route('/statistics', methods=['GET'])
@jwt_required()
def get_statistics():
    """الحصول على إحصائيات النظام"""
    try:
        # التحقق من دور المستخدم (الإحصائيات للمسؤولين فقط)
        current_user_email = get_jwt_identity()
        user = User.get_by_email(current_user_email)
        
        if not user or user.role != 'admin':
            return jsonify({
                'error': 'ليس لديك صلاحية للوصول إلى هذه البيانات'
            }), 403
        
        # الحصول على إحصائيات التقييمات
        evaluation_stats = Evaluation.get_statistics()
        
        # الحصول على إحصائيات قاعدة البيانات
        db_metrics = get_metrics()
        
        # الحصول على عدد المستخدمين
        users = User.get_all()
        user_count = len(users)
        admin_count = len([u for u in users if u.role == 'admin'])
        
        return jsonify({
            'users': {
                'total': user_count,
                'admins': admin_count,
                'regular': user_count - admin_count
            },
            'evaluations': evaluation_stats,
            'database': db_metrics
        }), 200
    except Exception as e:
        logger.error(f"خطأ في الحصول على إحصائيات النظام: {str(e)}")
        return jsonify({
            'error': 'حدث خطأ أثناء الحصول على إحصائيات النظام',
            'details': str(e)
        }), 500

@api_bp.route('/search', methods=['GET'])
@jwt_required()
def search():
    """البحث في النظام"""
    try:
        # الحصول على معايير البحث
        query = request.args.get('q', '')
        type = request.args.get('type', 'all')
        
        if not query:
            return jsonify({
                'error': 'يجب توفير استعلام البحث'
            }), 400
        
        results = {
            'evaluations': [],
            'rubrics': [],
            'users': []
        }
        
        # البحث في التقييمات
        if type in ['all', 'evaluations']:
            evaluations = Evaluation.search(query)
            results['evaluations'] = [eval.to_dict() for eval in evaluations]
        
        # البحث في معايير التقييم
        if type in ['all', 'rubrics']:
            rubrics = Rubric.search(query)
            results['rubrics'] = [rubric.to_dict() for rubric in rubrics]
        
        # البحث في المستخدمين (للمسؤولين فقط)
        if type in ['all', 'users']:
            current_user_email = get_jwt_identity()
            user = User.get_by_email(current_user_email)
            
            if user and user.role == 'admin':
                # طريقة البحث ليست مضمنة في نموذج المستخدم، لذلك سنستخدم حلاً مؤقتًا
                all_users = User.get_all()
                search_users = [u for u in all_users if query.lower() in u.email.lower() or (u.name and query.lower() in u.name.lower())]
                results['users'] = [u.to_dict() for u in search_users]
        
        return jsonify({
            'query': query,
            'type': type,
            'results': results,
            'counts': {
                'evaluations': len(results['evaluations']),
                'rubrics': len(results['rubrics']),
                'users': len(results['users'])
            }
        }), 200
    except Exception as e:
        logger.error(f"خطأ في البحث: {str(e)}")
        return jsonify({
            'error': 'حدث خطأ أثناء البحث',
            'details': str(e)
        }), 500

@api_bp.route('/users/me', methods=['GET'])
@jwt_required()
def get_current_user():
    """الحصول على معلومات المستخدم الحالي"""
    try:
        current_user_email = get_jwt_identity()
        user = User.get_by_email(current_user_email)
        
        if not user:
            return jsonify({
                'error': 'المستخدم غير موجود'
            }), 404
        
        # الحصول على عدد التقييمات الخاصة بالمستخدم
        user_evaluations = Evaluation.get_by_user(user.id)
        total_evaluations = len(user_evaluations)
        completed_evaluations = len([e for e in user_evaluations if e.status == 'completed'])
        
        user_data = user.to_dict()
        user_data['stats'] = {
            'total_evaluations': total_evaluations,
            'completed_evaluations': completed_evaluations,
            'pending_evaluations': total_evaluations - completed_evaluations
        }
        
        return jsonify(user_data), 200
    except Exception as e:
        logger.error(f"خطأ في الحصول على معلومات المستخدم الحالي: {str(e)}")
        return jsonify({
            'error': 'حدث خطأ أثناء الحصول على معلومات المستخدم',
            'details': str(e)
        }), 500

@api_bp.route('/users/<int:user_id>', methods=['GET'])
@jwt_required()
def get_user(user_id):
    """الحصول على معلومات مستخدم محدد (للمسؤولين فقط)"""
    try:
        # التحقق من دور المستخدم
        current_user_email = get_jwt_identity()
        current_user = User.get_by_email(current_user_email)
        
        if not current_user or current_user.role != 'admin':
            return jsonify({
                'error': 'ليس لديك صلاحية للوصول إلى هذه البيانات'
            }), 403
        
        # الحصول على المستخدم المطلوب
        user = User.get_by_id(user_id)
        
        if not user:
            return jsonify({
                'error': 'المستخدم غير موجود'
            }), 404
        
        # الحصول على عدد التقييمات الخاصة بالمستخدم
        user_evaluations = Evaluation.get_by_user(user.id)
        total_evaluations = len(user_evaluations)
        completed_evaluations = len([e for e in user_evaluations if e.status == 'completed'])
        
        user_data = user.to_dict()
        user_data['stats'] = {
            'total_evaluations': total_evaluations,
            'completed_evaluations': completed_evaluations,
            'pending_evaluations': total_evaluations - completed_evaluations
        }
        
        return jsonify(user_data), 200
    except Exception as e:
        logger.error(f"خطأ في الحصول على معلومات المستخدم {user_id}: {str(e)}")
        return jsonify({
            'error': 'حدث خطأ أثناء الحصول على معلومات المستخدم',
            'details': str(e)
        }), 500

@api_bp.route('/users', methods=['GET'])
@jwt_required()
def get_users():
    """الحصول على قائمة المستخدمين (للمسؤولين فقط)"""
    try:
        # التحقق من دور المستخدم
        current_user_email = get_jwt_identity()
        current_user = User.get_by_email(current_user_email)
        
        if not current_user or current_user.role != 'admin':
            return jsonify({
                'error': 'ليس لديك صلاحية للوصول إلى هذه البيانات'
            }), 403
        
        # الحصول على المستخدمين
        users = User.get_all()
        
        return jsonify({
            'users': [user.to_dict() for user in users],
            'count': len(users)
        }), 200
    except Exception as e:
        logger.error(f"خطأ في الحصول على قائمة المستخدمين: {str(e)}")
        return jsonify({
            'error': 'حدث خطأ أثناء الحصول على قائمة المستخدمين',
            'details': str(e)
        }), 500

@api_bp.route('/users/<int:user_id>/toggle-active', methods=['POST'])
@jwt_required()
def toggle_user_active(user_id):
    """تغيير حالة تفعيل المستخدم (للمسؤولين فقط)"""
    try:
        # التحقق من دور المستخدم
        current_user_email = get_jwt_identity()
        current_user = User.get_by_email(current_user_email)
        
        if not current_user or current_user.role != 'admin':
            return jsonify({
                'error': 'ليس لديك صلاحية للقيام بهذه العملية'
            }), 403
        
        # الحصول على المستخدم المطلوب
        user = User.get_by_id(user_id)
        
        if not user:
            return jsonify({
                'error': 'المستخدم غير موجود'
            }), 404
        
        # لا يمكن تعطيل المستخدم نفسه
        if user.id == current_user.id:
            return jsonify({
                'error': 'لا يمكنك تغيير حالة تفعيل حسابك'
            }), 400
        
        # تغيير حالة التفعيل
        user.is_active = not user.is_active
        
        if user.save():
            logger.info(f"تم تغيير حالة تفعيل المستخدم {user.email} إلى {user.is_active} بواسطة {current_user.email}")
            return jsonify({
                'message': f"تم {'تفعيل' if user.is_active else 'تعطيل'} المستخدم بنجاح",
                'user': user.to_dict()
            }), 200
        else:
            return jsonify({
                'error': 'حدث خطأ أثناء تحديث حالة المستخدم'
            }), 500
    except Exception as e:
        logger.error(f"خطأ في تغيير حالة تفعيل المستخدم {user_id}: {str(e)}")
        return jsonify({
            'error': 'حدث خطأ أثناء تغيير حالة تفعيل المستخدم',
            'details': str(e)
        }), 500

@api_bp.route('/users/<int:user_id>/change-role', methods=['POST'])
@jwt_required()
def change_user_role(user_id):
    """تغيير دور المستخدم (للمسؤولين فقط)"""
    try:
        # التحقق من دور المستخدم
        current_user_email = get_jwt_identity()
        current_user = User.get_by_email(current_user_email)
        
        if not current_user or current_user.role != 'admin':
            return jsonify({
                'error': 'ليس لديك صلاحية للقيام بهذه العملية'
            }), 403
        
        # الحصول على البيانات
        data = request.get_json()
        new_role = data.get('role')
        
        if not new_role or new_role not in ['user', 'admin']:
            return jsonify({
                'error': 'الدور غير صالح'
            }), 400
        
        # الحصول على المستخدم المطلوب
        user = User.get_by_id(user_id)
        
        if not user:
            return jsonify({
                'error': 'المستخدم غير موجود'
            }), 404
        
        # لا يمكن تغيير دور المستخدم نفسه
        if user.id == current_user.id:
            return jsonify({
                'error': 'لا يمكنك تغيير دور حسابك'
            }), 400
        
        # تغيير الدور
        user.role = new_role
        
        if user.save():
            logger.info(f"تم تغيير دور المستخدم {user.email} إلى {new_role} بواسطة {current_user.email}")
            return jsonify({
                'message': f"تم تغيير دور المستخدم بنجاح إلى {new_role}",
                'user': user.to_dict()
            }), 200
        else:
            return jsonify({
                'error': 'حدث خطأ أثناء تحديث دور المستخدم'
            }), 500
    except Exception as e:
        logger.error(f"خطأ في تغيير دور المستخدم {user_id}: {str(e)}")
        return jsonify({
            'error': 'حدث خطأ أثناء تغيير دور المستخدم',
            'details': str(e)
        }), 500