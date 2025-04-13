# Database Migration Guide

This guide provides instructions for managing database migrations in the Pet Tracker application to prevent schema-related errors.

## The Issue with Missing Columns

If you encounter an error like:
```
Database error: (psycopg2.errors.UndefinedColumn) column user.role does not exist
```

This means there's a mismatch between your database schema and the model definitions in the code.

## Quick Fix for Missing Role Column

To quickly add the missing role column to your database:

1. Run the provided script:
   ```
   python add_role_column.py
   ```

2. This script will check if the 'role' column exists in the user table and add it if missing.

## Using Flask-Migrate for Schema Management

For ongoing schema management, use Flask-Migrate:

1. Initialize migrations (if not already done):
   ```
   flask db init
   ```

2. Create migration for current changes:
   ```
   flask db migrate -m "Add description here"
   ```

3. Apply migrations:
   ```
   flask db upgrade
   ```

4. Check migration status:
   ```
   flask db current
   ```

## Best Practices for Schema Changes

1. **Always use migrations**: Whenever you change a model, create and apply a migration.

2. **Version control migrations**: Keep migration files in your version control system.

3. **Test migrations**: Test migrations both up and down to ensure they work properly.

4. **Include migrations in deployment**: Ensure migrations are applied during deployment.

5. **Monitor schema changes**: Regularly check for unapplied migrations.

## Deployment Recommendations

1. Include automatic migration in your deployment process:
   ```
   python run_migration.py
   ```

2. Add pre-start checks to detect schema issues:
   ```
   python check_schema.py
   ```

## Error Handling

The authentication routes now include enhanced error handling to detect and report schema issues. If a column is missing, it will:

1. Log detailed error information
2. Attempt to fix the schema automatically
3. Return a user-friendly error message
4. Not expose sensitive database details

## When Migration Is Required

Create a new migration when:

1. Adding a new model (table)
2. Adding/removing columns
3. Changing column types
4. Adding/modifying indexes
5. Adding/modifying constraints