"""
Simple script to check the database connection and tables for the BTEC Evaluation System.
"""

import os
from sqlalchemy import create_engine, inspect

def test_db_connection():
    """Test the database connection"""
    db_url = os.environ.get("DATABASE_URL")
    
    if not db_url:
        print("No DATABASE_URL found in environment variables")
        return False
    
    try:
        engine = create_engine(db_url)
        conn = engine.connect()
        conn.close()
        print("✅ Database connection successful!")
        return engine
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

def list_tables():
    """List all tables in the database"""
    engine = test_db_connection()
    if not engine:
        return
    
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    
    print("\nDatabase Tables:")
    print("----------------")
    
    if not tables:
        print("No tables found in the database.")
    else:
        for table in tables:
            print(f"- {table}")
            columns = inspector.get_columns(table)
            for column in columns:
                print(f"  • {column['name']} ({column['type']})")
            print()

if __name__ == "__main__":
    list_tables()