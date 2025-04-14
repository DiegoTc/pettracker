"""Make IMEI the primary device identifier

Revision ID: imei_as_primary_identifier
Revises: 
Create Date: 2025-04-14 02:35:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError


# revision identifiers, used by Alembic.
revision = 'imei_as_primary_identifier'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # First, make device_id nullable
    op.alter_column('device', 'device_id',
               existing_type=sa.VARCHAR(length=64),
               nullable=True)
    
    # Now add NOT NULL constraint to IMEI column
    # Need to handle existing records that might have NULL IMEI values
    # We'll use a database session to update those first
    bind = op.get_bind()
    session = Session(bind=bind)
    
    # Execute a query to find devices with NULL IMEI values
    result = session.execute(
        """
        SELECT id, device_id FROM device 
        WHERE imei IS NULL
        """
    ).fetchall()
    
    # Update those devices with a generated IMEI based on device_id
    for device_id, original_device_id in result:
        try:
            # Generate a pseudo-IMEI from device_id if available, or use a fallback
            pseudo_imei = f"MIGRATED{device_id:010d}"
            session.execute(
                """
                UPDATE device SET imei = :imei
                WHERE id = :id
                """,
                {"imei": pseudo_imei, "id": device_id}
            )
        except IntegrityError:
            # In case of duplicate IMEI, append a random suffix
            import random
            random_suffix = random.randrange(100, 999)
            pseudo_imei = f"MIGRATED{device_id:07d}{random_suffix}"
            session.execute(
                """
                UPDATE device SET imei = :imei
                WHERE id = :id
                """,
                {"imei": pseudo_imei, "id": device_id}
            )
    
    session.commit()
    
    # Now add the NOT NULL constraint to IMEI
    op.alter_column('device', 'imei',
               existing_type=sa.VARCHAR(length=32),
               nullable=False)
    
    # Add index on IMEI column if not already present
    op.create_index(op.f('ix_device_imei'), 'device', ['imei'], unique=True)


def downgrade():
    # Remove the NOT NULL constraint from IMEI
    op.alter_column('device', 'imei',
               existing_type=sa.VARCHAR(length=32),
               nullable=True)
    
    # Make device_id required again
    op.alter_column('device', 'device_id',
               existing_type=sa.VARCHAR(length=64),
               nullable=False)
    
    # Drop the index on IMEI if we created it
    op.drop_index(op.f('ix_device_imei'), table_name='device')