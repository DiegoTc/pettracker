#!/usr/bin/env python3
"""
Helper script to run Flask-Migrate for the IMEI migration
This is an alternative to the standalone migration script

Usage:
    python3 run_flask_migration.py
"""
import os
import sys
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate, upgrade

# Create basic Flask app with migration support
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

if not app.config['SQLALCHEMY_DATABASE_URI']:
    print("ERROR: DATABASE_URL environment variable not set")
    sys.exit(1)

db = SQLAlchemy(app)
migrate = Migrate(app, db)

def run_migration():
    """Run the migration using Flask-Migrate"""
    print(f"Using database: {app.config['SQLALCHEMY_DATABASE_URI']}")
    print("Running Flask-Migrate upgrade...")
    with app.app_context():
        # Initialize or upgrade the database
        upgrade()
    print("Migration completed successfully!")

if __name__ == '__main__':
    run_migration()