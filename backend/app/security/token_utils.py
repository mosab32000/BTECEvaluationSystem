import jwt
from datetime import datetime, timedelta
from flask import current_app, request, jsonify
from functools import wraps

def generate_token(user_id):
    payload = {
        'exp': datetime.utcnow() + timedelta(days=1),  # Token expires in 1 day for testing
        'iat': datetime.utcnow(),
        'sub': user_id
    }
    return jwt.encode(payload, current_app.config['JWT_SECRET_KEY'], algorithm='HS256')

def verify_token(token):
    try:
        payload = jwt.decode(token, current_app.config['JWT_SECRET_KEY'], algorithms=['HS256'])
        return payload['sub']
    except jwt.ExpiredSignatureError:
        return None  # Token has expired
    except jwt.InvalidTokenError:
        return None  # Invalid token

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        auth_header = request.headers.get('Authorization')
        
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
        
        if not token:
            return jsonify({'message': 'Token is missing'}), 401
        
        user_id = verify_token(token)
        if not user_id:
            return jsonify({'message': 'Invalid or expired token'}), 401
        
        return f(user_id, *args, **kwargs)
    
    return decorated