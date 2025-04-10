# Database Migration Instructions

This document provides instructions for managing database migrations using Flask-Migrate in the Pet Tracker project.

## Setup on a New Environment

To set up the migration system on a new environment, follow these steps:

1. Install the required packages:
   ```bash
   pip install flask-migrate
   ```

2. Initialize the migration repository (if it doesn't exist):
   ```bash
   flask db init
   ```

3. Apply existing migrations:
   ```bash
   flask db upgrade
   ```

## Creating New Migrations

When you make changes to your database models:

1. Generate a migration script:
   ```bash
   flask db migrate -m "Description of your changes"
   ```

2. Review the generated migration script in `migrations/versions/` to ensure it's correct

3. Apply the migration:
   ```bash
   flask db upgrade
   ```

## Troubleshooting

If you encounter errors during migration:

1. **Column doesn't exist**: If a migration tries to drop a column that doesn't exist, edit the migration file to remove that operation.

2. **Table doesn't exist**: Similar to columns, edit the migration file to remove operations on non-existent tables.

3. **Start fresh**: If you're having persistent issues and are still in development:
   ```bash
   # Drop and recreate the database
   # Then initialize migrations
   flask db init
   flask db migrate -m "Initial schema"
   flask db upgrade
   ```

## Alternative Database Setup (without migrations)

If you prefer not to use migrations, you can set up the database with:

```python
python -c "from app import app, db; app.app_context().push(); db.create_all()"
```

To add the role column specifically:

```python
python -c "from app import app, db; app.app_context().push(); db.engine.execute('ALTER TABLE \"user\" ADD COLUMN IF NOT EXISTS role VARCHAR(20) DEFAULT \"user\" NOT NULL;')"
```

## Production Considerations

For production environments:

1. Always backup your database before applying migrations
2. Test migrations in a staging environment first
3. Never run `db.drop_all()` in production
4. Consider using database-specific tools for large-scale migrations