"""
WSGI entry point for the BTEC Evaluation System
"""
import os
import sys
import logging
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Helper function to check and set environment variables
def ensure_env_var(name, default=None, required=False):
    """
    Check if environment variable exists and set a default if it doesn't
    """
    value = os.environ.get(name)
    if not value:
        if required:
            logger.error(f"Required environment variable {name} is not set")
            sys.exit(1)
        elif default:
            os.environ[name] = default
            logger.info(f"{name} set to default value")
        else:
            logger.warning(f"{name} is not set")
    else:
        logger.debug(f"{name} already exists in environment")
    return value

# Set required environment variables with defaults
ensure_env_var('SECRET_KEY', 'dev-secret-key')
ensure_env_var('JWT_SECRET_KEY', 'dev-jwt-secret')
ensure_env_var('ENCRYPTION_KEY', 'dev-encryption-key-32bytes1234567')
ensure_env_var('DATABASE_URL', 'sqlite:///./data/btec_eval.db')

# Import and create app after setting environment variables
from backend.app import create_app

app = create_app()

if __name__ == '__main__':
    host = os.environ.get('HOST', '0.0.0.0')
    port = int(os.environ.get('PORT', 5000))
    app.run(host=host, port=port, debug=True)