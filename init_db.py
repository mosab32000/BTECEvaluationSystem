from backend.app import create_app
from backend.app.database import db
from backend.app.models import User, Evaluation

app = create_app()

with app.app_context():
    db.create_all()
    print("Database tables created successfully!")

    # Create a test user if none exists
    if not User.query.filter_by(email='test@example.com').first():
        test_user = User(email='test@example.com')
        test_user.set_password('password123')
        db.session.add(test_user)
        db.session.commit()
        print("Test user created successfully!")
    else:
        print("Test user already exists.")