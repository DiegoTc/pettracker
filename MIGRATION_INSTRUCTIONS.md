# Database Migration Instructions

This document provides instructions for properly migrating the database when schema changes are made.

## Understanding the Migration System

The application uses Flask-Migrate (Alembic) to manage database migrations. This ensures that database schema changes are tracked and can be applied consistently across different environments.

## Migration Commands

### Create a Migration

When you make changes to your SQLAlchemy models, generate a new migration:

```bash
flask db migrate -m "description_of_changes"
```

This creates a new migration script in the `migrations/versions/` directory.

### Apply Migrations

To apply all pending migrations:

```bash
flask db upgrade
```

### Downgrade Database

To revert to a previous migration:

```bash
flask db downgrade
```

## Troubleshooting Common Issues

### 1. User role column missing

If you encounter errors about the User.role column missing, ensure you:

1. Check that the User model has the role field properly defined:
   ```python
   role = db.Column(db.String(20), default='user', nullable=False)
   ```

2. Check if the column exists in the database:
   ```sql
   SELECT column_name, data_type, column_default 
   FROM information_schema.columns 
   WHERE table_name = 'user' AND column_name = 'role';
   ```

3. If the column doesn't exist or has incorrect properties, run:
   ```bash
   flask db stamp head  # Mark current state as latest
   flask db migrate -m "add_user_role_column"  # Create migration for changes
   flask db upgrade  # Apply the migration
   ```

### 2. Table doesn't reflect model changes

When your models change but the database doesn't reflect those changes:

1. Make sure all models have `__table_args__ = {'extend_existing': True}` to handle schema reflection correctly
2. Run a fresh migration:
   ```bash
   flask db stamp head
   flask db migrate
   flask db upgrade
   ```

### 3. SQLAlchemy Metadata Reflection Issues

If SQLAlchemy is not correctly reflecting the database schema:

1. Ensure the app context is properly set up before reflecting:
   ```python
   with app.app_context():
       Base.metadata.reflect(db.engine)
   ```

2. Clear SQLAlchemy's metadata cache before reflecting:
   ```python
   Base.metadata.clear()
   Base.metadata.reflect(db.engine)
   ```

## Best Practices

1. Always back up your database before running migrations
2. Review migration scripts before applying them
3. Test migrations in development before deploying to production
4. Keep migration scripts under version control
5. For model changes, consider data migrations in addition to schema migrations
6. When adding a column with a default value, consider adding it as nullable first, then fill existing rows, then set it to non-nullable

## Recent Migration History

The most recent migration added or confirmed that the User model has a role column with these properties:
- Data type: VARCHAR(20)
- Default value: 'user'
- Constraint: NOT NULL
