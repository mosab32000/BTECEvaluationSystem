#!/usr/bin/env python3
"""
Entrypoint script for running the BTEC Evaluation System server.
"""
import os
import logging
import secrets
import base64
from dotenv import load_dotenv
from backend.wsgi import app
from cryptography.fernet import Fernet

# Setup logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='server.log'
)

# Load environment variables
load_dotenv()

def ensure_secret_key(env_var, length=32):
    """Ensure the environment variable exists, generate a random one if not"""
    if not os.environ.get(env_var):
        random_key = secrets.token_hex(length)
        os.environ[env_var] = random_key
        logging.info(f"Generated random {env_var}")
    else:
        logging.info(f"{env_var} is already configured")

def ensure_encryption_key():
    """Ensure the ENCRYPTION_KEY environment variable exists, generate if not"""
    if not os.environ.get('ENCRYPTION_KEY'):
        key = Fernet.generate_key().decode()
        os.environ['ENCRYPTION_KEY'] = key
        logging.info("Generated random ENCRYPTION_KEY")
    else:
        logging.info("ENCRYPTION_KEY is already configured")

if __name__ == '__main__':
    print("Starting BTEC Evaluation System...")
    
    # Ensure required keys exist
    ensure_secret_key('SECRET_KEY')
    ensure_secret_key('JWT_SECRET_KEY')
    ensure_encryption_key()
    
    # Log database connection information (without credentials)
    db_url = os.environ.get('DATABASE_URL', '')
    if db_url:
        # Split at @ and take the second part to avoid showing credentials
        safe_db_url = 'postgresql://' + db_url.split('@')[1] if '@' in db_url else 'Unknown'
        logging.info(f"Database connection: {safe_db_url}")
    else:
        logging.warning("DATABASE_URL not found in environment")
    
    # Check if OpenAI API key is available
    if os.environ.get('OPENAI_API_KEY'):
        logging.info("OpenAI API key is configured")
    else:
        logging.warning("OpenAI API key is not configured. AI evaluation will be simulated.")
    
    # Check for blockchain configuration 
    if all([os.environ.get(key) for key in ['INFURA_URL', 'CONTRACT_ADDRESS', 'SIGNER_PRIVATE_KEY']]):
        logging.info("Blockchain service is configured")
    else:
        logging.warning("Blockchain service is not fully configured. Blockchain operations will be simulated.")
    
    # Run the application
    app.run(host='0.0.0.0', port=5000, debug=True)