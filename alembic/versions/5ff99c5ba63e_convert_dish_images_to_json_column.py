"""convert_dish_images_to_json_column

Revision ID: 5ff99c5ba63e
Revises: e5b8c91d2f4a
Create Date: 2026-04-17 00:15:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5ff99c5ba63e'
down_revision: Union[str, Sequence[str], None] = 'e5b8c91d2f4a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Drop old dish_images table
    op.drop_constraint('fk_dish_images_dish_id_dishes', 'dish_images', type_='foreignkey')
    op.drop_index(op.f('ix_dish_images_id'), table_name='dish_images')
    op.drop_table('dish_images')

    # Add additional_images JSON column to dishes
    op.add_column(
        'dishes',
        sa.Column('additional_images', sa.JSON(), nullable=True)
    )


def downgrade() -> None:
    """Downgrade schema."""
    # Remove JSON column
    op.drop_column('dishes', 'additional_images')

    # Recreate dish_images table
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
