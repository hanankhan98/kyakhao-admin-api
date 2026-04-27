"""add_logo_and_banner_to_restaurants

Revision ID: a13a02c66d3a
Revises: 
Create Date: 2026-04-15 19:02:33.617527

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a13a02c66d3a'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('restaurants', sa.Column('logo', sa.String(), nullable=True))
    op.add_column('restaurants', sa.Column('banner', sa.String(), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('restaurants', 'banner')
    op.drop_column('restaurants', 'logo')
