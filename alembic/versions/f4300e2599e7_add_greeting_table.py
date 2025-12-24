"""Add greeting table

Revision ID: f4300e2599e7
Revises:
Create Date: 2025-11-03 19:36:48.234843

"""

from collections.abc import Sequence

import sqlalchemy as sa
import sqlalchemy.dialects.postgresql as postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "f4300e2599e7"
down_revision: str | Sequence[str] | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "greeting",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
            primary_key=True,
        ),
        sa.Column("sender", sa.String(50), nullable=False),
        sa.Column("recipient", sa.String(50), nullable=False),
        sa.Column("message", sa.String(280), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    """Upgrade schema."""
    pass


def downgrade() -> None:
    op.drop_table("greeting")
    """Downgrade schema."""
    pass
