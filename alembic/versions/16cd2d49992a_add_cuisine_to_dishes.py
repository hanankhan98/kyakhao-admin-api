"""add_cuisine_to_dishes

Revision ID: 16cd2d49992a
Revises: 5ff99c5ba63e
Create Date: 2026-05-07 15:44:27.293040

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '16cd2d49992a'
down_revision: Union[str, Sequence[str], None] = '5ff99c5ba63e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('dishes', sa.Column('cuisine', sa.String(length=100), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('dishes', 'cuisine')
