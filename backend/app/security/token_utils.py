import jwt
from datetime import datetime, timedelta
from flask import current_app, request, jsonify
from functools import wraps
import logging

def generate_token(user_id):
    """
    Generate a JWT token for the given user_id
    """
    try:
        payload = {
            'exp': datetime.utcnow() + timedelta(days=1),  # Token expires in 1 day for testing
            'iat': datetime.utcnow(),
            'sub': user_id
        }
        return jwt.encode(payload, current_app.config['JWT_SECRET_KEY'], algorithm='HS256')
    except Exception as e:
        logging.error(f"Error generating token: {e}")
        raise Exception(f"Could not generate authentication token: {str(e)}")

def verify_token(token):
    """
    Verify and decode a JWT token
    Returns the user_id on success, None on failure
    """
    try:
        payload = jwt.decode(token, current_app.config['JWT_SECRET_KEY'], algorithms=['HS256'])
        return payload['sub']
    except jwt.ExpiredSignatureError:
        logging.warning("Token verification failed: Token has expired")
        return None  # Token has expired
    except jwt.InvalidTokenError as e:
        logging.warning(f"Token verification failed: Invalid token - {e}")
        return None  # Invalid token
    except Exception as e:
        logging.error(f"Unexpected error during token verification: {e}")
        return None

def token_required(f):
    """
    Decorator to require a valid JWT token for route access
    Passes the extracted user_id to the wrapped function
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        auth_header = request.headers.get('Authorization')
        
        # Extract token from Authorization header
        if auth_header:
            if auth_header.startswith('Bearer '):
                token = auth_header.split(' ')[1]
            else:
                logging.warning("Malformed Authorization header received")
                return jsonify({
                    'status': 'error',
                    'message': 'Authorization header must start with Bearer'
                }), 401
        
        # Check if token exists
        if not token:
            logging.warning("Request missing Authorization token")
            return jsonify({
                'status': 'error',
                'message': 'Authentication token is missing',
                'details': 'Add the token in the Authorization header as "Bearer <token>"'
            }), 401
        
        # Verify token and extract user_id
        user_id = verify_token(token)
        if not user_id:
            logging.warning(f"Invalid or expired token used in request")
            return jsonify({
                'status': 'error',
                'message': 'Invalid or expired token',
                'details': 'Please login again to obtain a new token'
            }), 401
        
        # Call the wrapped function with the user_id
        try:
            return f(user_id, *args, **kwargs)
        except Exception as e:
            logging.error(f"Error in protected route: {e}")
            return jsonify({
                'status': 'error',
                'message': 'Internal server error',
                'details': str(e)
            }), 500
    
    return decorated