from flask import request, jsonify, current_app
from ..database import db
from ..models import Evaluation
from ..security.encryption import Vault
from ..security.token_utils import token_required
from ..services.ai_service_simple import AIEvaluator
from ..services.blockchain_service import BlockchainService
import json
import logging
from . import evaluation_bp
from datetime import datetime

@evaluation_bp.route('/evaluate', methods=['POST'])
@token_required
def evaluate(user_id):
    """
    Evaluate a BTEC task submission
    
    Request body:
    {
        "task": "The task submission content",
        "format": "text" or "json" (optional, defaults to "text")
    }
    """
    data = request.get_json()
    task = data.get('task')
    format_type = data.get('format', 'text')  # Default to text format

    if not task:
        return jsonify({
            'status': 'error',
            'message': 'Task submission is required'
        }), 400

    vault = Vault(current_app.config['ENCRYPTION_KEY'])
    blockchain_service = BlockchainService()
    ai_evaluator = AIEvaluator()

    # Encrypt the task submission
    encrypted_task = vault.encrypt(task)
    
    # Use the appropriate evaluation method based on format
    if format_type == 'json':
        try:
            # Get JSON structured evaluation
            grade_data = ai_evaluator.evaluate_with_json(task)
            # Save the grade as a JSON string in the database
            grade_json = json.dumps(grade_data)
            audit_hash = blockchain_service.record_grade(grade_json)
            
            new_evaluation = Evaluation(
                task_encrypted=encrypted_task, 
                grade=grade_json, 
                audit_hash=audit_hash, 
                user_id=user_id
            )
            db.session.add(new_evaluation)
            db.session.commit()
            
            return jsonify({
                'status': 'success',
                'evaluation_id': new_evaluation.id,
                'grade': grade_data.get('grade'),
                'feedback': grade_data.get('feedback'),
                'improvement_areas': grade_data.get('improvement_areas'),
                'audit_hash': audit_hash,
                'timestamp': datetime.utcnow().isoformat()
            }), 200
        except Exception as e:
            logging.error(f"Error in JSON evaluation: {e}")
            return jsonify({
                'status': 'error',
                'message': f'Error during evaluation: {str(e)}'
            }), 500
    else:
        # Original text format
        try:
            grade_text = ai_evaluator.evaluate(task)
            audit_hash = blockchain_service.record_grade(grade_text)
            
            new_evaluation = Evaluation(
                task_encrypted=encrypted_task, 
                grade=grade_text, 
                audit_hash=audit_hash, 
                user_id=user_id
            )
            db.session.add(new_evaluation)
            db.session.commit()
            
            return jsonify({
                'status': 'success',
                'evaluation_id': new_evaluation.id,
                'grade': grade_text,
                'audit_hash': audit_hash,
                'timestamp': datetime.utcnow().isoformat()
            }), 200
        except Exception as e:
            logging.error(f"Error in text evaluation: {e}")
            return jsonify({
                'status': 'error',
                'message': f'Error during evaluation: {str(e)}'
            }), 500

@evaluation_bp.route('/evaluations', methods=['GET'])
@token_required
def get_evaluations(user_id):
    """Get all evaluations for the authenticated user"""
    evaluations = Evaluation.query.filter_by(user_id=user_id).all()
    output = []
    vault = Vault(current_app.config['ENCRYPTION_KEY'])
    
    for evaluation in evaluations:
        # Decrypt the task submission for viewing
        try:
            decrypted_task = vault.decrypt(evaluation.task_encrypted)
        except Exception as e:
            logging.error(f"Decryption error: {e}")
            decrypted_task = "Error decrypting task"
        
        # Try to parse grade as JSON, if it fails, treat it as text
        try:
            grade_data = json.loads(evaluation.grade)
            evaluation_data = {
                'id': evaluation.id,
                'task': decrypted_task,
                'grade': grade_data.get('grade'),
                'feedback': grade_data.get('feedback'),
                'improvement_areas': grade_data.get('improvement_areas'),
                'format': 'json',
                'audit_hash': evaluation.audit_hash,
                'submitted_at': evaluation.submitted_at.isoformat() if evaluation.submitted_at else None
            }
        except (json.JSONDecodeError, TypeError) as e:
            # Handle as plain text
            evaluation_data = {
                'id': evaluation.id,
                'task': decrypted_task,
                'grade': evaluation.grade,
                'format': 'text',
                'audit_hash': evaluation.audit_hash,
                'submitted_at': evaluation.submitted_at.isoformat() if evaluation.submitted_at else None
            }
        
        output.append(evaluation_data)
    
    return jsonify({
        'status': 'success',
        'count': len(output),
        'evaluations': output
    }), 200

@evaluation_bp.route('/evaluation/<int:evaluation_id>', methods=['GET'])
@token_required
def get_evaluation(user_id, evaluation_id):
    """Get a specific evaluation by ID"""
    evaluation = Evaluation.query.filter_by(id=evaluation_id, user_id=user_id).first()
    
    if not evaluation:
        return jsonify({
            'status': 'error',
            'message': 'Evaluation not found or not authorized to access'
        }), 404
    
    vault = Vault(current_app.config['ENCRYPTION_KEY'])
    
    # Decrypt the task submission
    try:
        decrypted_task = vault.decrypt(evaluation.task_encrypted)
    except Exception as e:
        logging.error(f"Decryption error: {e}")
        decrypted_task = "Error decrypting task"
    
    # Try to parse grade as JSON, if it fails, treat it as text
    try:
        grade_data = json.loads(evaluation.grade)
        result = {
            'id': evaluation.id,
            'task': decrypted_task,
            'grade': grade_data.get('grade'),
            'feedback': grade_data.get('feedback'),
            'improvement_areas': grade_data.get('improvement_areas'),
            'format': 'json',
            'audit_hash': evaluation.audit_hash,
            'submitted_at': evaluation.submitted_at.isoformat() if evaluation.submitted_at else None
        }
    except (json.JSONDecodeError, TypeError) as e:
        result = {
            'id': evaluation.id,
            'task': decrypted_task,
            'grade': evaluation.grade,
            'format': 'text',
            'audit_hash': evaluation.audit_hash,
            'submitted_at': evaluation.submitted_at.isoformat() if evaluation.submitted_at else None
        }
    
    return jsonify({
        'status': 'success',
        'evaluation': result
    }), 200

@evaluation_bp.route('/verify/<string:audit_hash>', methods=['GET'])
def verify_evaluation(audit_hash):
    """
    Verify an evaluation using its blockchain audit hash
    This endpoint is public (doesn't require authentication)
    """
    if not audit_hash:
        return jsonify({
            'status': 'error',
            'message': 'Audit hash is required'
        }), 400
    
    blockchain_service = BlockchainService()
    verification_result = blockchain_service.verify_grade(audit_hash)
    
    if verification_result['verified']:
        # Find the evaluation in the database by audit hash
        evaluation = Evaluation.query.filter_by(audit_hash=audit_hash).first()
        
        if evaluation:
            return jsonify({
                'status': 'success',
                'verified': True,
                'details': verification_result['details'],
                'evaluation_date': evaluation.submitted_at.isoformat() if evaluation.submitted_at else None,
                'message': 'This evaluation record has been verified on the blockchain.'
            }), 200
        else:
            # Hash verified but no record found (could happen if database was reset but blockchain remains)
            return jsonify({
                'status': 'warning',
                'verified': True,
                'details': verification_result['details'],
                'message': 'Hash verified on blockchain, but no corresponding database record found.'
            }), 200
    else:
        return jsonify({
            'status': 'error',
            'verified': False,
            'reason': verification_result['reason'],
            'message': 'Could not verify this evaluation on the blockchain.'
        }), 404

@evaluation_bp.route('/evaluation/<int:evaluation_id>/verify', methods=['GET'])
@token_required
def verify_own_evaluation(user_id, evaluation_id):
    """
    Verify one of the user's own evaluations by ID
    This is an authenticated endpoint
    """
    evaluation = Evaluation.query.filter_by(id=evaluation_id, user_id=user_id).first()
    
    if not evaluation:
        return jsonify({
            'status': 'error',
            'message': 'Evaluation not found or not authorized to access'
        }), 404
    
    blockchain_service = BlockchainService()
    
    try:
        # For JSON format grades, pass the original grade for exact verification
        original_grade = evaluation.grade
        verification_result = blockchain_service.verify_grade(
            evaluation.audit_hash, 
            expected_grade=original_grade
        )
        
        if verification_result['verified']:
            return jsonify({
                'status': 'success',
                'verified': True,
                'evaluation_id': evaluation.id,
                'audit_hash': evaluation.audit_hash,
                'details': verification_result['details'],
                'message': 'Your evaluation has been verified on the blockchain.'
            }), 200
        else:
            return jsonify({
                'status': 'error',
                'verified': False,
                'evaluation_id': evaluation.id,
                'audit_hash': evaluation.audit_hash,
                'reason': verification_result['reason'],
                'message': 'Could not verify this evaluation on the blockchain.'
            }), 200
            
    except Exception as e:
        logging.error(f"Error verifying evaluation {evaluation_id}: {e}")
        return jsonify({
            'status': 'error',
            'message': f'Error during verification: {str(e)}'
        }), 500

@evaluation_bp.route('/evaluate/rubric', methods=['POST'])
@token_required
def evaluate_with_rubric(user_id):
    """
    Evaluate a BTEC task submission using a custom or default rubric
    
    Request body:
    {
        "task": "The task submission content",
        "rubric": {
            "sections": [
                {
                    "name": "Section name",
                    "weight": 25,
                    "criteria": ["Criterion 1", "Criterion 2", "Criterion 3"]
                },
                ...
            ]
        }
    }
    
    The rubric parameter is optional - if not provided, a default BTEC rubric will be used
    """
    data = request.get_json()
    task = data.get('task')
    custom_rubric = data.get('rubric')
    
    if not task:
        return jsonify({
            'status': 'error',
            'message': 'Task submission is required'
        }), 400
    
    vault = Vault(current_app.config['ENCRYPTION_KEY'])
    blockchain_service = BlockchainService()
    ai_evaluator = AIEvaluator()
    
    # Encrypt the task submission
    encrypted_task = vault.encrypt(task)
    
    try:
        # Get rubric-based evaluation
        evaluation_result = ai_evaluator.evaluate_with_rubric(task, custom_rubric)
        
        # Save the grade as a JSON string in the database
        grade_json = json.dumps(evaluation_result)
        audit_hash = blockchain_service.record_grade(grade_json)
        
        new_evaluation = Evaluation(
            task_encrypted=encrypted_task, 
            grade=grade_json, 
            audit_hash=audit_hash, 
            user_id=user_id
        )
        db.session.add(new_evaluation)
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'evaluation_id': new_evaluation.id,
            'grade': evaluation_result.get('grade'),
            'total_score': evaluation_result.get('total_score'),
            'sections': evaluation_result.get('sections'),
            'overall_feedback': evaluation_result.get('overall_feedback'),
            'audit_hash': audit_hash,
            'timestamp': datetime.utcnow().isoformat()
        }), 200
    except Exception as e:
        logging.error(f"Error in rubric evaluation: {e}")
        return jsonify({
            'status': 'error',
            'message': f'Error during evaluation: {str(e)}'
        }), 500