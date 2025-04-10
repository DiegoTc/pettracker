import os
from app import app, db
from flask_migrate import Migrate, upgrade, stamp

# Initialize Flask-Migrate
migrate = Migrate(app, db)

# Create an application context
with app.app_context():
    print("Stamping the database with head...")
    # Stamp the database with the current head
    stamp('head')
    
    print("Running migrations...")
    # Run the database migrations
    upgrade()
    
    print("Migration complete.")