# Test script to check if Flask app loads correctly
import sys
import os

try:
    print("Checking if Flask app loads correctly...")
    
    # Try to import the app
    from backend.wsgi import app
    
    print("✅ Successfully imported Flask app")
    
    # Check if important configurations are loaded
    print("\nChecking configurations:")
    print(f"Debug mode: {app.debug}")
    print(f"Secret key configured: {'Yes' if app.secret_key else 'No'}")
    print(f"Database URI configured: {'Yes' if app.config.get('SQLALCHEMY_DATABASE_URI') else 'No'}")
    
    # Check environment variables
    print("\nChecking critical environment variables:")
    env_vars = [
        'DATABASE_URL', 
        'OPENAI_API_KEY',
        'ENCRYPTION_KEY',
        'SECRET_KEY',
        'JWT_SECRET_KEY'
    ]
    
    for var in env_vars:
        value = os.environ.get(var)
        status = "✅ Set" if value else "❌ Not set"
        print(f"{var}: {status}")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\nTest completed.")