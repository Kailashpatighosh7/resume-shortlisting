"""add shortlist_quota to jobs

Revision ID: 001_shortlist_quota
Revises:
Create Date: 2026-06-11
"""

from alembic import op
import sqlalchemy as sa

revision = "001_shortlist_quota"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "jobs",
        sa.Column("shortlist_quota", sa.Integer(), nullable=False, server_default="5"),
    )


def downgrade() -> None:
    op.drop_column("jobs", "shortlist_quota")
