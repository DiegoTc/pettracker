#!/usr/bin/env python3
"""
Standalone migration script to update the database schema to make IMEI the primary device identifier
This script can be run directly without Flask-Migrate

Usage:
    python3 run_imei_migration.py

Requirements:
    - DATABASE_URL environment variable must be set
    - sqlalchemy must be installed
"""
import os
import sys
import random
from sqlalchemy import create_engine, text
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

def run_migration():
    """Run the migration to make IMEI the primary device identifier"""
    # Get database URL from environment
    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        print("ERROR: DATABASE_URL environment variable not set")
        sys.exit(1)

    print(f"Connecting to database: {database_url}")
    engine = create_engine(database_url)

    try:
        with engine.begin() as conn:
            print("Starting migration to make IMEI the primary device identifier...")
            
            # Step 1: Check if IMEI column exists
            result = conn.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name = 'device' AND column_name = 'imei'"))
            if result.rowcount == 0:
                print("ERROR: IMEI column doesn't exist in device table")
                sys.exit(1)
            
            # Step 2: Make device_id nullable
            print("Making device_id column nullable...")
            conn.execute(text("ALTER TABLE device ALTER COLUMN device_id DROP NOT NULL"))
            
            # Step 3: Find devices with NULL IMEI values
            result = conn.execute(text("SELECT id, device_id FROM device WHERE imei IS NULL"))
            devices_without_imei = result.fetchall()
            
            if devices_without_imei:
                print(f"Found {len(devices_without_imei)} devices without IMEI values")
                
                # Step 4: Update those devices with a generated IMEI
                for device_id, original_device_id in devices_without_imei:
                    try:
                        # Generate a pseudo-IMEI from device_id if available, or using the DB id
                        pseudo_imei = f"MIGRATED{device_id:010d}"
                        conn.execute(
                            text("UPDATE device SET imei = :imei WHERE id = :id"),
                            {"imei": pseudo_imei, "id": device_id}
                        )
                        print(f"  - Updated device ID {device_id} with IMEI: {pseudo_imei}")
                    except IntegrityError:
                        # In case of duplicate IMEI, append a random suffix
                        random_suffix = random.randrange(100, 999)
                        pseudo_imei = f"MIGRATED{device_id:07d}{random_suffix}"
                        conn.execute(
                            text("UPDATE device SET imei = :imei WHERE id = :id"),
                            {"imei": pseudo_imei, "id": device_id}
                        )
                        print(f"  - Updated device ID {device_id} with IMEI (with random suffix): {pseudo_imei}")
            else:
                print("No devices without IMEI values found.")
            
            # Step 5: Make IMEI NOT NULL
            print("Making IMEI column NOT NULL...")
            conn.execute(text("ALTER TABLE device ALTER COLUMN imei SET NOT NULL"))
            
            # Step 6: Create index on IMEI if not exists
            print("Creating index on IMEI column...")
            conn.execute(text("CREATE INDEX IF NOT EXISTS ix_device_imei ON device (imei)"))
            
            print("Migration completed successfully!")
            
    except SQLAlchemyError as e:
        print(f"ERROR: Migration failed: {e}")
        sys.exit(1)

def verify_migration():
    """Verify the migration was successful"""
    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        print("ERROR: DATABASE_URL environment variable not set")
        sys.exit(1)
    
    engine = create_engine(database_url)
    
    try:
        with engine.connect() as conn:
            # Check IMEI column is NOT NULL
            result = conn.execute(text("""
                SELECT is_nullable 
                FROM information_schema.columns 
                WHERE table_name = 'device' AND column_name = 'imei'
            """))
            is_nullable = result.scalar()
            if is_nullable == 'YES':
                print("WARNING: IMEI column is still nullable")
            else:
                print("✓ IMEI column is correctly set to NOT NULL")
            
            # Check all devices have IMEI values
            result = conn.execute(text("SELECT COUNT(*) FROM device WHERE imei IS NULL"))
            null_count = result.scalar()
            if null_count > 0:
                print(f"WARNING: Found {null_count} devices with NULL IMEI values")
            else:
                print("✓ All devices have IMEI values")
            
            # Check if index exists
            result = conn.execute(text("""
                SELECT indexname FROM pg_indexes 
                WHERE tablename = 'device' AND indexname = 'ix_device_imei'
            """))
            if result.rowcount == 0:
                print("WARNING: Index on IMEI column is missing")
            else:
                print("✓ Index on IMEI column exists")
                
    except SQLAlchemyError as e:
        print(f"ERROR: Verification failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    run_migration()
    print("\nVerifying migration...")
    verify_migration()
    
    print("\nMigration completed and verified.")
    print("\nNext steps:")
    print("1. Verify your application works with the updated schema")
    print("2. Update any code that expects device_id to be mandatory")
    print("3. Make sure all device creation code provides IMEI values")