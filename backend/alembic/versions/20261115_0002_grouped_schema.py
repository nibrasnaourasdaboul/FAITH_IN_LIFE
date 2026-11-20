"""Replace the schema with the grouped DBML.

Revision ID: 20261115_0002
Revises: 20261113_0001
Create Date: 2026-11-15
"""

from alembic import op

from app.db.base import Base
from app.models import entities  # noqa: F401

revision = "20261115_0002"
down_revision = "20261113_0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # يمسح الجداول القديمة ويعيد إنشاءها وفق المخطط المجمّع.
    op.execute(
        """
        DO $$ DECLARE row RECORD;
        BEGIN
          FOR row IN
            SELECT tablename FROM pg_tables
            WHERE schemaname = 'public' AND tablename <> 'alembic_version'
          LOOP
            EXECUTE 'DROP TABLE IF EXISTS ' || quote_ident(row.tablename) || ' CASCADE';
          END LOOP;
        END $$;
        """
    )
    Base.metadata.create_all(bind=op.get_bind())


def downgrade() -> None:
    bind = op.get_bind()
    Base.metadata.drop_all(bind=bind)
