from app import app, db
from models import User
from flask import current_app

with app.app_context():
    print(f'User columns: {User.__table__.columns.keys()}')
    user = User.query.first()
    if user:
        print(f'User values: {user.email}, role: {user.role}')
    else:
        print('No users found in database')