
from flask import Blueprint, jsonify

# Create health blueprint
health_bp = Blueprint('health', __name__, url_prefix='/health')

@health_bp.route('/')
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "ok"})
