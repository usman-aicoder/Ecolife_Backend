"""Create onboarding tables (lifestyle and health data)

Revision ID: 002
Revises: 001
Create Date: 2025-10-30

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '002'
down_revision: Union[str, None] = '001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create lifestyle_data and health_data tables."""

    # Create lifestyle_data table
    op.create_table(
        'lifestyle_data',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('transportation_mode', sa.String(length=50), nullable=True),
        sa.Column('diet_type', sa.String(length=50), nullable=True),
        sa.Column('shopping_pattern', sa.String(length=50), nullable=True),
        sa.Column('recycling_habits', sa.String(length=50), nullable=True),
        sa.Column('reusable_items', sa.Boolean(), nullable=True),
        sa.Column('energy_source', sa.String(length=50), nullable=True),
        sa.Column('travel_frequency', sa.String(length=50), nullable=True),
        sa.Column('paper_preference', sa.String(length=50), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id')
    )
    op.create_index(op.f('ix_lifestyle_data_id'), 'lifestyle_data', ['id'], unique=False)

    # Create health_data table
    op.create_table(
        'health_data',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('age', sa.Integer(), nullable=True),
        sa.Column('height', sa.Float(), nullable=True),
        sa.Column('weight', sa.Float(), nullable=True),
        sa.Column('activity_level', sa.String(length=50), nullable=True),
        sa.Column('wellness_goal', sa.String(length=100), nullable=True),
        sa.Column('dietary_preference', sa.String(length=50), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id')
    )
    op.create_index(op.f('ix_health_data_id'), 'health_data', ['id'], unique=False)


def downgrade() -> None:
    """Drop lifestyle_data and health_data tables."""
    op.drop_index(op.f('ix_health_data_id'), table_name='health_data')
    op.drop_table('health_data')
    op.drop_index(op.f('ix_lifestyle_data_id'), table_name='lifestyle_data')
    op.drop_table('lifestyle_data')
