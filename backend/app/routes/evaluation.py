from flask import request, jsonify, current_app
from ..database import db
from ..models import Evaluation
from ..security.encryption import Vault
from ..security.token_utils import token_required
from ..services.ai_service import AIEvaluator
from ..services.blockchain_service import BlockchainService
from . import evaluation_bp

@evaluation_bp.route('/evaluate', methods=['POST'])
@token_required
def evaluate(user_id):
    data = request.get_json()
    task = data.get('task')

    if not task:
        return jsonify({'message': 'Task submission is required'}), 400

    vault = Vault(current_app.config['ENCRYPTION_KEY'])
    blockchain_service = BlockchainService()
    ai_evaluator = AIEvaluator()

    # Encrypt the task submission
    encrypted_task = vault.encrypt(task)
    
    # Get AI evaluation
    grade = ai_evaluator.evaluate(task) # Evaluate the original task
    
    # Record grade on blockchain (or get simulated hash if blockchain is not configured)
    audit_hash = blockchain_service.record_grade(grade)

    # Save to database
    new_evaluation = Evaluation(task_encrypted=encrypted_task, grade=grade, audit_hash=audit_hash, user_id=user_id)
    db.session.add(new_evaluation)
    db.session.commit()

    return jsonify({
        'grade': grade,
        'audit_hash': audit_hash
    }), 200

@evaluation_bp.route('/evaluations', methods=['GET'])
@token_required
def get_evaluations(user_id):
    evaluations = Evaluation.query.filter_by(user_id=user_id).all()
    output = []
    vault = Vault(current_app.config['ENCRYPTION_KEY'])
    
    for evaluation in evaluations:
        # Decrypt the task submission for viewing
        try:
            decrypted_task = vault.decrypt(evaluation.task_encrypted)
        except Exception as e:
            decrypted_task = "Error decrypting task"
            
        output.append({
            'id': evaluation.id,
            'task': decrypted_task,
            'grade': evaluation.grade,
            'audit_hash': evaluation.audit_hash,
            'submitted_at': evaluation.submitted_at
        })
    
    return jsonify(output), 200