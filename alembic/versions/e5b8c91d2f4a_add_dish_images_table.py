"""add_dish_images_table

Revision ID: e5b8c91d2f4a
Revises: a13a02c66d3a
Create Date: 2026-04-16 17:40:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e5b8c91d2f4a'
down_revision: Union[str, Sequence[str], None] = 'a13a02c66d3a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Agar table pehle se exist karti hai (SQLAlchemy auto-create ki wajah se) toh drop kar do
    op.execute("DROP TABLE IF EXISTS dish_images CASCADE")

    op.create_table(
        'dish_images',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('image_url', sa.String(length=500), nullable=False),
        sa.Column('dish_id', sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_dish_images_id'), 'dish_images', ['id'], unique=False)
    op.create_foreign_key(
        'fk_dish_images_dish_id_dishes',
        'dish_images',
        'dishes',
        ['dish_id'],
        ['id'],
        ondelete='CASCADE'
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint('fk_dish_images_dish_id_dishes', 'dish_images', type_='foreignkey')
    op.drop_index(op.f('ix_dish_images_id'), table_name='dish_images')
    op.drop_table('dish_images')
