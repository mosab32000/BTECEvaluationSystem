"""
وحدة واجهة برمجة التطبيقات لإدارة الحصص التفاعلية في نظام تقييم BTEC
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from backend.app.database import db
from backend.app.models import User, Session
from datetime import datetime

# إنشاء مخطط Blueprint
sessions_bp = Blueprint('sessions', __name__)

@sessions_bp.route('/sessions', methods=['GET'])
def get_sessions():
    """الحصول على قائمة جميع الحصص التفاعلية"""
    try:
        sessions = Session.query.all()
        return jsonify([{
            'id': session.id,
            'title': session.title,
            'date': session.session_date.strftime('%Y-%m-%d'),
            'time': session.session_time.strftime('%H:%M'),
            'description': session.description,
            'status': session.status,
            'created_by': session.created_by
        } for session in sessions]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@sessions_bp.route('/sessions', methods=['POST'])
@jwt_required()
def create_session():
    """إنشاء حصة تفاعلية جديدة"""
    user_id = get_jwt_identity()
    data = request.get_json()
    
    # التحقق من وجود البيانات المطلوبة
    if not all(key in data for key in ['title', 'session_date', 'session_time']):
        return jsonify({'error': 'بيانات غير كاملة'}), 400
    
    try:
        # تحويل النص إلى تاريخ ووقت
        session_date = datetime.strptime(data['session_date'], '%Y-%m-%d').date()
        session_time = datetime.strptime(data['session_time'], '%H:%M').time()
        
        # إنشاء حصة جديدة
        new_session = Session(
            title=data['title'],
            session_date=session_date,
            session_time=session_time,
            description=data.get('description', ''),
            status='scheduled',  # الحالة الافتراضية: مجدولة
            created_by=user_id,
            created_at=datetime.utcnow()
        )
        
        db.session.add(new_session)
        db.session.commit()
        
        return jsonify({
            'message': 'تم إنشاء الحصة بنجاح',
            'session_id': new_session.id
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@sessions_bp.route('/sessions/<int:session_id>', methods=['GET'])
def get_session(session_id):
    """الحصول على تفاصيل حصة محددة"""
    try:
        session = Session.query.get(session_id)
        if not session:
            return jsonify({'error': 'الحصة غير موجودة'}), 404
            
        return jsonify({
            'id': session.id,
            'title': session.title,
            'date': session.session_date.strftime('%Y-%m-%d'),
            'time': session.session_time.strftime('%H:%M'),
            'description': session.description,
            'status': session.status,
            'created_by': session.created_by,
            'created_at': session.created_at.isoformat()
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@sessions_bp.route('/sessions/<int:session_id>', methods=['PUT'])
@jwt_required()
def update_session(session_id):
    """تحديث معلومات حصة محددة"""
    user_id = get_jwt_identity()
    data = request.get_json()
    
    try:
        session = Session.query.get(session_id)
        if not session:
            return jsonify({'error': 'الحصة غير موجودة'}), 404
            
        # التحقق من أن المستخدم هو من أنشأ الحصة
        if session.created_by != user_id:
            return jsonify({'error': 'غير مصرح لك بتحديث هذه الحصة'}), 403
            
        # تحديث البيانات
        if 'title' in data:
            session.title = data['title']
        if 'session_date' in data:
            session.session_date = datetime.strptime(data['session_date'], '%Y-%m-%d').date()
        if 'session_time' in data:
            session.session_time = datetime.strptime(data['session_time'], '%H:%M').time()
        if 'description' in data:
            session.description = data['description']
        if 'status' in data:
            session.status = data['status']
            
        session.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({'message': 'تم تحديث الحصة بنجاح'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@sessions_bp.route('/sessions/<int:session_id>', methods=['DELETE'])
@jwt_required()
def delete_session(session_id):
    """حذف حصة محددة"""
    user_id = get_jwt_identity()
    
    try:
        session = Session.query.get(session_id)
        if not session:
            return jsonify({'error': 'الحصة غير موجودة'}), 404
            
        # التحقق من أن المستخدم هو من أنشأ الحصة
        if session.created_by != user_id:
            return jsonify({'error': 'غير مصرح لك بحذف هذه الحصة'}), 403
            
        db.session.delete(session)
        db.session.commit()
        
        return jsonify({'message': 'تم حذف الحصة بنجاح'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500