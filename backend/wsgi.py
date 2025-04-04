
import sys
import os
import secrets
from dotenv import load_dotenv
from cryptography.fernet import Fernet

# Add the project root directory to Python's path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def ensure_encryption_key():
    """Ensure the ENCRYPTION_KEY environment variable exists, generate if not"""
    env_var = "ENCRYPTION_KEY"
    
    # If the encryption key doesn't exist, generate a new one
    if not os.environ.get(env_var):
        # Generate a key for Fernet encryption (URL-safe base64-encoded 32-byte key)
        key = Fernet.generate_key().decode('utf-8')
        
        # Set the environment variable
        os.environ[env_var] = key
        
        # Optionally, save it to the .env file for persistence
        env_file = '.env'
        with open(env_file, 'a+') as file:
            file.seek(0)  # Go to beginning of file
            content = file.read()
            if f"{env_var}=" not in content:
                file.write(f"\n{env_var}={key}")
                print(f"Generated and saved new {env_var} to .env file")
            else:
                print(f"{env_var} already exists in .env file")
    else:
        print(f"{env_var} already exists in environment")

def ensure_secret_key(env_var, length=32):
    """Ensure the environment variable exists, generate a random one if not"""
    if not os.environ.get(env_var):
        # Generate a random key
        key = secrets.token_hex(length)
        # Set the environment variable
        os.environ[env_var] = key
        
        # Save it to the .env file for persistence
        env_file = '.env'
        with open(env_file, 'a+') as file:
            file.seek(0)  # Go to beginning of file
            content = file.read()
            if f"{env_var}=" not in content:
                file.write(f"\n{env_var}={key}")
                print(f"Generated and saved new {env_var} to .env file")
            else:
                print(f"{env_var} already exists in .env file")
    else:
        print(f"{env_var} already exists in environment")

# Load environment variables
load_dotenv()

# Ensure secret and encryption keys exist
ensure_secret_key("SECRET_KEY")
ensure_secret_key("JWT_SECRET_KEY")
ensure_encryption_key()

from backend.app import create_app

app = create_app()

if __name__ == '__main__':
    # Get port from environment or default to 3000
    port = int(os.environ.get('PORT', 3000))
    print(f"Starting BTEC Evaluation System on port {port}...")
    app.run(host='0.0.0.0', port=port, debug=True)
