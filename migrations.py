from flask.cli import FlaskGroup
from app import app, db
from flask_migrate import Migrate, current

cli = FlaskGroup(app)

if __name__ == '__main__':
    cli()