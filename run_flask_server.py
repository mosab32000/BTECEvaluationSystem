#!/usr/bin/env python3
"""
Simplified server launcher for the BTEC Evaluation System.
This file is used by the Replit workflow to start the server.
"""
import os
import sys
import logging
from pathlib import Path
from backend.wsgi import app

# Setup logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='server.log',
    filemode='a'
)

def ensure_encryption_key():
    """Ensure the ENCRYPTION_KEY environment variable exists, generate if not"""
    if not os.environ.get('ENCRYPTION_KEY'):
        from cryptography.fernet import Fernet
        key = Fernet.generate_key().decode()
        logging.info("Generated new encryption key")
        print(f"Generated ENCRYPTION_KEY: {key}")
        os.environ['ENCRYPTION_KEY'] = key

def ensure_secret_key(env_var, length=32):
    """Ensure the environment variable exists, generate a random one if not"""
    if not os.environ.get(env_var):
        import secrets
        key = secrets.token_hex(length)
        logging.info(f"Generated new {env_var}")
        print(f"Generated {env_var}: {key}")
        os.environ[env_var] = key

if __name__ == '__main__':
    # Ensure required keys are available
    ensure_secret_key('SECRET_KEY')
    ensure_secret_key('JWT_SECRET_KEY')
    ensure_encryption_key()
    
    print("Starting BTEC Evaluation System server...")
    try:
        app.run(host='0.0.0.0', port=5000, debug=True)
    except Exception as e:
        logging.error(f"Server failed to start: {e}")
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)