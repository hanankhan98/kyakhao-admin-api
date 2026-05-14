"""add_missing_name_and_price_columns

Revision ID: d67ab4659eda
Revises: e5e3326f5f1e
Create Date: 2026-05-14 13:20:34.006040

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd67ab4659eda'
down_revision: Union[str, Sequence[str], None] = 'e5e3326f5f1e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add missing columns safely using IF NOT EXISTS
    # This works on both local (already has columns) and live (missing columns)
    op.execute("ALTER TABLE restaurants ADD COLUMN IF NOT EXISTS name VARCHAR")
    op.execute("ALTER TABLE dishes ADD COLUMN IF NOT EXISTS price DOUBLE PRECISION")


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('dishes', 'price')
    op.drop_column('restaurants', 'name')
