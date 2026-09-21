"""Add hints, company_tags, required_concept, difficulty_tier to exercises

Revision ID: a1b2c3d4e5f6
Revises: d2a68bcfae02
Create Date: 2026-09-21 15:28:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, None] = 'd2a68bcfae02'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add Socratic hints (JSON array of 5 progressive hints)
    op.add_column('exercises', sa.Column('hints_json', sa.Text(), nullable=True))
    # Add company tags (e.g. "Google · Amazon · Meta")
    op.add_column('exercises', sa.Column('company_tags', sa.String(length=255), nullable=True))
    # Add required concept label (e.g. "Hash Map + complement")
    op.add_column('exercises', sa.Column('required_concept', sa.String(length=255), nullable=True))
    # Add difficulty tier (Basic | Intermediate | Advanced)
    op.add_column('exercises', sa.Column('difficulty_tier', sa.String(length=50), nullable=True))


def downgrade() -> None:
    op.drop_column('exercises', 'difficulty_tier')
    op.drop_column('exercises', 'required_concept')
    op.drop_column('exercises', 'company_tags')
    op.drop_column('exercises', 'hints_json')
