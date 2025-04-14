# IMEI Migration Guide for PetTracker

This guide explains the architectural change to use IMEI as the primary device identifier in the PetTracker application.

## Overview

We're transitioning from using `device_id` as the primary identifier for devices to using the industry-standard `IMEI` (International Mobile Equipment Identity) number.

This change will:
- Make the system more compatible with physical GPS tracking hardware
- Provide a standard way to identify devices across the platform
- Simplify device registration and lookup processes

## Changes Made

1. **Database Model**: Updated the Device model to make IMEI required and device_id optional
2. **Validation**: Added IMEI formatting and validation in both backend and frontend
3. **Frontend Forms**: Redesigned device forms to prioritize IMEI and make device_id an advanced option
4. **API Endpoints**: Updated to support lookup by both internal ID and IMEI for backward compatibility

## Running the Migration

There are two ways to run the migration:

### Option 1: Using Flask-Migrate (if configured)

If Flask-Migrate is set up in your environment:

```bash
# Set up environment variables (if not already done)
export DATABASE_URL="postgresql://username:password@localhost:5432/database_name"

# Run migration
flask db upgrade
```

### Option 2: Using the Standalone Migration Script

For environments without Flask-Migrate:

```bash
# Set up environment variables
export DATABASE_URL="postgresql://username:password@localhost:5432/database_name"

# Run the standalone migration script
python3 run_imei_migration.py
```

## Migration Process

The migration will:

1. Make the `device_id` field nullable (optional)
2. Identify any devices with NULL IMEI values
3. Generate placeholder IMEI values for those devices
4. Make the IMEI field NOT NULL (required)
5. Create an index on the IMEI column for faster lookups

## Verification

After migration, verify that:

1. The IMEI column is set to NOT NULL
2. All devices have a valid IMEI value
3. The application can look up devices by IMEI

You can check the database schema with:

```bash
psql $DATABASE_URL -c "\d device"
```

## Potential Issues

### Duplicate IMEI Values

If you encounter unique constraint violations, you may need to clean up duplicate IMEI values:

```sql
-- Find duplicates
SELECT imei, COUNT(*) FROM device GROUP BY imei HAVING COUNT(*) > 1;

-- Update specific devices
UPDATE device SET imei = 'NEW_UNIQUE_IMEI' WHERE id = specific_device_id;
```

### API Backward Compatibility

The API has been updated to support both:

- Integer ID lookups: `/api/devices/123`
- IMEI lookups: `/api/devices/by-imei/123456789012345`

This ensures existing integrations continue to work.

## For New Development

When creating new devices:

1. Always require IMEI as the primary identifier
2. Generate a device_id only if needed for legacy support
3. Use the IMEI for device lookup where possible

## Questions or Issues?

If you encounter any issues during migration or have questions, please contact the development team.