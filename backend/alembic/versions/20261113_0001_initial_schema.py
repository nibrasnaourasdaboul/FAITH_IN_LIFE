"""Initial schema from the FAITH in LIFE ERD.

Revision ID: 20261113_0001
Revises:
Create Date: 2026-11-13
"""

from alembic import op

from app.db.base import Base
from app.models import entities  # noqa: F401

revision = "20261113_0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    Base.metadata.create_all(bind=bind)


def downgrade() -> None:
    bind = op.get_bind()
    Base.metadata.drop_all(bind=bind)
    op.execute("DROP EXTENSION IF EXISTS vector")
