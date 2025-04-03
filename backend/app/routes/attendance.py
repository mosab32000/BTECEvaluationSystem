"""
وحدة واجهة برمجة التطبيقات لإدارة سجل الحضور والغياب في نظام تقييم BTEC
"""

from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..database import db
from ..models import User
from ..models.attendance import Student, Attendance
from datetime import datetime
from . import attendance_bp

@attendance_bp.route('/attendance', methods=['GET'])
@jwt_required()
def get_attendance_records():
    """الحصول على سجلات الحضور والغياب"""
    try:
        # يمكن تصفية السجلات حسب التاريخ أو الطالب
        student_id = request.args.get('student_id')
        date = request.args.get('date')
        
        query = Attendance.query
        
        if student_id:
            query = query.filter_by(student_id=student_id)
        if date:
            query = query.filter_by(attendance_date=datetime.strptime(date, '%Y-%m-%d').date())
            
        records = query.all()
        
        return jsonify([{
            'id': record.id,
            'student_id': record.student_id,
            'date': record.attendance_date.strftime('%Y-%m-%d'),
            'status': record.status,
            'recorded_by': record.recorded_by
        } for record in records]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@attendance_bp.route('/attendance', methods=['POST'])
@jwt_required()
def record_attendance():
    """تسجيل حضور أو غياب طالب"""
    user_id = get_jwt_identity()
    data = request.get_json()
    
    # التحقق من وجود البيانات المطلوبة
    if not all(key in data for key in ['student_id', 'status']):
        return jsonify({'error': 'بيانات غير كاملة'}), 400
    
    try:
        # التحقق من صحة حالة الحضور
        if data['status'] not in ['present', 'absent', 'late', 'excused']:
            return jsonify({'error': 'حالة حضور غير صالحة'}), 400
            
        # معالجة التاريخ
        attendance_date = datetime.utcnow().date()
        if 'attendance_date' in data and data['attendance_date']:
            attendance_date = datetime.strptime(data['attendance_date'], '%Y-%m-%d').date()
            
        # التحقق من وجود الطالب
        student = Student.query.get(data['student_id'])
        if not student:
            return jsonify({'error': 'الطالب غير موجود'}), 404
            
        # التحقق من عدم وجود سجل سابق لنفس اليوم
        existing_record = Attendance.query.filter_by(
            student_id=data['student_id'],
            attendance_date=attendance_date
        ).first()
        
        if existing_record:
            # تحديث السجل الموجود
            existing_record.status = data['status']
            existing_record.updated_at = datetime.utcnow()
            db.session.commit()
            return jsonify({'message': 'تم تحديث سجل الحضور بنجاح'}), 200
        
        # إنشاء سجل جديد
        new_record = Attendance(
            student_id=data['student_id'],
            attendance_date=attendance_date,
            status=data['status'],
            recorded_by=user_id,
            created_at=datetime.utcnow()
        )
        
        db.session.add(new_record)
        db.session.commit()
        
        return jsonify({
            'message': 'تم تسجيل الحضور بنجاح',
            'record_id': new_record.id
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@attendance_bp.route('/attendance/<int:record_id>', methods=['PUT'])
@jwt_required()
def update_attendance(record_id):
    """تحديث سجل حضور محدد"""
    user_id = get_jwt_identity()
    data = request.get_json()
    
    try:
        record = Attendance.query.get(record_id)
        if not record:
            return jsonify({'error': 'سجل الحضور غير موجود'}), 404
            
        # التحقق من أن المستخدم هو من سجل الحضور أو لديه صلاحيات مناسبة
        if record.recorded_by != user_id:
            # يمكن هنا إضافة منطق التحقق من الصلاحيات
            return jsonify({'error': 'غير مصرح لك بتحديث هذا السجل'}), 403
            
        # تحديث البيانات
        if 'status' in data:
            record.status = data['status']
        if 'attendance_date' in data:
            record.attendance_date = datetime.strptime(data['attendance_date'], '%Y-%m-%d').date()
            
        record.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({'message': 'تم تحديث سجل الحضور بنجاح'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@attendance_bp.route('/attendance/<int:record_id>', methods=['DELETE'])
@jwt_required()
def delete_attendance(record_id):
    """حذف سجل حضور محدد"""
    user_id = get_jwt_identity()
    
    try:
        record = Attendance.query.get(record_id)
        if not record:
            return jsonify({'error': 'سجل الحضور غير موجود'}), 404
            
        # التحقق من أن المستخدم هو من سجل الحضور أو لديه صلاحيات مناسبة
        if record.recorded_by != user_id:
            # يمكن هنا إضافة منطق التحقق من الصلاحيات
            return jsonify({'error': 'غير مصرح لك بحذف هذا السجل'}), 403
            
        db.session.delete(record)
        db.session.commit()
        
        return jsonify({'message': 'تم حذف سجل الحضور بنجاح'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@attendance_bp.route('/attendance/students/<int:student_id>', methods=['GET'])
@jwt_required()
def get_student_attendance(student_id):
    """الحصول على سجل حضور طالب محدد"""
    try:
        # التحقق من وجود الطالب
        student = Student.query.get(student_id)
        if not student:
            return jsonify({'error': 'الطالب غير موجود'}), 404
            
        records = Attendance.query.filter_by(student_id=student_id).all()
        
        # حساب إحصائيات الحضور
        total_days = len(records)
        present_days = sum(1 for record in records if record.status == 'present')
        absent_days = sum(1 for record in records if record.status == 'absent')
        late_days = sum(1 for record in records if record.status == 'late')
        excused_days = sum(1 for record in records if record.status == 'excused')
        
        attendance_rate = 0
        if total_days > 0:
            attendance_rate = (present_days / total_days) * 100
            
        return jsonify({
            'student_id': student_id,
            'student_name': f"{student.first_name} {student.last_name}",
            'total_days': total_days,
            'present_days': present_days,
            'absent_days': absent_days,
            'late_days': late_days,
            'excused_days': excused_days,
            'attendance_rate': round(attendance_rate, 2),
            'records': [{
                'date': record.attendance_date.strftime('%Y-%m-%d'),
                'status': record.status
            } for record in records]
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500