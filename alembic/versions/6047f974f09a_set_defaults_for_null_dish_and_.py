"""set_defaults_for_null_dish_and_restaurant_columns

Revision ID: 6047f974f09a
Revises: 5369dd5b096a
Create Date: 2026-05-14 17:40:23.076525

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6047f974f09a'
down_revision: Union[str, Sequence[str], None] = '5369dd5b096a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Fix dishes table: set defaults for columns that were added later
    # and have NULL values in existing rows
    op.execute("UPDATE dishes SET price = 0.0 WHERE price IS NULL")
    op.execute("UPDATE dishes SET spicy = false WHERE spicy IS NULL")
    op.execute("UPDATE dishes SET additional_images = '[]' WHERE additional_images IS NULL")
    op.execute("UPDATE dishes SET status = 'draft' WHERE status IS NULL")
    op.execute("UPDATE dishes SET meal_type = '' WHERE meal_type IS NULL")
    op.execute("UPDATE dishes SET dietary_type = '' WHERE dietary_type IS NULL")
    op.execute("UPDATE dishes SET texture = '' WHERE texture IS NULL")

    # Fix restaurants table
    op.execute("UPDATE restaurants SET name = '' WHERE name IS NULL")
    op.execute("UPDATE restaurants SET birth_date = '' WHERE birth_date IS NULL")
    op.execute("UPDATE restaurants SET last_name = '' WHERE last_name IS NULL")


def downgrade() -> None:
    """Downgrade schema."""
    # Data migration downgrade is typically a no-op
    pass
