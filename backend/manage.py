import os
from flask.cli import FlaskGroup
from backend.app import create_app, db
from backend.app.models import User, Evaluation
import base64
import logging

logging.basicConfig(level=logging.DEBUG)
app = create_app()
cli = FlaskGroup(app)

@cli.command("create_db")
def create_db():
    db.drop_all()
    db.create_all()
    db.session.commit()
    print("Database tables created")

@cli.command("generate_key")
def generate_key():
    """Generate a Fernet encryption key"""
    key = base64.urlsafe_b64encode(os.urandom(32)).decode()
    print(f"Generated key: {key}")
    print("Add this to your .env file as ENCRYPTION_KEY=<key>")

if __name__ == "__main__":
    cli()
