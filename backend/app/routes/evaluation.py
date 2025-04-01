from flask import request, jsonify, current_app
from backend.app.database import db
from backend.app.models import Evaluation
from backend.app.security.encryption import Vault
from backend.app.security.token_utils import token_required
from backend.app.services.ai_service import AIEvaluator
from backend.app.services.blockchain_service import BlockchainService
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

    encrypted_task = vault.encrypt(task)
    grade = ai_evaluator.evaluate(task)  # Evaluate the original task for now
    audit_hash = blockchain_service.record_grade(grade)

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
        output.append({
            'id': evaluation.id,
            'task': vault.decrypt(evaluation.task_encrypted),
            'grade': evaluation.grade,
            'audit_hash': evaluation.audit_hash,
            'submitted_at': evaluation.submitted_at
        })
    return jsonify(output), 200
