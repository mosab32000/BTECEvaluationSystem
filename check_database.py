#!/usr/bin/env python3
"""
Simple script to check the database connection and tables for the BTEC Evaluation System.
"""
import os
import sys
import logging
from pathlib import Path
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# Setup logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)

# Create a mini-app just for testing DB access
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

def test_db_connection():
    """Test the database connection"""
    try:
        # Try to execute a simple query
        with app.app_context():
            from sqlalchemy import text
            result = db.session.execute(text('SELECT 1')).scalar()
            logging.info(f"Database connection test result: {result}")
            print(f"✅ Successfully connected to database: {os.environ.get('DATABASE_URL')}")
        return True
    except Exception as e:
        logging.error(f"Database connection error: {e}")
        print(f"❌ Failed to connect to database: {e}", file=sys.stderr)
        return False

def list_tables():
    """List all tables in the database"""
    try:
        with app.app_context():
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            tables = inspector.get_table_names()
            if tables:
                print(f"📋 Found {len(tables)} tables in the database:")
                for table in tables:
                    print(f"  - {table}")
                    # List columns in the table
                    columns = inspector.get_columns(table)
                    for column in columns:
                        print(f"    • {column['name']}: {column['type']}")
            else:
                print("📋 No tables found in the database.")
    except Exception as e:
        logging.error(f"Error listing tables: {e}")
        print(f"❌ Failed to list tables: {e}", file=sys.stderr)

if __name__ == '__main__':
    print("🔍 Checking BTEC Evaluation System database...")
    if test_db_connection():
        list_tables()
    else:
        print("❌ Database connection failed. Check your DATABASE_URL environment variable.")
        sys.exit(1)