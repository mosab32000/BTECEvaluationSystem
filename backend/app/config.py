import os
from dotenv import load_dotenv

load_dotenv() # Load environment variables from .env file

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'super-secret-jwt-key'
    ENCRYPTION_KEY = os.environ.get('ENCRYPTION_KEY')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # Service Keys
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
    INFURA_URL = os.environ.get('INFURA_URL')
    CONTRACT_ADDRESS = os.environ.get('CONTRACT_ADDRESS')
    SIGNER_PRIVATE_KEY = os.environ.get('SIGNER_PRIVATE_KEY')
    # Allowed origins for CORS
    ALLOWED_ORIGINS = os.environ.get('ALLOWED_ORIGINS', '*').split(' ')


class DevelopmentConfig(Config):
    DEBUG = True
    FLASK_ENV = 'development'

class ProductionConfig(Config):
    DEBUG = False
    FLASK_ENV = 'production'
    # Add production-specific settings like logging, different DB, etc.

# Select configuration based on FLASK_ENV
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}