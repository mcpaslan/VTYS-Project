"""add program_id to user

Revision ID: 51932dfbbaa2
Revises: 5f2e3c6d2cb6
Create Date: 2025-12-10 20:52:00.886129

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "51932dfbbaa2"
down_revision: Union[str, Sequence[str], None] = "5f2e3c6d2cb6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.execute(
        """
        ALTER TABLE users ADD COLUMN current_program_id INT REFERENCES programs(id);
    """
    )


def downgrade():
    op.execute(
        """
        ALTER TABLE users DROP COLUMN current_program_id;
    """
    )
