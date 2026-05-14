"""add_all_missing_dish_and_restaurant_columns

Revision ID: 5369dd5b096a
Revises: d67ab4659eda
Create Date: 2026-05-14 15:12:05.372205

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5369dd5b096a'
down_revision: Union[str, Sequence[str], None] = 'd67ab4659eda'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add all potentially missing columns safely using IF NOT EXISTS
    # Fixes live DB schema mismatch where migrations were stamped but not applied

    # --- dishes table columns ---
    op.execute("ALTER TABLE dishes ADD COLUMN IF NOT EXISTS cuisine VARCHAR(100)")
    op.execute("ALTER TABLE dishes ADD COLUMN IF NOT EXISTS meal_type VARCHAR(100)")
    op.execute("ALTER TABLE dishes ADD COLUMN IF NOT EXISTS meal_time VARCHAR(100)")
    op.execute("ALTER TABLE dishes ADD COLUMN IF NOT EXISTS texture VARCHAR(100)")
    op.execute("ALTER TABLE dishes ADD COLUMN IF NOT EXISTS dietary_type VARCHAR(100)")
    op.execute("ALTER TABLE dishes ADD COLUMN IF NOT EXISTS calories INTEGER")
    op.execute("ALTER TABLE dishes ADD COLUMN IF NOT EXISTS spicy BOOLEAN")

    # --- restaurants table columns ---
    op.execute("ALTER TABLE restaurants ADD COLUMN IF NOT EXISTS last_name VARCHAR")
    op.execute("ALTER TABLE restaurants ADD COLUMN IF NOT EXISTS birth_date VARCHAR")
    op.execute("ALTER TABLE restaurants ADD COLUMN IF NOT EXISTS logo VARCHAR")
    op.execute("ALTER TABLE restaurants ADD COLUMN IF NOT EXISTS banner VARCHAR")
    op.execute("ALTER TABLE restaurants ADD COLUMN IF NOT EXISTS bank_name VARCHAR")
    op.execute("ALTER TABLE restaurants ADD COLUMN IF NOT EXISTS account_holder_name VARCHAR")
    op.execute("ALTER TABLE restaurants ADD COLUMN IF NOT EXISTS account_number VARCHAR")
    op.execute("ALTER TABLE restaurants ADD COLUMN IF NOT EXISTS ifsc_code VARCHAR")


def downgrade() -> None:
    """Downgrade schema."""
    # Remove columns added above (reverse order)
    op.execute("ALTER TABLE restaurants DROP COLUMN IF EXISTS ifsc_code")
    op.execute("ALTER TABLE restaurants DROP COLUMN IF EXISTS account_number")
    op.execute("ALTER TABLE restaurants DROP COLUMN IF EXISTS account_holder_name")
    op.execute("ALTER TABLE restaurants DROP COLUMN IF EXISTS bank_name")
    op.execute("ALTER TABLE restaurants DROP COLUMN IF EXISTS banner")
    op.execute("ALTER TABLE restaurants DROP COLUMN IF EXISTS logo")
    op.execute("ALTER TABLE restaurants DROP COLUMN IF EXISTS birth_date")
    op.execute("ALTER TABLE restaurants DROP COLUMN IF EXISTS last_name")

    op.execute("ALTER TABLE dishes DROP COLUMN IF EXISTS spicy")
    op.execute("ALTER TABLE dishes DROP COLUMN IF EXISTS calories")
    op.execute("ALTER TABLE dishes DROP COLUMN IF EXISTS dietary_type")
    op.execute("ALTER TABLE dishes DROP COLUMN IF EXISTS texture")
    op.execute("ALTER TABLE dishes DROP COLUMN IF EXISTS meal_time")
    op.execute("ALTER TABLE dishes DROP COLUMN IF EXISTS meal_type")
    op.execute("ALTER TABLE dishes DROP COLUMN IF EXISTS cuisine")
