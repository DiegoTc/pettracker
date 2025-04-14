# IMEI Migration Instructions

## Quick Guide to Run the Migration

We've provided multiple methods to run the database migration to support IMEI as the primary device identifier:

### Method 1: Standalone Migration Script (Recommended)

This is the simplest method that doesn't require Flask-Migrate:

```bash
# Make sure your DATABASE_URL environment variable is set
export DATABASE_URL="postgresql://username:password@localhost:5432/database_name"

# Run the migration script
python3 run_imei_migration.py
```

### Method 2: Using Flask-Migrate Helper

If you prefer to use Flask-Migrate:

```bash
# Install Flask-Migrate if not already installed
pip install flask-migrate

# Make sure your DATABASE_URL environment variable is set
export DATABASE_URL="postgresql://username:password@localhost:5432/database_name"

# Run the Flask migration helper
python3 run_flask_migration.py
```

### Method 3: Manual Database Updates

If you prefer to run the SQL directly:

```sql
-- Step 1: Make device_id nullable
ALTER TABLE device ALTER COLUMN device_id DROP NOT NULL;

-- Step 2: Update NULL IMEI values (replace with your own logic)
UPDATE device 
SET imei = CONCAT('MIGRATED', LPAD(id::text, 10, '0'))
WHERE imei IS NULL;

-- Step 3: Make IMEI NOT NULL
ALTER TABLE device ALTER COLUMN imei SET NOT NULL;

-- Step 4: Create index on IMEI
CREATE INDEX IF NOT EXISTS ix_device_imei ON device (imei);
```

## What to Expect After Migration

1. The `device_id` field will be optional
2. The `imei` field will be required
3. Existing devices without IMEI values will have generated IMEI values
4. Lookups by both internal ID and IMEI will work

## Verifying the Migration

```bash
# Connect to your database
psql $DATABASE_URL

# Check the device table schema
\d device

# Verify all devices have IMEI values
SELECT COUNT(*) FROM device WHERE imei IS NULL;

# View IMEI values that were generated
SELECT id, device_id, imei FROM device WHERE imei LIKE 'MIGRATED%';
```

## Troubleshooting

If you encounter issues:

1. **Error: IMEI value already exists**  
   Some devices might have duplicate IMEI values. Use the standalone script which handles this with random suffixes.

2. **Error: device_id cannot be NULL**  
   The migration script might not have successfully made device_id nullable. Run the ALTER TABLE command manually.

3. **API errors after migration**  
   Make sure all code that creates devices now provides an IMEI value.

For more details about this architectural change, see the full [IMEI Migration Guide](./IMEI_MIGRATION_GUIDE.md).